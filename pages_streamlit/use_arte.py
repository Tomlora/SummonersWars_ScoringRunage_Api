import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.no_default_selectbox import selectbox
from fonctions.visualisation import filter_dataframe
from fonctions.gestion_bdd import lire_bdd

from fonctions.visuel import css


css()




st.title(st.session_state.langue['where_to_use'])
st.info(st.session_state.langue['where_to_use_description'], icon="ℹ️")

add_vertical_space(1)

@st.cache_data(show_spinner=st.session_state.langue['loading_data'])
def charger_data_artefact():
    df = lire_bdd('sw_where2use', index='index').T
    
    swarfarm = lire_bdd('sw_ref_monsters').T
    
    swarfarm['url'] = swarfarm.apply(
                        lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
    
    df = df.merge(swarfarm[['name', 'url', 'natural_stars']], how='left', left_on='Awakened', right_on='name').drop_duplicates(subset=['Awakened'])
    
    df['Stats préférées'] = df['Preferred stats'].str.replace('Any', 'Toutes') 
    df[['Element', 'Attribute', 'Preferred stats']] = df[['Element', 'Attribute', 'Preferred stats']].astype('category')

    return df

import json
@st.cache_data
def translation(langue):
    if langue == 'Français':
        return json.load(open('langue/fr.json', encoding='utf-8'))
    elif langue == 'English':
        return json.load(open('langue/en.json', encoding='utf-8'))
    

    
try:
    if not 'langue' in st.session_state:
        st.session_state.langue = translation("Français") 
except:
    pass  



dict_priority = {'Faible': 1, 'Moyen': 2, 'Elevé': 3}
def choose_stats(stats, key):
    stats = selectbox(st.session_state.langue['select_stat'], stats, key=f"{key}", no_selection_label='Aucun')
    priority = st.selectbox(st.session_state.langue['select_priority'], ['Faible', 'Moyen', 'Elevé'], key=f"{key}2")
    priority = dict_priority[priority]
    
    return stats, priority
    

df_where_to_use = charger_data_artefact()

tab1, tab2 = st.tabs([st.session_state.langue['search_artefact'], st.session_state.langue['search_monster']])

stats = df_where_to_use.columns.drop(['Family', 'Element', 'Awakened', 'Attribute', 'Preferred stats', 'Include', 'name', 'url', 'natural_stars'])

with tab1:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stat1, priority1 = choose_stats(stats, 'stats1')
    with col2:
        stat2, priority2 = choose_stats(stats, 'stats2')

    add_vertical_space(1)    

    # col3, col4 = st.columns(2)
    with col3:
        stat3, priority3 = choose_stats(stats, 'stats3')
    with col4:
        stat4, priority4 = choose_stats(stats, 'stats4')

    df_final = df_where_to_use.copy()
    for stat, priority in zip([stat1, stat2, stat3, stat4], [priority1, priority2, priority3, priority4]):
        if stat != None:
            df_final = df_final[df_final[stat] >= priority]

    if stat1 == None and stat2 == None and stat3 == None and stat4 == None:
        st.warning(st.session_state.langue['fill_first_value'])
    else:
        # Modif DF
        df_final = df_final[['Awakened', 'Attribute', 'Element', 'Family', 'Preferred stats', 'url', 'natural_stars']]  
        
        df_final.columns = ['Monstre', 'Attribut', 'Element', 'Famille', 'Stats préférées', 'url', 'Etoiles']
        
         
        
        # Filtre dispo    
        index_filter = filter_dataframe(
                df_final.drop(['url', 'Etoiles'], axis=1), 'data_build', type_number='int').index
        
        data_filter = df_final.loc[index_filter].dropna(subset='url').sort_values(by=['Etoiles', 'Famille'], ascending=[False, False])
        
        
        st.image(data_filter['url'].tolist(), width=50, caption=data_filter['Monstre'].tolist()) 
        
with tab2:
      
    monster = st.multiselect('Monstre', df_where_to_use['Awakened'].unique(), key='monster')
    
    df_monster = df_where_to_use[df_where_to_use['Awakened'].isin(monster)]\
        .drop(['Family', 'Element', 'Attribute', 'Preferred stats', 'Include', 'name', 'url', 'natural_stars'], axis=1)\
        .set_index('Awakened')
        
    df_monster.replace({0: '/', 1: 'Faible', 2: 'Moyen', 3 : 'Elevé' }, inplace=True)
    
    st.dataframe(df_monster, use_container_width=True)
    
    


st.caption('Made by Tomlora :sunglasses:')