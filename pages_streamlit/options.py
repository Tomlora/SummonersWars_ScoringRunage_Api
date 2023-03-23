import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.gestion_bdd import lire_bdd, supprimer_data, supprimer_data_all

from st_pages import add_indentation

add_indentation()


def params():
    # On lit la BDD
    df_actuel = lire_bdd('sw_score')
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)


    df_actuel = df_actuel[df_actuel['id_joueur'] == st.session_state['id_joueur']]
    df_actuel.drop(['id_joueur'], axis=1, inplace=True)

    # Datetime
    df_actuel['datetime'] = pd.to_datetime(
        df_actuel['date'], format='%d/%m/%Y')
    df_actuel.sort_values(by=['datetime'], inplace=True)

    # Liste des dates
    liste_date = df_actuel['date'].unique().tolist()

    with st.form('Supprimer des données'):
        st.subheader('Supprimer un enregistrement (Validation définitive !)')
        date_retenu = st.selectbox('Date', liste_date)
        validation_suppression = st.form_submit_button(
            'Valider la suppression')

    if validation_suppression:
        supprimer_data(st.session_state['id_joueur'], date_retenu)
        st.text('Supprimé')

    with st.form('Supprimer toutes mes données'):
        st.subheader('Tout supprimer (Validation définitive !)')
        validation_suppression_definitive = st.form_submit_button(
            'Valider la suppression définitive')

    if validation_suppression_definitive:

        supprimer_data_all(st.session_state['id_joueur'])
        st.text('Supprimé')



if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Options')
        params()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
    
    
st.caption('Made by Tomlora')