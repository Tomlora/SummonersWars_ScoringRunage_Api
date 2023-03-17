
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fonctions.visuel import load_lottieurl
from streamlit_lottie import st_lottie
from params.coef import coef_set
from fonctions.visualisation import filter_dataframe, table_with_images
from streamlit_extras.switch_page_button import switch_page
from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd, sauvegarde_bdd
from fonctions.compare import comparaison, comparaison_graph


from st_pages import add_indentation

add_indentation()



st.title('Scoring SW')





def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame

    ex : st.session_state.tcd_spd.style.apply(highlight_max, color='green', axis=1)
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)
        

def show_img_monsters(data, stars, variable='*'):
    
    data = data[data[variable] == stars]
    
    st.subheader(f'{stars} etoiles ({data.shape[0]} monstres)')
    
    return st.image(data['url'].tolist(), width=70, caption=data['name'].tolist())



new_index = ['Autre', 'Despair', 'Destroy', 'Violent', 'Will', 'Total']

if 'submitted' in st.session_state:
    if st.session_state.submitted:    

   
    # -------------- Scoring du compte
        try:
            tcd_column, score_column = st.columns(2)
                

            with tcd_column:
                    # Stat du joueur
                st.dataframe(st.session_state.tcd[[100, 110, 120]].reindex(new_index))

            with score_column:
                    # Score du joueur
                st.metric('Score Rune', st.session_state['score'])
                st.metric('Date', st.session_state.tcd.iloc[0]['date'])

            size_general, avg_score_general, max_general, size_guilde, avg_score_guilde, max_guilde, df_max, df_guilde = comparaison(
                    st.session_state['guildeid'])

            tab1, tab2, tab3, tab4 = st.tabs(['Autre scorings', 'Detail du scoring', 'Efficience moyenne par set', 'Monstres'])
                
            with tab1:
                with st.expander('Autre scorings'):

                        # ---------------- Scoring arte + speed

                    tcd_column_spd, score_column_arte = st.columns(2)

                    with tcd_column_spd:
                        st.metric('Score Speed', st.session_state['score_spd'])

                    with score_column_arte:
                        st.metric('Score Arte', st.session_state['score_arte'])

                        # ---------------- Df arte + speed

                    tcd_column_df_spd, score_column_df_arte = st.columns(2)
                        #  df.style.highlight_max(axis=0)
                    with tcd_column_df_spd:
                        st.dataframe(st.session_state.tcd_spd.reindex(new_index))

                    with score_column_df_arte:
                        st.dataframe(st.session_state.tcd_arte)
                            
            with tab2:
                with st.expander('Detail du scoring'):
                        
                    column_detail_scoring1, column_detail_scoring2 = st.columns(2)
                        
                    with column_detail_scoring1:
                        st.dataframe(st.session_state.tcd_detail_score)
                        
                    with column_detail_scoring2:
                        txt = 'Une rune 100 vaut 1 point \nUne rune 110 vaut 2 points\nUne Rune 120 vaut 3 points\n\n\nCoefficient : \n'
                            
                        for rune, score in coef_set.items():
                            txt += f'{rune.upper()} : {score} \n'
                            
                        st.text(txt)    
                            
            with tab3:
                with st.expander('Efficience par set'):

        
                    data_grp : pd.DataFrame = st.session_state['data_avg'].groupby('rune_set').agg({'efficiency' : ['mean', 'max', 'median', 'count']})
                    data_grp = data_grp.droplevel(level=0, axis=1)
                    st.dataframe(data_grp.rename(columns={'mean' : 'moyenne',
                                                            'median' : 'mediane',
                                                            'count' : 'Nombre runes'}))

                    fig = go.Figure()
                    fig.add_trace(go.Histogram(y=data_grp['max'], x=data_grp.index, histfunc='avg', name='max'))
                    fig.add_trace(go.Histogram(y=data_grp['mean'], x=data_grp.index, histfunc='avg', name='mean'))
                    fig.update_layout(
                    barmode="overlay",
                    bargap=0.1)
                    st.plotly_chart(fig)
                
            with tab4:
                with st.expander('Liste de monstres'):
                        
                    st.warning(body="Pour des raisons de performance, l'autel de scellement n'est inclus que dans l'onglet spécifié", icon="🚨")
                        
                        # @st.cache_data(show_spinner=False)
                    def chargement_mobs():
                        data_mobs = pd.DataFrame.from_dict(
                                            st.session_state['data_json'], orient="index").transpose()

                        data_mobs = data_mobs['unit_list']
                            
                            # data_mobs = data_mobs[data_mobs['class'] > 3]

                            # On va boucler et retenir ce qui nous intéresse..
                        list_mobs = []


                        for monstre in data_mobs[0]:
                            unit = monstre['unit_id']
                            master_id = monstre['unit_master_id']
                            stars = monstre['class']
                            level = monstre['unit_level']
                            list_mobs.append([unit, master_id, stars, level])

                        # On met ça en dataframe
                        df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre', '*', 'level'])
                            
                        return df_mobs
                        
                    df_mobs = chargement_mobs()

                        # Maintenant, on a besoin d'identifier les id.
                        # Pour cela, on va utiliser l'api de swarfarm
                        
                    @st.cache_data(show_spinner=False)
                    def load_swarfarm():
                        return pd.read_excel('swarfarm.xlsx')

                    st.session_state.swarfarm = load_swarfarm()
                        
                    # on merge
                    df_mobs_complet = pd.merge(df_mobs, st.session_state.swarfarm, left_on='id_monstre', right_on='com2us_id')
                        
                    # on retient ce dont on a besoin
                    df_mobs_name = df_mobs_complet[['name', '*', 'level', 'image_filename', 'element', 'natural_stars', 'awaken_level']]
                        
                    def key_element(x):
                        '''Transforme les valeurs catégoriques en valeurs numériques'''
                        if x == 'Fire':
                            return 0
                        elif x == 'Water':
                            return 1
                        elif x == 'Wind':
                            return 2
                        elif x == 'Light':
                            return 3
                        elif x == 'Dark':
                            return 4
                        else:
                            return x
                            
                    df_mobs_name['element_number'] = df_mobs_name['element'].apply(lambda x : key_element(x))
                        
                    
                    df_mobs_name.sort_values(by=['element_number', 'natural_stars', '*', 'level', 'name'],
                                                ascending=[True, False, False, False, True],
                                                inplace=True)
                        
                        
                    df_mobs_name['url'] = df_mobs_name.apply(lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
                        
                    menu1, menu2, menu3, menu4 = st.tabs(['Box', '2A', 'LD', 'Autel de scellement'])
                        
                    with menu1:
                        tab1, tab2, tab3, tab4, tab5 = st.tabs(['6 etoiles', '5 etoiles', '4 etoiles', '3 etoiles', '2 etoiles'])
                            
                        with tab1:
                            show_img_monsters(df_mobs_name, 6)
                            
                        with tab2:
                            show_img_monsters(df_mobs_name, 5)
                                
                        with tab3:
                            show_img_monsters(df_mobs_name, 4)
                            
                        with tab4:
                            show_img_monsters(df_mobs_name, 3)
                                
                        with tab5:
                            show_img_monsters(df_mobs_name, 2)
                        
                    with menu2:
                        tab1, tab2, tab3, tab4, tab5 = st.tabs(['6 etoiles', '5 etoiles', '4 etoiles', '3 etoiles', '2 etoiles'])
                            
                        df_mobs_2a_only = df_mobs_name[df_mobs_name['awaken_level'] == 2]
                            
                        with tab1:
                            show_img_monsters(df_mobs_2a_only, 6)
                            
                        with tab2:
                            show_img_monsters(df_mobs_2a_only, 5)
                                
                        with tab3:
                            show_img_monsters(df_mobs_2a_only, 4)
                            
                        with tab4:
                            show_img_monsters(df_mobs_2a_only, 3)
                                
                        with tab5:
                            show_img_monsters(df_mobs_2a_only, 2)
                            
                            
                    with menu3:
                        df_mobs_ld_only = df_mobs_name[df_mobs_name['element_number'].isin([3,4])]
                            
                            
                        tab1, tab2, tab3, tab4 = st.tabs(['5 etoiles naturel', '4 etoiles naturel', '3 etoiles naturel', '2 etoiles naturel'])
                            
                        with tab1:
                            show_img_monsters(df_mobs_ld_only, 5, 'natural_stars')
                            
                        with tab2:
                            show_img_monsters(df_mobs_ld_only, 4, 'natural_stars')
                                
                        with tab3:
                            show_img_monsters(df_mobs_ld_only, 3, 'natural_stars')
                            
                        with tab4:
                            show_img_monsters(df_mobs_ld_only, 2, 'natural_stars')
                        
                    with menu4:
                            
                            # autel de scellement
                            
                            # @st.cache_data(show_spinner=False)
                        def chargement_storage():
                            data_storage = pd.DataFrame(st.session_state['data_json']['unit_storage_list'])
                            df_storage_complet = pd.merge(data_storage, st.session_state.swarfarm, left_on='unit_master_id', right_on='com2us_id')
                                
                            df_storage_complet = df_storage_complet[['unit_master_id','name', 'element', 'class', 'quantity', 'image_filename']]
                            
                            df_storage_complet['url'] = df_storage_complet.apply(lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
                            
                            
                            df_storage_complet.rename(columns={'class' : '*', 'quantity' : 'quantité'}, inplace=True)
                            
                                
                            df_storage_complet.sort_values(by='*', ascending=False, inplace=True)
                                
                            return df_storage_complet
                        
                        tab1, tab2 = st.tabs(['Interactif', 'Image'])
                            
                        df_storage_complet = chargement_storage()
                            
                        with tab1:    
                            df_storage_complet_filter = filter_dataframe(
                                    df_storage_complet.drop(['unit_master_id', 'url', 'image_filename'], axis=1), 'data_build', type_number='int', disabled=True)
                            
                                
                            st.dataframe(df_storage_complet_filter)
                            
                        with tab2:
                            df_html = table_with_images(df=df_storage_complet[['url', 'name', 'quantité']], url_columns=("url",))
                            
                            st.markdown(df_html, unsafe_allow_html=True)
                            
                # Stockage monstres
                            
            df_mobs_copy = df_mobs.copy()
                            
            df_mobs_global = df_mobs_copy.groupby(by=['id_monstre']).count()
                            
            df_mobs_global['storage'] = False
                            
            df_mobs_global.reset_index(inplace=True)
            df_mobs_global.rename(columns={'id_unit' : 'quantité'}, inplace=True)
                            
                                            
            df_storage_global = df_storage_complet.copy()
                            
            df_storage_global['storage'] = True
            df_storage_global.rename(columns={'unit_master_id': 'id_monstre'}, inplace=True)
            df_global = pd.concat([df_mobs_global[['id_monstre', 'quantité', 'storage']], df_storage_global[['id_monstre', 'quantité', 'storage']]]).reset_index(drop=True)
                            
            df_global['id'] = st.session_state['id_joueur']
                            
                # on supprime les informations qu'on avait déjà
            requete_perso_bdd('''DELETE FROM sw_monsters WHERE "id" = :id''', dict_params={'id' : st.session_state['id_joueur']})
                # # on insert les nouvelles
        
            sauvegarde_bdd(df_global, 'sw_monsters', 'append', index=False)

                            
                        
                # ---------------- Comparaison

            col1, col2 = st.columns(2)
            with col1:
                st.header('Comparaison (Runes)')
            with col2:
                img = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_yMpiqXia1k.json')
                st_lottie(img, width=60, height=60)
                    

            tab1, tab2 = st.tabs(['General', st.session_state['guilde']])
                # Par rapport à tous les joueurs
            with tab1:

                comparaison1_1, comparaison1_2, comparaison1_3 = st.columns(3)

                with comparaison1_1:
                    st.metric('Joueurs', size_general)

                with comparaison1_2:
                    delta1_2 = int(st.session_state['score']) - avg_score_general
                    st.metric('Moyenne Score', avg_score_general, delta1_2)

                with comparaison1_3:
                    delta1_3 = int(st.session_state['score']) - max_general
                    st.metric('Record score', max_general, delta1_3)

                rank2_1, rank2_2 = st.columns(2)

                with rank2_1:
                    rank_general = int(df_max.loc[st.session_state['pseudo']]['rank'])
                    st.metric('Classement', rank_general)

                    # with rank2_2:
                fig_general = comparaison_graph(df_max, 'General')
                st.plotly_chart(fig_general)

                # Par rapport à sa guilde
            with tab2:

                comparaison2_1, comparaison2_2, comparaison2_3 = st.columns(3)

                with comparaison2_1:
                    st.metric('Joueurs', size_guilde)

                with comparaison2_2:
                    delta2_2 = int(st.session_state['score']) - avg_score_guilde
                    st.metric('Moyenne Score', avg_score_guilde, delta2_2)

                with comparaison2_3:
                    delta2_3 = int(st.session_state['score']) - max_guilde
                    st.metric('Record score', max_guilde, delta2_3)

                rank2_1, rank2_2 = st.columns(2)

                with rank2_1:
                    rank_guilde = int(df_guilde.loc[st.session_state['pseudo']]['rank'])
                    st.metric('Classement', rank_guilde)

                    # with rank2_2:
                fig_guilde = comparaison_graph(df_guilde, st.session_state['guilde'])
                st.plotly_chart(fig_guilde)

        except Exception as e:
            print(e)
            st.subheader('Erreur')
            st.write('Pas de JSON chargé')
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
