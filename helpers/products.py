from app.models import get_pdv_db, close_pdv_db
from app.models import get_products_by_description, insert_history_register
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

def get_product(id_or_description):
    db = get_pdv_db()
    try:
        
        query = "SELECT * FROM products WHERE code = ?"
        prod = db.execute(query, [id_or_description]).fetchone()

        if prod is None:
            query = 'SELECT * FROM products WHERE description LIKE ?;'
            prod = get_products_by_description(db=db, query=query, params=id_or_description)

            if len(prod) == 0: 
                raise Exception
            else:
                return prod
        else:
            return [dict(prod)]
    except Exception as e:
        raise e
    finally:
        close_pdv_db()
    
def get_product_by_id(id) -> dict:
    db = get_pdv_db()
    try:
        
        query = "SELECT * FROM products WHERE code = ?;"
        prod = db.execute(query, [id]).fetchone()

        if prod is None:
            raise Exception
        else:
            return dict(prod)
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def searc_products_by_description(description) -> list:
    db = get_pdv_db()
    try:
        original_description = description
        description = description.split()
        if len(description) < 2:
            query = "SELECT * FROM products WHERE description LIKE ? ORDER BY priority DESC, CASE WHEN description LIKE ? THEN 0 ELSE 1 END, description;"
            prod = db.execute(query,[f'%{description[0]}%',f'{description[0]}%']).fetchall()
        else:
            params = list()
            query = "SELECT * FROM products WHERE"
            for i in range(len(description)):
                query += ' description LIKE ? AND ' if i + 1 < len(description) else 'description LIKE ? '
                params.append(f'%{description[i]}%')
            query += "ORDER BY priority DESC, CASE WHEN description LIKE ? THEN 0 WHEN description LIKE ? THEN 1 ELSE 2 END, description;"
            params.append(f'{original_description}%')
            params.append(f'{description[0]}%')
            prod = db.execute(query,params).fetchall()

        cont = 0
        products = []
        for row in prod:
            products.append(dict(row))
            cont += 1
            if cont >= 70: break

        return products
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def get_product_siblings(id) -> list:
    db = get_pdv_db()
    try:
        query = "SELECT * FROM products WHERE parentCode = ?;"
        siblings = db.execute(query, [id]).fetchall()
        if not len(siblings):
            prod = dict(db.execute("SELECT parentCode FROM products WHERE code = ?;", [id]).fetchone())
            id = prod['parentCode']
            siblings = db.execute(query, [id]).fetchall()
            if not len(siblings):
                raise Exception
        
        siblingsArray = []
        for pr in siblings:
            siblingsArray.append(dict(pr))

        parent = dict(db.execute("SELECT * FROM products WHERE code = ?;", [id]).fetchone())

        return {"parent" : parent, "childs" : siblingsArray}
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def get_departments() -> list:
    db = get_pdv_db()
    try:
        query = "SELECT * FROM departments;"
        departments = db.execute(query).fetchall()
        
        departmentsArray = []
        for dept in departments:
            departmentsArray.append(dict(dept))

        return departmentsArray
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def insert_product(data):
    db = get_pdv_db()
    try:
        query = 'SELECT * FROM products WHERE code = ?;'
        db.execute("PRAGMA foreign_keys = ON;")
        row = db.execute(query, [data.get('code')]).fetchone()

        if row is not None:
            raise Exception
        
        #Creamos el producto
        query = 'INSERT INTO products (code, description, saleType, cost, salePrice, department, wholesalePrice, inventory, profitMargin, parentCode, modifiedAt) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        keys = ["code", "description", "saleType", "cost", "salePrice", "department", "wholesalePrice", "inventory", "profitMargin", "parentCode"]
        params = [data[key] for key in keys]
        params.append(today)
        db.execute(query, params)
        db.commit()

        #Insertamos el registro en el historial
        insert_history_register(data=data, today=today, method='POST')

        return {'message' : 'Product succesfully created!'}
            
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def update_product(data):
    db = get_pdv_db()
    try:
        db.execute("PRAGMA foreign_keys = ON;")

        #Updating the product!
        query = 'UPDATE products SET description = ?, saleType = ?, cost = ?, salePrice = ?, department = ?, wholesalePrice = ?, inventory = ?, profitMargin = ?, parentCode = ?, code = ?, priority = ?, modifiedAt = ? WHERE code = ?;'
        keys = ["description", "saleType", "cost", "salePrice", "department", "wholesalePrice", "inventory", "profitMargin", "parentCode", "code", "priority"]
        params = [data[key] for key in keys]
        params.append(today)
        params.append(data['originalCode'])
        db.execute(query, params)
        db.commit()

        #Insert register at history
        insert_history_register(data=data, today=today, method='PUT')

        query = 'UPDATE products SET cost = ?, salePrice = ?, wholesalePrice = ?, profitMargin = ?, modifiedAt = ?, WHERE code = ?;'
        keys = ["cost", "salePrice", "wholesalePrice", "profitMargin"]

        siblings = data['siblings']
        #Updating siblings!
        if siblings:
            for sibl in siblings:
                if sibl == data['originalCode']: continue
                params = [data[key] for key in keys]
                params.append(today)
                params.append(sibl)
                db.execute(query, params)

                historical = dict(db.execute("SELECT * FROM products WHERE code = ?;", [f'{sibl}']).fetchone())
                insert_history_register(data=historical, today=today, method='PUT')

            db.commit()

        db.commit()

        try:
            prod = get_product_by_id(data['code'])
            if(prod['cost'] == data['cost'] and prod['salePrice'] == data['salePrice'] and prod['wholesalePrice'] == data['wholesalePrice'] and prod['profitMargin'] == data['profitMargin']):
                return {'message' : f'Product succesfully updated!, code: {data['code']}'}
            else: 
                raise Exception
            
        except Exception as e:
            update_product(data)
        
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def delelete_product(id):
    db = get_pdv_db()
    try:
        db.execute("PRAGMA foreign_keys = ON;") 
        query = 'SELECT * FROM products WHERE code = ?;'
        row = db.execute(query, [id]).fetchone()

        if row is None:
            raise Exception 

        query = 'DELETE FROM products WHERE code = ?;'
        db.execute(query, [id])
        db.commit()
        
        data = dict(row)
        insert_history_register(data=data, today=today, method='DELETE')
        
        return {'message' : f'Succesfully deleted product with code = {id}'}
    
    except Exception as e:
        raise e
    finally:
        close_pdv_db()