from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import sqlite3
import pandas as pd

DATABASE = './db/data_base.db'
IADB = './db/ia.db'

def get_db() -> object:
    try:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        return db
    except Exception as e:
        raise(e)
    
def get_IA_db() -> object:
    try:
        db = sqlite3.connect(IADB)
        db.row_factory = sqlite3.Row
        return db
    except Exception as e:
        raise(e)
    
def close_db(db):
    try:
        db.close()
    except Exception as e:
        raise(e)

def predict_product(products: set, rules: list):
    recomendaciones = set()
    for rule, consequent in rules:
        rule = set(rule)
        if(rule.issubset(products)):
            recomendaciones.update(consequent)
    
    return list(recomendaciones)

def a_priory():
    db = get_db()
    tickets = dict()
    try:
        rows = db.execute('SELECT ticketId, code FROM ticketsProducts;').fetchall()
        
        #Cleanind data
        for row in rows:
            row = dict(row)
            if '-' in row['code']: continue
            if tickets.get(row['ticketId']):
                tickets[row['ticketId']].append(row['code'])
            else:
                tickets[row['ticketId']] = [row['code']]

        transactions = list()
        for key in tickets:
            transactions.append(tickets[key])

        #Applying A-Priory
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        frequent_itemsets = apriori(df=df, min_support=0.01, use_colnames=True)
        
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5, num_itemsets=1)

        #Formating the results for INSERT
        predictionTuples = list()
        for _, row in rules.iterrows():
            ante = str(list(row['antecedents'])).replace(']','').replace('[','').replace(' ','').replace("'",'')
            conse = str(list(row['consequents'])).replace(']','').replace('[','').replace(' ','').replace("'",'')
            predictionTuples.append( (ante, conse) )

        print('Succesfull A-Priory!..')
        return predictionTuples
    
    except Exception as e:
        print('Failed -> ', e)
    finally:
        close_db(db)

def insert_new_predictions(predictions: list):
    iadb = get_IA_db()
    try:
        iadb.execute('DROP TABLE IF EXISTS Apriori;')
        iadb.execute('CREATE TABLE "Apriori" ("ANTECEDENTSET"	TEXT NOT NULL, "CONSECUENTSET"	TEXT NOT NULL);')
        for ante, conse in predictions:
            iadb.execute('INSERT INTO Apriori (ANTECEDENTSET, CONSECUENTSET) VALUES (?, ?);', [ante, conse])
        
        iadb.commit()
        print('Succesfull predictions INSERT!')
    except Exception as e:
        print('Error INSERT PRED ->', e)

def get_asociation_rules():
    dbIa = get_IA_db()
    try:
        rows = dbIa.execute('SELECT * FROM Apriori;').fetchall()
        rules = list()

        for row in rows:
            row = dict(row)
            rules.append((row['ANTECEDENTSET'].split(','), row['CONSECUENTSET'].split(',')))

        return rules
    
    except Exception as e:
        print('Exception at get asociation rules -> ', e)
    finally:
        close_db(dbIa)
    return