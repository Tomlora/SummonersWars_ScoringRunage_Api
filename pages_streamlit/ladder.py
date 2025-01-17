from fonctions.gestion_bdd import lire_bdd_perso, cleaning_only_guilde
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from params.coef import coef_set, coef_set_spd
from datetime import timedelta
from streamlit_extras.button_selector import button_selector



from fonctions.visuel import css
css()



dict_type = {st.session_state.langue['Score_Rune'] : 'score_general',
                 st.session_state.langue['Score_Speed'] : 'score_spd',
                 f'{st.session_state.langue["Score_Rune"]} (Set)' : 'score sur un set',
                 f'{st.session_state.langue["Score_Speed"]} (Set)' : 'score spd sur un set',
                 st.session_state.langue['Score_Arte'] : 'score_arte',
                 st.session_state.langue['Score_Qualite'] : 'score_qual',
                 'Score Rune Com2us' : 'score_com2us',
                 'Score Rune Com2us (Set)' : 'score_com2us_set'}

dict_list = list(dict_type.keys())

    
set_to_show = ['Violent', 'Will', 'Destroy', 'Despair', 'Swift',
                'Blade', 'Endure', 'Energy', 'Fatal', 'Focus', 'Guard', 'Nemesis',
                'Rage', 'Revenge', 'Shield', 'Tolerance', 'Vampire']


def mise_en_forme_classement(df, variable='score', size=36):
    """Met en forme le classement final :  
    
    - Reset l'index
    - Trie du plus grand score au plus petit
    - Applique le paramètre de visibilité
    - Garde les variables à afficher
    - Filtre (optionnel) en fonction de si le filtre guilde est activé ou non
    
    Return le dataframe streamlit"""
    # on restreint à ce qu'on veut afficher

    # on sort_value
    df.reset_index(inplace=True)
    df.sort_values(variable, ascending=False, inplace=True)
    # on anonymise
    
    if not df.empty:
        df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 1 and st.session_state['pseudo'] != x['joueur'] else x['joueur'], axis=1)
        df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 4 and st.session_state['pseudo'] != x['joueur'] and st.session_state['guilde'] != x['guilde'] else x['joueur'], axis=1)
        
        # on filtre pour ceux qui veulent only guilde :
        df = df.apply(cleaning_only_guilde, axis=1)
        df = df[df['private'] == 0]

        df = df[['joueur', variable, 'date', 'guilde']]

        filtre_guilde = st.checkbox(st.session_state.langue['filter_guilde'])

        if filtre_guilde:
            df = df[df['guilde']
                    == st.session_state.guilde]
            
        df.reset_index(inplace=True, drop=True)
        height_dataframe = size * df.shape[0]

        
        st.dataframe(df.rename(columns={'score_general' : 'General',
                                        'score_spd' : 'Speed',
                                        'score_arte' : 'Artefact'}), height=height_dataframe,
                    use_container_width=True)
    
    else:
        st.warning(st.session_state.langue['no_data'])

    return df



