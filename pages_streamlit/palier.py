
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from fonctions.visualisation import transformation_stats_visu, plotline_evol_rune_visu, filter_dataframe
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.visuel import load_lottieurl, css
from streamlit_lottie import st_lottie
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation
import pandas as pd



css()
add_indentation()

@st.cache_data
def filter_data(df, selected_options):
    """Filtre la data en fonction des dates sélectionnés

    Parameters
    ----------
    df : DataFrame
        Dataframe avec les scores et dates
    selected_options : List
        Liste de dates à inclure dans le DataFrame

    Returns
    -------
    DataFrame
        DataFrame triée sur les dates sélectionnées
    """
    df_filtered = df[df['date'].isin(selected_options)]
    return df_filtered


def palier_page():
    
    check_detail = st.checkbox('Avoir le détail des sets', key='detail_set')

    if check_detail:
    
        data_detail_global = lire_bdd_perso('''SELECT rune_set as "Set", "100", "110", "120", points, date from sw_detail where id = :id_joueur''',
                                            params={'id_joueur': st.session_state['id_joueur']}, index_col=None).T
        
        select_set = st.multiselect('Selectionner un set', data_detail_global['Set'].unique().tolist(),
                                    default=data_detail_global['Set'].unique().tolist()[0])
        
        data_detail_filter = data_detail_global[data_detail_global['Set'].isin(select_set)]
        
        data_detail_filter['datetime'] = pd.to_datetime(data_detail_filter['date'], format='%d/%m/%Y')
        
        data_detail_filter.sort_values(by=['datetime'], ascending=False, inplace=True)
        
        col1, _, col2 = st.columns([40,5, 60])
        
        with col1:
        
            st.dataframe(data_detail_filter\
                        .drop('datetime', axis=1)\
                        .set_index('date'))
        
        with col2:
            options_date = data_detail_filter['date'].unique().tolist()
            
            # pour que les graph soient dans le bon sens
            data_detail_filter.sort_values('datetime', ascending=True, inplace=True)
            
            data_detail_filter = pd.melt(data_detail_filter, id_vars=['date', 'Set'], value_vars=[
                                '100', '110', '120', 'points'], var_name='Palier', value_name='Nombre')
                    
            if len(options_date) > 30:
                        list_tail = st.slider('Selectionner les derniers reportings:', 5, len(options_date), 30, help="Cette option s'affiche lorsque vous avez plus de 30 reportings différents")
                        options_date = options_date[:list_tail]

            options_select = st.multiselect(
                        'Selectionner les dates à afficher :', options_date, options_date)
            
            data_detail_filter = filter_data(data_detail_filter, options_select)
        

        
        data_100 = data_detail_filter[data_detail_filter['Palier'] == '100']
        data_110 = data_detail_filter[data_detail_filter['Palier'] == '110']
        data_120 = data_detail_filter[data_detail_filter['Palier'] == '120']
        data_points = data_detail_filter[data_detail_filter['Palier'] == 'points']
        
        
        tab1, tab2, tab3, tab4 = st.tabs(
                    ['Points', 'Palier 100', 'Palier 110', 'Palier 120'])
        
        with tab1:
            fig_rune_pts = plotline_evol_rune_visu(data_points)
            fig_rune_pts.update_yaxes(tickmode='linear')
            st.plotly_chart(fig_rune_pts)

        with tab2:
            fig_rune_100 = plotline_evol_rune_visu(data_100)
            fig_rune_100.update_yaxes(tickmode='linear')
            st.plotly_chart(fig_rune_100)

        with tab3:
            fig_rune_110 = plotline_evol_rune_visu(data_110)
            fig_rune_110.update_yaxes(tickmode='linear')
            st.plotly_chart(fig_rune_110)

        with tab4:
            fig_rune_120 = plotline_evol_rune_visu(data_120)
            fig_rune_120.update_yaxes(tickmode='linear')
            st.plotly_chart(fig_rune_120)        

        
    
    
    else:
        try:
            data_detail = transformation_stats_visu(
                'sw', st.session_state['id_joueur'], distinct=True, ascending=False)
            data_scoring = transformation_stats_visu(
                'sw_score', st.session_state['id_joueur'], distinct=True, ascending=False)                
            

            col1, _, col2 = st.columns([40,5, 60])

            with col2:
                img = load_lottieurl(
                    'https://assets10.lottiefiles.com/packages/lf20_sfiiilbf.json')
                st_lottie(img, width=40, height=40)
                
                
                
                # if check_detail:
                    
                options_date = data_scoring['date'].unique().tolist()
                
                if len(options_date) > 30:
                    list_tail = st.slider('Selectionner les derniers reportings:', 5, len(options_date), 30, help="Cette option s'affiche lorsque vous avez plus de 30 reportings différents")
                    options_date = options_date[:list_tail]

                options_select = st.multiselect(
                    'Selectionner les dates à afficher :', options_date, options_date)

                data_detail = filter_data(data_detail, options_select)
                data_scoring = filter_data(data_scoring, options_select)

            with col1:  # on met la col1 après, pour bien prendre en compte les modifs dans data_scoring
                st.subheader('Evolution')
                st.dataframe(data_scoring\
                    .set_index('date')\
                    .drop('datetime', axis=1)\
                    .rename(columns={'score_general' : 'General',
                                    'score_spd' : 'Speed',
                                    'score_arte' : 'Artefact'}),
                            use_container_width=True)
                
                data_detail.sort_values(by='datetime', ascending=True, inplace=True)
                data_scoring.sort_values(by='datetime', ascending=True, inplace=True)
                

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data_scoring['date'], y=data_scoring['score_general'], mode='lines+markers'))

                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
                fig.update_yaxes(showgrid=False)
                
                # sauter des lignes
                st.text("")
                st.text("")
                
                st.subheader('Score general')
                

                
                data_100 = data_detail[data_detail['Palier'] == '100']
                data_110 = data_detail[data_detail['Palier'] == '110']
                data_120 = data_detail[data_detail['Palier'] == '120']

                tab1, tab2, tab3, tab4 = st.tabs(
                    ['General', 'Palier 100', 'Palier 110', 'Palier 120'])

                with tab1:
                    st.plotly_chart(fig)

                with tab2:
                    fig_rune_100 = plotline_evol_rune_visu(data_100)
                    st.plotly_chart(fig_rune_100)

                with tab3:
                    fig_rune_110 = plotline_evol_rune_visu(data_110)
                    st.plotly_chart(fig_rune_110)

                with tab4:
                    fig_rune_120 = plotline_evol_rune_visu(data_120)
                    st.plotly_chart(fig_rune_120)
                


                st.subheader('Speed')

                data_detail_spd = transformation_stats_visu(
                    'sw_spd', st.session_state['id_joueur'], distinct=True, ascending=True)
                data_scoring_spd = transformation_stats_visu(
                    'sw_score', st.session_state['id_joueur'], distinct=True, score='score_spd', ascending=True)

                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=data_scoring_spd['date'], y=data_scoring_spd['score_spd'], mode='lines+markers'))

                fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
                fig2.update_yaxes(showgrid=False)

                data_25 = data_detail_spd[data_detail_spd['Palier'] == '23-25']
                data_28 = data_detail_spd[data_detail_spd['Palier'] == '26-28']
                data_31 = data_detail_spd[data_detail_spd['Palier'] == '29-31']
                data_35 = data_detail_spd[data_detail_spd['Palier'] == '32-35']
                data_36 = data_detail_spd[data_detail_spd['Palier'] == '36+']

                tab_spd_general, tab2325, tab2628, tab2931, tab3235, tab36 = st.tabs(
                    ['General', '23-25', '26-28', '29-31', '32-35', '36+'])

                with tab_spd_general:
                    st.plotly_chart(fig2)

                with tab2325:
                    fig25 = plotline_evol_rune_visu(data_25)
                    st.plotly_chart(fig25)

                with tab2628:
                    fig28 = plotline_evol_rune_visu(data_28)
                    st.plotly_chart(fig28)
                with tab2931:
                    fig31 = plotline_evol_rune_visu(data_31)
                    st.plotly_chart(fig31)
                with tab3235:
                    fig35 = plotline_evol_rune_visu(data_35)
                    st.plotly_chart(fig35)
                with tab36:
                    fig36 = plotline_evol_rune_visu(data_36)
                    st.plotly_chart(fig36)

                st.subheader('Artefact')
                data_detail_arte = transformation_stats_visu(
                    'sw_arte', st.session_state['id_joueur'], distinct=True, ascending=True)
                data_scoring_arte = transformation_stats_visu(
                    'sw_score', st.session_state['id_joueur'], distinct=True, score='score_arte', ascending=True)

                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=data_scoring_arte['date'], y=data_scoring_arte['score_arte'], mode='lines+markers'))

                tab_arte_general, tab80, tab85, tab90, tab95, tab100 = st.tabs(
                    ['General', '80', '85', '90', '95', '100+'])

                data_80 = data_detail_arte[data_detail_arte['Palier'] == '80']
                data_85 = data_detail_arte[data_detail_arte['Palier'] == '85']
                data_90 = data_detail_arte[data_detail_arte['Palier'] == '90']
                data_95 = data_detail_arte[data_detail_arte['Palier'] == '95']
                data_100 = data_detail_arte[data_detail_arte['Palier'] == '100+']

                with tab_arte_general:
                    st.plotly_chart(fig3)
                with tab80:
                    fig80 = px.line(data_80, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig80)
                with tab85:
                    fig85 = px.line(data_85, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig85)
                with tab90:
                    fig90 = px.line(data_90, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig90)
                with tab95:
                    fig95 = px.line(data_95, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig95)
                with tab100:
                    fig100 = px.line(data_100, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig100)

        except Exception as e:
            print(e)
            st.subheader('Erreur')
            st.write('Pas de JSON chargé')


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Evolution des stats')
        palier_page()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
    
    
    
st.caption('Made by Tomlora')