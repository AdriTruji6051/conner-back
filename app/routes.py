from app.models import close_hist_db, get_hist_db, get_pdv_db, close_pdv_db, get_products_by_description, insert_history_register
from app.helpers import create_ticket_struct, get_printers, open_drawer, send_label_to_printer, send_ticket_to_printer, log_error
from flask import jsonify, request, Blueprint, render_template
from flask_jwt_extended import create_access_token, jwt_required
from datetime import datetime

routes = Blueprint('routes', __name__)
today = datetime.now().strftime('%Y-%m-%d')
PRINTERS_ON_WEB = {}


@routes.route('/')
@routes.route('/dashboard')
@routes.route('/<path:path>')
@routes.route('/dashboard/<path:path>')
def serve_index(path=None):
    print(path)
    return render_template('index.html')


@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username').lower()
    password = data.get('password')

    if username == 'admin' and password == '14725':
        access_token = create_access_token(identity=username)
        return jsonify({'login': 'exitoso', 'token': access_token}), 200
    else:
        return jsonify({'login': 'fallido', 'message': 'Credenciales incorrectas'}), 401
    
@routes.route('/api/init/new/', methods=['GET'])
@jwt_required()
def initPc():
    try:
        client_ip = request.remote_addr
        client_printers = get_printers(ipv4=client_ip)
        global PRINTERS_ON_WEB
        PRINTERS_ON_WEB.update(client_printers)
    except Exception as e:
        log_error(f'/api/init/new/: {e}')
        return jsonify({'printers': 'Not found printers there!'}), 404
    finally:
        return jsonify({'printers': 'loaded'})
    
@routes.route('/api/get/printers/', methods=['GET'])
@jwt_required()
def getPrinters():
    printers = []
    for key in PRINTERS_ON_WEB:
        if PRINTERS_ON_WEB[key]['isdefault'] == True and PRINTERS_ON_WEB[key]['ipv4'] == request.remote_addr:
            printers.insert(0, key)
        elif PRINTERS_ON_WEB[key]['isdefault'] == True:
            printers.append(key)
    return jsonify(printers)


#PRODUCTS MANAGEMENT
@routes.route('/api/get/product/<string:search>', methods=['GET'])
@jwt_required()
def getProduct(search):
    db = get_pdv_db()
    try:
        
        query = "SELECT * FROM products WHERE code = ?"
        prod = db.execute(query, [search]).fetchone()

        if prod is None:
            query = 'SELECT * FROM products WHERE description LIKE ?;'
            prod = get_products_by_description(db=db, query=query, params=search)

            if len(prod) == 0: 
                raise Exception
            else:
                return jsonify(prod)
        else:
            return jsonify([dict(prod)])
    except Exception as e:
        if e: log_error(f'/api/get/product/<str>: {e}')
        return jsonify({"message": "Product not found"}), 404
    finally:
        close_pdv_db()
    
@routes.route('/api/get/product/id/<string:id>', methods=['GET'])
@jwt_required()
def getProductById(id):
    db = get_pdv_db()
    try: 
        query = "SELECT * FROM products WHERE code = ?;"
        prod = db.execute(query, [id]).fetchone()

        if prod is None:
            raise Exception
        else:
            return jsonify(dict(prod))
    except Exception as e:
        if e: log_error(f'/api/get/product/id/<str>: {e}')
        return jsonify('{"message": "Product not found"}'), 404
    finally:
        close_pdv_db()

@routes.route('/api/get/products/description/<string:description>', methods=['GET'])
@jwt_required()
def getAllProducts(description):
    db = get_pdv_db()
    try:
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
            query += "ORDER BY priority DESC, CASE WHEN description LIKE ? THEN 0 ELSE 1 END, description;"
            params.append(f'{description[0]}%')
            prod = db.execute(query,params).fetchall()

        cont = 0
        answer = []
        for row in prod:
            answer.append(dict(row))
            cont += 1
            if cont >= 70: break

        return jsonify(answer)
    except Exception as e:
        if e: log_error(f'/api/get/products/description/<str>: {e}')
        return jsonify('{"message": "Product not found"}'), 404
    finally:
        close_pdv_db()

