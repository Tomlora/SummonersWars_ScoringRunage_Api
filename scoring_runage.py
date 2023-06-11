import pandas as pd
from params.coef import coef_set, coef_set_spd
import streamlit as st
from st_pages import Page, Section, show_pages, add_indentation
from streamlit_extras.switch_page_button import switch_page


# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'

# set ++ importance



@st.cache_data
def chargement_params():
    category_selected = ['Violent', 'Will', 'Destroy', 'Despair']
    category_value = ", ".join(category_selected)


    category_selected_spd = ['Violent', 'Will', 'Destroy', 'Despair', 'Swift']
    category_value_spd = ", ".join(category_selected_spd)
    
    return category_selected,category_selected_spd, coef_set, coef_set_spd

st.session_state.category_selected, st.session_state.category_selected_spd, st.session_state.coef_set, st.session_state.coef_set_spd = chargement_params()

add_indentation()
show_pages([
                    Page('pages_streamlit/upload.py', 'Upload JSON', icon=':file_folder:'),
                    Section(name='Scoring', icon=':bar_chart:'),
                    Page('pages_streamlit/general.py', 'General', ':books:'),
                    Page('pages_streamlit/palier.py', 'Evolution', ':chart_with_upwards_trend:'),
                    Page('pages_streamlit/timelapse.py', 'Timelapse', ':bookmark_tabs:'), 
                    Section(name='Classement', icon=':trophy:'),
                    Page('pages_streamlit/ladder.py', 'Scoring', icon='🥇'),
                    Page('pages_streamlit/ladder_value.py', 'Rune', icon=':trophy:'),
                    Page('pages_streamlit/ladder_arte.py', 'Artefact', icon=':trophy:'), 
                    Page('pages_streamlit/ladder_others.py', 'Ladder PvP | WB', icon=':trophy:'),
                    Section(name='Runages', icon=':crossed_swords:'),
                    Page('pages_streamlit/grind_runes.py', 'Optimisation', icon=':mag:'),
                    Page('pages_streamlit/build.py', 'Créer un build', icon=':clipboard:'),
                    Page('pages_streamlit/calculator.py', 'Calculateur efficience', icon=':1234:'),
                    Page('pages_streamlit/stats_runes.py', 'Statistiques', icon=':bar_chart:'),
                    Section(name='Artefacts', icon=':gem:'),
                    Page('pages_streamlit/inventaire_artefact.py', 'Inventaire', icon=':open_file_folder:'),
                    Page('pages_streamlit/stats_artefact.py', 'Statistiques', icon=':bar_chart:'),
                    Page('pages_streamlit/dmg_add.py', 'Calculateur dmg', icon=':1234:'),
                    Page('pages_streamlit/use_arte.py', 'Where2Use', icon=':brain:'),
                    Section(name='Paramètres', icon=':gear:'),
                    Page('pages_streamlit/visibility.py', 'Ma visibilité', icon=':eyes:'),
                    Page('pages_streamlit/options.py', 'Mes données', icon=':iphone:'),
                    Section(name='Mise à jour', icon=':loudspeaker:'),
                    Page('pages_streamlit/update.py', 'Version 10/06/23', icon=':speaker:')

                    # Section(name='Administration', icon=':star:'),
                    # Page('pages_streamlit/visualisation_joueur.py', 'Visualisation', icon=':mag:'),
                    # Page('pages_streamlit/box.py', 'Box guilde', icon=':briefcase:' )
                    ])


# si submitted n'est pas initialisé, c'est que le joueur vient d'arriver et n'a pas upload de json. C'est donc false.
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
    
switch_page('Upload JSON')    



