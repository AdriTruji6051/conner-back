import sqlite3
from flask import g

DATABASE = './db/data_base.db'
HISTORY = './db/history.db'
DRAWER_LOGS = './db/drawer_logs.db'
CONFIG_DB = './db/config.db'

def get_pdv_db() -> object:
    try:
        if 'pdv_db' not in g:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    except Exception as e:
        raise(e)

def close_pdv_db():
    try:
        db = g.pop('pdv_db', None)
        if db is not None:
            db.close()

    except Exception as e:
        raise(e)


def get_conf_db() -> object:
    try:
        if 'conf_db' not in g:
            g.db = sqlite3.connect(CONFIG_DB)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    except Exception as e:
        raise(e)

def close_conf_db():
    try:
        db = g.pop('conf_db', None)
        if db is not None:
            db.close()

    except Exception as e:
        raise(e)

def get_hist_db() -> object:
    try:
        if 'hist' not in g:
            g.db = sqlite3.connect(HISTORY)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    except Exception as e:
        raise(e)

def close_hist_db():
    try:
        db = g.pop('hist', None)
        if db is not None:
            db.session.remove()
            db.close()

    except Exception as e:
        raise(e)  
    
def get_drawer_db() -> object:
    try:
        if 'draw' not in g:
            g.db = sqlite3.connect(DRAWER_LOGS)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    except Exception as e:
        raise(e)

def close_drawer_db():
    try:
        db = g.pop('draw', None)
        if db is not None:
            db.session.remove()
            db.close()

    except Exception as e:
        raise(e)  

def get_products_by_description(db = object, query = str, params = str) -> list:
    try:
        rows = db.execute(query, [f'%{params}%']).fetchall()

        prod = []
        insertIndex = 0
        for row in rows:
            row = dict(row)
            des = row['description'][:len(params)].upper()
            if des == params: 
                prod.insert(insertIndex, row)
                insertIndex += 1
            else: 
                prod.append(row) 

        return prod
    
    except Exception as e:
        raise(e)
    
def insert_history_register(data = dict, today = str, method = str):
    db = get_hist_db()
    try:
        query = 'INSERT INTO history_changes_products (code, description, saleType, cost, salePrice, wholesalePrice, profitMargin, operationType, modifiedAt) values (? ,?, ?, ?, ?, ?, ?, ?, ?);'
        keys = ["code", "description", "saleType", "cost", "salePrice", "wholesalePrice", "profitMargin"]
        params = [data[key] for key in keys]
        params.append(method)
        params.append(today)
        db.execute(query, params)
        db.commit()
    except Exception as e:
        raise e
    finally:
        close_hist_db()