@routes.route('/api/get/siblings/product/id/<string:search>', methods=['GET'])
@jwt_required()
def getSiblings(search):
    db = get_pdv_db()
    try:
        query = "SELECT * FROM products WHERE parentCode = ?;"
        siblings = db.execute(query, [search]).fetchall()
        if not len(siblings):
            prod = dict(db.execute("SELECT parentCode FROM products WHERE code = ?;", [search]).fetchone())
            search = prod['parentCode']
            siblings = db.execute(query, [search]).fetchall()
            if siblings is None:
                raise Exception
        
        siblingsArray = []
        for pr in siblings:
            siblingsArray.append(dict(pr))

        parent = dict(db.execute("SELECT * FROM products WHERE code = ?;", [search]).fetchone())

        return jsonify({"parent" : parent, "childs" : siblingsArray})
    except Exception as e:
        if e: log_error(f'/api/get/products/description/<str>: {e}')
        return jsonify({"message": "Product not found"}), 404
    finally:
        close_pdv_db()

@routes.route('/api/get/all/departments/', methods=['GET'])
@jwt_required()
def getDepartments():
    db = get_pdv_db()
    try:
        query = "SELECT * FROM departments;"
        departments = db.execute(query).fetchall()
        
        departmentsArray = []
        for dept in departments:
            departmentsArray.append(dict(dept))

        return jsonify(departmentsArray)
    except Exception as e:
        if e: log_error(f'/api/get/all/departments/: {e}')
        return jsonify({"message": "Problems at getting departments!"}), 500
    finally:
        close_pdv_db()

#PRODUCTS CRUD ----------------->
@routes.route('/api/create/product/', methods=['POST'])
@jwt_required()
def createProduct():
    db = get_pdv_db()

    try:
        data = dict(request.get_json())
    
        if data is None:
            raise Exception

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

        return jsonify({'message' : 'Product succesfully created!'})
            
    except Exception as e:
        if e: log_error(f'/api/create/product/: {e}')
        return jsonify({'message' : f"Couldn't create the product"}), 500
    finally:
        close_pdv_db()
    
@routes.route('/api/update/product/', methods=['PUT'])
@jwt_required()
def updateProduct():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())
        if data is None:
            raise Exception

        db.execute("PRAGMA foreign_keys = ON;")

        #Updating the product!
        query = 'UPDATE products SET description = ?, saleType = ?, cost = ?, salePrice = ?, department = ?, wholesalePrice = ?, inventory = ?, profitMargin = ?, parentCode = ?, code = ?, modifiedAt = ? WHERE code = ?;'
        keys = ["description", "saleType", "cost", "salePrice", "department", "wholesalePrice", "inventory", "profitMargin", "parentCode", "code"]
        params = [data[key] for key in keys]
        params.append(today)
        params.append(data['originalCode'])
        db.execute(query, params)
        db.commit()

        #Insert register at history
        insert_history_register(data=data, today=today, method='PUT')

        query = 'UPDATE products SET cost = ?, salePrice = ?, wholesalePrice = ?, profitMargin = ?,  modifiedAt = ? WHERE code = ?;'
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
        return jsonify({'message' : 'Product succesfully updated!'})
    except Exception as e:
        if e: log_error(f'/api/update/product/: {e}')
        return jsonify({'message' : "Couldn't update all of the products"}), 500
    finally:
        close_pdv_db()

@routes.route('/api/delete/product/id/<string:id>', methods=['DELETE'])
@jwt_required()
def deleteProductById(id):
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
        
        return jsonify({'message' : f'Succesfully deleted product with code = {id}'})
    
    except Exception as e:
        if e: log_error(f'/api/delete/product/id/<str>: {e}')
        return jsonify({'message' : f'Not found product with code = {id}'}), 404
    finally:
        close_pdv_db()

