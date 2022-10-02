import pandas as pd
import numpy as np
import streamlit as st

from gestion_bdd import lire_bdd, supprimer_data

def params():
    
    df_actuel = lire_bdd('sw_score')
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)

    
    df_actuel = df_actuel[df_actuel['Joueur'] == st.session_state['pseudo']]
    df_actuel.drop(['Joueur'], axis=1, inplace=True)
    
    df_actuel['datetime'] = pd.to_datetime(df_actuel['date'], format='%d/%m/%Y')
    df_actuel.sort_values(by=['datetime'], inplace=True)
    
    liste_date = df_actuel['date'].unique().tolist()
    
    with st.form('Supprimer des données'):
        st.subheader('Supprimer un enregistrement (Validation définitive !)')
        date_retenu = st.selectbox('Date', liste_date)
        validation_suppression = st.form_submit_button('Valider la suppression')
        
    if validation_suppression:
       supprimer_data(st.session_state['pseudo'], date_retenu)
       st.text('Supprimé')