def classement():
    # On lit la BDD
    # on récupère la data
    
    st.info(f'**Note** : {st.session_state.langue["update_ladder"]}', icon="ℹ️")

    if st.session_state.visibility == 0:
        st.warning(st.session_state.langue['no_visibility'], icon="ℹ️")

    @st.cache_data(ttl=timedelta(minutes=10), show_spinner=st.session_state.langue['loading_data'])
    def load_data_ladder():
        data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_score.date, sw_score.score_general, sw_score.score_spd, sw_score.score_arte, sw_score.score_qual, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_score ON sw_user.id = sw_score.id_joueur
                            where sw_user.visibility != 0''').transpose().reset_index()
        return data

    data = load_data_ladder()

    # choice_radio = st.radio(st.session_state.langue['Classement'], options=dict_type.keys(), index=0, horizontal=True)

    choice_radio = button_selector(dict_type.keys())


    
    classement = dict_type[dict_list[choice_radio]]


    if classement == 'score sur un set':
        # set = st.radio('Quel set ?', options=coef_set.keys(), horizontal=True)
        set = st.radio('Set ?', options=st.session_state.set_rune, horizontal=True)

        if set in ['Violent', 'Will', 'Despair', 'Destroy']:
            data_set = lire_bdd_perso(f'''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw.date, sw."Set", sw."100", sw."110", sw."120", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw ON sw_user.id = sw.id
                            where sw_user.visibility != 0
                            and sw."Set" = '{set}';''').transpose().reset_index()
        
        else:
            data_set = lire_bdd_perso(f'''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_detail.date, sw_detail."rune_set", sw_detail."100", sw_detail."110", sw_detail."120", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_detail ON sw_user.id = sw_detail.id
                            where sw_user.visibility != 0
                            and sw_detail."rune_set" = '{set}';''').transpose().reset_index()
            

        
        data_set['date'] = pd.to_datetime(data_set['date'], format="%d/%m/%Y")

        data_set_grp = data_set.groupby(['joueur', 'guilde']).agg(
            {'100': 'max', '110': 'max', '120': 'max', 'date': 'max', 'visibility': 'max'})

        data_set_grp['date'] = data_set_grp['date'].dt.strftime('%d/%m/%Y')

        # calcul points
        data_set_grp['score'] = (data_set_grp['100'] * 1 + data_set_grp['110']
                                 * 2 + data_set_grp['120'] * 3) * coef_set.get(set,1)

        # on restreint à ce qu'on veut afficher

        mise_en_forme_classement(data_set_grp)

    elif classement == 'score spd sur un set':
        set_spd = st.radio(
            'Set ?', options=coef_set_spd.keys(), horizontal=True)

        data_spd = lire_bdd_perso(f'''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_spd.date, sw_spd."Set", sw_spd."23-25", sw_spd."26-28", sw_spd."29-31", sw_spd."32-35", sw_spd."36+", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_spd ON sw_user.id = sw_spd.id
                            where sw_user.visibility != 0
                            and sw_spd."Set" = '{set_spd}';''').transpose().reset_index()

        data_spd['date'] = pd.to_datetime(data_spd['date'], format="%d/%m/%Y")

        data_spd_grp = data_spd.groupby(['joueur', 'guilde']).agg(
            {'23-25': 'max', '26-28': 'max', '29-31': 'max', '32-35': 'max', '36+': 'max', 'date': 'max', 'visibility': 'max'})

        data_spd_grp['date'] = data_spd_grp['date'].dt.strftime('%d/%m/%Y')

        data_spd_grp['score'] = (data_spd_grp['23-25'] * 1 + data_spd_grp['26-28'] * 2 +
                                 data_spd_grp['29-31'] * 3 + data_spd_grp['32-35'] *
                                 4 + data_spd_grp['36+'] * 5) * coef_set_spd.get(set_spd,1)
        
       
        mise_en_forme_classement(data_spd_grp)

    elif classement == 'score_com2us':
        
        data_set = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, MAX(sw_scoring_com2us.date) as "date", MAX(sw_scoring_com2us."mean_SCORE") as "moyenne", MAX(sw_scoring_com2us."max_SCORE") as "max", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_scoring_com2us ON sw_user.id = sw_scoring_com2us.id
                            where sw_user.visibility != 0
                            Group by sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, guilde  ''').transpose().reset_index()
        
        option = st.radio('Option :', options=['max', 'moyenne'], index=0, horizontal=True)
        
        mise_en_forme_classement(data_set, option, size=50)
    
    elif classement == 'score_com2us_set':
        set = st.radio('Set ?', options=st.session_state.set_rune, horizontal=True)
        data_set = lire_bdd_perso(f'''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_scoring_com2us.rune_set, MAX(sw_scoring_com2us.date) as "date", MAX(sw_scoring_com2us."mean_SCORE") as "moyenne", MAX(sw_scoring_com2us."max_SCORE") as "max", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_scoring_com2us ON sw_user.id = sw_scoring_com2us.id
                            where sw_user.visibility != 0
                            and sw_scoring_com2us.rune_set = '{set}'
                            Group by sw_user.id, sw_user.joueur, sw_scoring_com2us.rune_set, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, guilde  ''').transpose().reset_index()
        
        option = st.radio('Option :', options=['max', 'moyenne'], index=0, horizontal=True)

        
        mise_en_forme_classement(data_set, option, size=50)

    else:

        # on transpose la date au format date
        data['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y")

        # on groupby : score, dernière date et visibilité
        data_ranking = data.groupby(['joueur', 'guilde']).agg(
            {classement: 'max', 'date': 'max', 'visibility': 'max'})
        # on met en forme la date
        data_ranking['date'] = data_ranking['date'].dt.strftime('%d/%m/%Y')
        
        mise_en_forme_classement(data_ranking, classement)



if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Classement Scoring')
        classement()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')