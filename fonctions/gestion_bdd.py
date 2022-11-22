
import pandas as pd

from sqlalchemy import *

import os

# https://betterprogramming.pub/how-to-execute-plain-sql-queries-with-sqlalchemy-627a3741fdb1

DB = os.environ.get('API_SQL')

engine = create_engine(DB, echo=False)



def lire_bdd(nom_table, format:str="df", index=None, distinct:bool=False):
    """Lire la BDD

    Parameters
    -----------
    nom_table: :class:`str`
            Le nom de la table
    format: :class:`str`
            Choix entre 'dict' ou 'df'
    """
    conn = engine.connect()
    
    if distinct:
        requetesql = f'SELECT distinct * FROM {nom_table}'
    else:
        requetesql = f'SELECT * FROM {nom_table}'
    try:
        df = pd.read_sql(requetesql, con=conn, index_col=index)
    except KeyError:
        nom_table = nom_table.lower()
        df = pd.read_sql(requetesql, con=conn, index_col='Joueur')
    except:
        nom_table = nom_table.lower()
        df = pd.read_sql(requetesql, con=conn, index_col=index)
    df = df.transpose()
    if format == "dict":
        df = df.to_dict()
    conn.close()
    return df

def lire_bdd_perso(requests:str, format:str="df", index_col:str="joueur", params=None):
    """Lire la BDD
    Parameters
    -----------
    requests: :class:`str`
            Requête SQL avec obligatoirement SELECT (columns) from (table) et éventuellement WHERE
    format: :class:`str`
            Choix entre 'dict' ou 'df'
    index_col: :class:`str`
            Colonne de l'index de la table
    params : dict avec {'variable' : 'value}
    
    
    Les variables doivent être sous forme %(variable)s
    """
    conn = engine.connect()

    if params == None:
        df = pd.read_sql(requests, con=conn, index_col=index_col)
    else:
        df = pd.read_sql(requests, con=conn, index_col=index_col, params=params)

    df = df.transpose()
    if format == "dict":
        df = df.to_dict()
    conn.close()
    return df
    


def sauvegarde_bdd(df, nom_table, methode_save='replace'):
    """Sauvegarde la BDD au format dataframe

    Parameters
    -----------
    df: :class:`dict` or  `dataframe`
            Dataframe ou dict
    nom_table: :class:`str`
            Nom de la table sql
    method_save: :class:`str`
            Si la table existe déjà, choix entre "append" pour insérer des nouvelles valeurs ou "replace" pour supprimer la table existante et la remplacer
    """
    conn = engine.connect()
    if not isinstance(df, pd.DataFrame): # si la variable envoyée n'est pas un dataframe, on l'a met au format dataframe
        df = pd.DataFrame(df)
        df = df.transpose()
    df.to_sql(nom_table, con=conn, if_exists=methode_save, index=True, method='multi', dtype={'Score' : Float(), 'serie' : BigInteger()})
    conn.close()
    
def supprimer_bdd(nom_table):
    conn = engine.connect()
    sql = text(f'DROP TABLE IF EXISTS {nom_table}')
    conn.execute(sql)
    conn.close()
    
def supprimer_data(Joueur, date):
    conn = engine.connect()
    params_sql = {'joueur' : Joueur, 'date' : date}
    sql1 = text(f'''DELETE FROM sw WHERE "id" = :joueur AND date = :date;
                    DELETE FROM sw_score WHERE "id" = :joueur AND date = :date''')  # :var_name
    conn.execute(sql1, params_sql)

    conn.close
    
def update_guilde(joueur, guilde, guildeid, compteid):
    conn = engine.connect()
    params_sql = {'joueur' : joueur, 'guilde' : guilde, 'guilde_id' : guildeid, 'joueur_id' : compteid}
    # sql1 = text('UPDATE sw_score SET guilde = :guilde WHERE "Joueur" = :joueur')
    sql1 = text('UPDATE sw_user SET guilde = :guilde, guilde_id = :guilde_id, joueur_id = :joueur_id WHERE joueur = :joueur')
    conn.execute(sql1, params_sql)
    conn.close()
    
def get_data_bdd(request:text, dict_params = None):
    conn = engine.connect()
    sql = text(request)
    if dict_params == None:
        data = conn.execute(sql)
    else:
        data = conn.execute(sql, dict_params)
    conn.close()
    
    return data
    
def requete_perso_bdd(request:text, dict_params:dict):
    """
    request : requête sql au format text
    
    dict_params : dictionnaire {variable : valeur}
    
    Rappel
    -------
    Dans la requête sql, une variable = :variable """
    conn = engine.connect()
    sql = text(request)
    conn.execute(sql, dict_params)
    conn.close
    
def get_user(joueur):
    '''Return l'id, la guilde et la visibilité du joueur demandé'''
    # à adapter avec l'id du compte quand on aura assez d'infos
    conn = engine.connect()
    sql = text('SELECT * FROM sw_user WHERE joueur = :joueur ')
    data = conn.execute(sql, {'joueur' : joueur})
    data = data.mappings().all()
    id_joueur = data[0]['id']
    guilde = data[0]['guilde']
    visibility = data[0]['visibility']
    guildeid = data[0]['guilde_id']   
    return id_joueur, guilde, visibility, guildeid
    
    