#TICKET MANAGEMENT
@routes.route('/api/get/tickets/day/<string:day>', methods=['GET'])
@jwt_required()
def getTicketsByDate(day):
    #Input date format YYYY:MM:DD
    db = get_pdv_db()
    try:
        sql = 'SELECT * FROM tickets WHERE createdAt LIKE ?;'
        sqlPr = 'SELECT * FROM ticketsProducts WHERE ticketId = ?;'

        rows = db.execute(sql, [f'{day}%']).fetchall()
        answer = []

        for row in rows:
            row = dict(row)
            for key in row:
                if type(row[key]) == bytes:
                    row[key] = str(row[key])

            prodRows = db.execute(sqlPr, [row['ID']]).fetchall()
            products = []
            for prod in prodRows:
                products.append(dict(prod))
            
            row['products'] = products
            answer.append(row)

        return jsonify(answer)
    
    except Exception as e:
        if e: log_error(f'/api/get/tickets/day/<str>: {e}')
        return jsonify({'message' : 'Problems at getting tickets!'}), 400
    finally:
        close_pdv_db()

@routes.route('/api/print/ticket/id/', methods=['POST'])
@jwt_required()
def printTicketById():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        id = data['id']
        printerName = data['printerName']
        if(printerName):
            printer = PRINTERS_ON_WEB[printerName]
            
            sql = 'SELECT * FROM tickets WHERE ID = ?;'
            sqlPr = 'SELECT * FROM ticketsProducts WHERE ticketId = ?;'

            row = dict(db.execute(sql, [id]).fetchone())
            prodRows = db.execute(sqlPr, [id]).fetchall()

            products = []
            for prod in prodRows:
                prod = dict(prod)
                prod['import'] = prod['cantity'] * prod['usedPrice']
                products.append(prod)
            
            ticketStruct = create_ticket_struct(ticketID=id ,products=products, total=row['total'], subtotal=row['subTotal'], notes=row['notes'], date=row['createdAt'], productCount=row['articleCount'], wholesale=row['discount'])
            send_ticket_to_printer(ticket_struct=ticketStruct, printer=printer, open_drawer=False)

        return jsonify({'message' : 'Succesfull ticket reprint!'})
    
    except Exception as e:
        if e: log_error(f'/api/print/ticket/id/: {e}')
        return jsonify({'message' : 'Problems at getting tickets!'}), 400
    finally:
        close_pdv_db()


#TICKET CRUD
@routes.route('/api/create/ticket/', methods=['POST'])
@jwt_required()
def createTicket():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        #Keys: products,total, paidWith, notes, willPrint
        date = datetime.now()

        createAt = date.strftime('%Y-%m-%d %H:%M:%S')
        printerName = data['printerName']
        willPrint = data['willPrint']
        wholesale = data['wholesale']
        subtotal = data['total']
        total = data['paidWith']
        notes = data['notes']
        productsCount = data['productsCount']

        profitTicket = 0

        ticketId = dict(db.execute('SELECT MAX (ID) FROM tickets;').fetchone())['MAX (ID)']
        queryTicktProd = 'INSERT INTO ticketsProducts (ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) values (?,?,?,?,?,?,?,?);'
        queryTickt = 'INSERT INTO tickets (ID, createdAt, subTotal, total, profit, articleCount, notes, discount) values (?,?,?,?,?,?,?,?);'

        if(ticketId):
            ticketId += 1
        else:
            ticketId = 1

        for prod in data['products']:
            profit = 0
            if 'wholesalePrice' in prod: prod['wholesalePrice'] = prod['wholesalePrice'] if prod['wholesalePrice'] else prod['salePrice']
            else: prod['wholesalePrice'] = prod['salePrice']

            if(prod['cost']): profit = ( (prod['wholesalePrice'] * 100) / prod['cost'] ) - 100 if wholesale else ( prod['salePrice'] * 100) /  (prod['cost']) - 100
            else: profit = 10

            params = [
                ticketId,
                prod['code'],
                prod['description'],
                prod['cantity'],
                round(profit),
                createAt,
                wholesale,
                prod['wholesalePrice'] if wholesale else prod['salePrice']
            ]
            
            profitTicket += round(( prod['wholesalePrice'] * (profit /100)) * prod['cantity'] ) if wholesale else round(( prod['salePrice'] * (profit / 100)) * prod['cantity'] )
            db.execute(queryTicktProd, params)
        
        
        params = [
            ticketId,
            createAt,
            subtotal,
            total,
            profitTicket,
            productsCount,
            notes,
            wholesale
        ]

        db.execute(queryTickt, params)
        db.commit()

        if(willPrint and printerName):
            createAt = date.strftime('%d-%m-%Y %H:%M')
            ticketStruct = create_ticket_struct(ticketID=ticketId, products=data['products'], total=total, subtotal=subtotal,notes=notes, date=createAt, productCount=productsCount, wholesale=wholesale )
            printer = PRINTERS_ON_WEB[printerName]

            send_ticket_to_printer(ticket_struct=ticketStruct, printer=printer, open_drawer=False)

        if(not willPrint and printerName):
            printer = PRINTERS_ON_WEB[printerName]
            open_drawer(printer=printer)
        
        return jsonify({'folio' : ticketId})
    except Exception as e:
        if e: log_error(f'/api/create/ticket/: {e}')
        return jsonify({'message' : 'Problems at updating database!'}), 500
    finally:
        close_pdv_db()

