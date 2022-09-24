import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from gestion_bdd import lire_bdd

def transformation_stats(nom_table):
    df_actuel = lire_bdd(nom_table)
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)
    df_actuel['date'] = pd.to_datetime(df_actuel['date'])
    df_actuel['date'] = df_actuel['date'].dt.strftime('%d/%m/%Y')
    if nom_table == 'sw':
        df_actuel.sort_values(by=['date','Set'], inplace=True)
    else:
        df_actuel.sort_values(by='date', inplace=True)
    df_actuel = df_actuel[df_actuel['Joueur'] == st.session_state['pseudo']]
    df_actuel.drop(['Joueur'], axis=1, inplace=True)
    

    
    if nom_table == 'sw':
        df_actuel = pd.melt(df_actuel, id_vars=['date', 'Set'], value_vars=['100', '110', '120'], var_name='Palier', value_name='Nombre')
        df_actuel.sort_values(by=['date', 'Set', 'Palier'], inplace=True)
    else:
        df_actuel = pd.pivot_table(df_actuel, 'score', index='date')
        df_actuel['score'] = df_actuel['score'].astype('int')
    
    return df_actuel


def plotline_evol_rune(df):
    fig = px.line(df, x="date", y="Nombre", color="Set")
    fig.update_layout({
                'plot_bgcolor': 'rgb(255, 255, 255)',
                'paper_bgcolor': 'rgba(0, 0, 0,0)'
    })
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_yaxes(showgrid=False)
    return fig


def palier_page():
    try:
        data_detail = transformation_stats('sw')
        data_scoring = transformation_stats('sw_score')
        
        
        st.subheader('Evolution')
           
        st.dataframe(data_scoring)
            
        fig = px.line(data_scoring, x=data_scoring.index, y='score')
        fig.update_layout({
                    'plot_bgcolor': 'rgb(255, 255, 255)',
                    'paper_bgcolor': 'rgba(0, 0, 0,0)'
        })

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig)
        
        data_100 = data_detail[data_detail['Palier'] == '100']
        data_110 = data_detail[data_detail['Palier'] == '110']
        data_120 = data_detail[data_detail['Palier'] == '120']
        
        
        
        st.write('Palier 100')
        fig1 = plotline_evol_rune(data_100)
        st.plotly_chart(fig1)

        st.write('Palier 110')
        fig2 = plotline_evol_rune(data_110)
        st.plotly_chart(fig2)

        st.write('Palier 120')
        fig3 = plotline_evol_rune(data_120)
        st.plotly_chart(fig3)
    
    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')