@routes.route('/api/update/ticket/', methods=['PUT'])
@jwt_required()
def updateTicket():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        ticketID = data['ID']
        products = data['products']

        db.execute('UPDATE tickets SET profit = ?, discount = ?, subTotal = ?, articleCount = ? WHERE ID = ?;',[
            data['profit'],
            data['discount'],
            data['subTotal'],
            data['articleCount'],
            ticketID
        ])
        
        rows = db.execute('SELECT ID FROM ticketsProducts WHERE ticketId = ?;', [ticketID])
        prodIDs = set()
        for row in rows:
            prodIDs.add(dict(row)['ID'])

        for prod in products:
            db.execute('UPDATE ticketsProducts SET cantity = ? WHERE ID = ?;', [
                prod['cantity'],
                prod['ID']
            ])
            prodIDs.discard(prod['ID'])
        
        for id in prodIDs:
            db.execute('UPDATE ticketsProducts SET ticketId = ? WHERE ID = ?;', [ticketID * -1,id])
        
        db.commit()

        return jsonify({'message' : 'Ticket updated!'})
    except Exception as e:
        if e: log_error(f'/api/update/ticket/: {e}')
        return jsonify({'message' : 'Problems at updating tickets!'}), 400
    finally:
        close_pdv_db()

#DRAWER SERVICE
@routes.route('/api/openDrawer/', methods=['POST'])
@jwt_required()
def openDrawer():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        printer = PRINTERS_ON_WEB[data['printerName']]

        open_drawer(printer)
        
        return jsonify({'message' : 'Succesfull drawer open'})
    except Exception as e:
        if e: log_error(f'/api/openDrawer/: {e}')
        return jsonify({'message' : 'Pedillos'}), 500

#LABELS SERVICE
@routes.route('/api/get/modifiedProducts/day/<string:day>', methods=['GET'])
@jwt_required()
def detModifiedByDay(day):
    db = get_hist_db()
    try:
        rows = db.execute("SELECT * FROM history_changes_products WHERE modifiedAt = ? AND operationType != 'DELETE';",[day]).fetchall()
        products = []
        for row in rows:
            products.append(dict(row))

        return jsonify(products)
    except Exception as e:
        if e: log_error(f'/api/get/modifiedProducts/day/<str>: {e}')
        return jsonify({'message' : 'Not data finded'}), 404
    finally:
        close_hist_db()

@routes.route('/api/print/labels/', methods=['POST'])
@jwt_required()
def printLabels():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        labels = data['labels']
        printer = PRINTERS_ON_WEB[data['printerName']]

        for label in labels:
            send_label_to_printer(label, printer)
        
        return jsonify({'message' : 'Succesfull labels print'})
    except Exception as e:
        if e: log_error(f'/api/print/labels/: {e}')
        return jsonify({'message' : "Couldn't print labels!"}), 500