from app.helpers import get_printers, log_error
from flask import jsonify, request, Blueprint, render_template
from flask_jwt_extended import create_access_token, jwt_required
from datetime import datetime
from helpers.conner import get_asociation_rules

routes = Blueprint('routes', __name__)
today = datetime.now().strftime('%Y-%m-%d')

PRINTERS_ON_WEB = {}
RULES = get_asociation_rules()

# Helpers imports the global variables
from helpers.products import delelete_product, get_departments, get_product, get_product_by_id, get_product_siblings, insert_product, searc_products_by_description, update_product
from helpers.tickets import get_tickets_by_date, ticket_create, ticket_print, ticket_update
from helpers.utils import get_products_changes, labels_print, drawer_open
from helpers.conner import conner_asociation_rules, conner_consequents


@routes.route('/')
@routes.route('/dashboard')
@routes.route('/<path:path>')
@routes.route('/dashboard/<path:path>')
def serve_index(path=None):
    print(path)
    return render_template('index.html')

@routes.route('/api/get/product/')
@routes.route('/api/get/product/id/')
@routes.route('/api/get/products/description/')
@routes.route('/api/get/siblings/product/id/')
@routes.route('/api/delete/product/id/')
@routes.route('/api/get/tickets/day/')
@routes.route('/api/get/modifiedProducts/day/')
def notParameters():
    return jsonify({'message' : 'Not data sended'})


def generate_token(identity, role):
    additional_claims = {"role": role}
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    return access_token

@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    keys = ['username', 'password']
    for key in keys:
        if not key in keys:
            return jsonify({'message' : 'Not data sended'}), 400


    username = data.get('username').lower()
    password = data.get('password')

    if username == 'admin' and password == '14725':
        access_token = generate_token(identity=password, role='user')  
        return jsonify({'login': 'succesfull', 'token': access_token, 'role': 'user'}), 200
    
    elif username == 'admin' and password == '110603':
        access_token = access_token = generate_token(identity=password, role='admin')
        
        return jsonify({'login': 'succesfull', 'token': access_token, 'role': 'admin'}), 200

    else:
        return jsonify({'login': 'unauthorized', 'message': 'Uncorrect credentials'}), 401
    
@routes.route('/api/init/new', methods=['GET'])
@jwt_required()
def initPc():
    try:
        client_ip = request.remote_addr
        client_printers = get_printers(ipv4=client_ip)
        global PRINTERS_ON_WEB
        PRINTERS_ON_WEB.update(client_printers)
    except Exception as e:
        log_error(f'/api/init/new: {e}')
        return jsonify({'printers': 'Not found printers there!'}), 404
    finally:
        return jsonify({'printers': 'loaded'})
    
@routes.route('/api/get/printers', methods=['GET'])
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
    try:
        if not search:
            return jsonify({'message' : 'Not data sended'}), 100
        
        return jsonify(get_product(search))
    
    except Exception as e:
        if e: log_error(f'/api/get/product/<str>: {e}')
        return jsonify({"message": "Product not found"}), 404



@routes.route('/api/get/product/id/<string:id>', methods=['GET'])
@jwt_required()
def getProductById(id):
    try:
        if not id:
            return jsonify({'message' : 'Not data sended'}), 100
        
        return jsonify(get_product_by_id(id))
    except Exception as e:
        if e: log_error(f'/api/get/product/id/<str>: {e}')
        return jsonify({"message": "Product not found"}), 404



@routes.route('/api/get/products/description/<string:description>', methods=['GET'])
@jwt_required()
def getAllProducts(description):
    try:
        return jsonify(searc_products_by_description(description))
    except Exception as e:
        if e: log_error(f'/api/get/products/description/<str>: {e}')
        return jsonify('{"message": "Product not found"}'), 404



@routes.route('/api/get/siblings/product/id/<string:search>', methods=['GET'])
@jwt_required()
def getSiblings(search):
    try:
        return jsonify(get_product_siblings(search))
    except Exception as e:
        if e: log_error(f'/api/get/products/description/<str>: {e}')
        return jsonify({"message": "Not siblings!"}), 404
    


@routes.route('/api/get/all/departments', methods=['GET'])
@jwt_required()
def getDepartments():
    try:
        return jsonify(get_departments())
    except Exception as e:
        if e: log_error(f'/api/get/all/departments/: {e}')
        return jsonify({"message": "Problems at fetching departments!"}), 500



#PRODUCTS CRUD ----------------->
@routes.route('/api/create/product', methods=['POST'])
@jwt_required()
def createProduct():
    try:
        data = dict(request.get_json())

        if data is None:
            raise Exception

        return jsonify(insert_product(data))
            
    except Exception as e:
        if e: log_error(f'/api/create/product: {e}')
        return jsonify({'message' : "Couldn't create the product"}), 500




@routes.route('/api/update/product', methods=['PUT'])
@jwt_required()
def updateProduct():
    try:
        data = dict(request.get_json())
        if data is None:
            raise Exception

        return jsonify(update_product(data))
    
    except Exception as e:
        if e: log_error(f'/api/update/product/: {e}')
        return jsonify({'message' : "Couldn't update all of the products"}), 500



@routes.route('/api/delete/product/id/<string:id>', methods=['DELETE'])
@jwt_required()
def deleteProductById(id):
    try:
        if not id:
            return jsonify({'message' : 'Not data sended'}), 100
        
        return jsonify(delelete_product(id))
    
    except Exception as e:
        if e: log_error(f'/api/delete/product/id/<str>: {e}')
        return jsonify({'message' : f'Not found product with code = {id}'}), 404



#TICKET MANAGEMENT
@routes.route('/api/get/tickets/day/<string:day>', methods=['GET'])
@jwt_required()
def getTicketsByDate(day): # Input date format YYYY-MM-DD
    try:
        if not day:
            return jsonify({'message' : 'Not data sended'}), 100

        return jsonify(get_tickets_by_date(day))
    
    except Exception as e:
        if e: log_error(f'/api/get/tickets/day/<str>: {e}')
        return jsonify({'message' : 'Problems at getting tickets!'}), 400


@routes.route('/api/print/ticket/id', methods=['POST'])
@jwt_required()
def printTicketById():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400

        return jsonify(ticket_print(data))
    
    except Exception as e:
        if e: log_error(f'/api/print/ticket/id: {e}')
        return jsonify({'message' : 'Problems at getting tickets!'}), 400


#TICKET CRUD
@routes.route('/api/create/ticket', methods=['POST'])
@jwt_required()
def createTicket():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        return jsonify(ticket_create(data))
    
    except Exception as e:
        if e: log_error(f'/api/create/ticket: {e}')
        return jsonify({'message' : 'Problems at updating database!'}), 500



@routes.route('/api/update/ticket', methods=['PUT'])
@jwt_required()
def updateTicket():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        

        return jsonify(ticket_update(data))
    
    except Exception as e:
        if e: log_error(f'/api/update/ticket/: {e}')
        return jsonify({'message' : 'Problems at updating tickets!'}), 400

#DRAWER SERVICE
@routes.route('/api/openDrawer', methods=['POST'])
@jwt_required()
def openDrawer():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        return jsonify(drawer_open(data))
    except Exception as e:
        if e: log_error(f'/api/openDrawer: {e}')
        return jsonify({'message' : 'Drawer can not be open'}), 500

#LABELS SERVICE
@routes.route('/api/get/modifiedProducts/day/<string:day>', methods=['GET'])
@jwt_required()
def getModifiedByDay(day):
    try:
        if not day:
            return jsonify({'message' : 'Not data sended'}), 100

        return jsonify(get_products_changes(day))
    
    except Exception as e:
        if e: log_error(f'/api/get/modifiedProducts/day/<str>: {e}')
        return jsonify({'message' : 'Not data finded'}), 404

@routes.route('/api/print/labels', methods=['POST'])
@jwt_required()
def printLabels():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        return jsonify(labels_print(data))
    except Exception as e:
        if e: log_error(f'/api/print/labels/: {e}')
        return jsonify({'message' : "Couldn't print labels!"}), 500
    
#Data science and IA development
@routes.route('/api/ia/consequent', methods=['POST'])
@jwt_required()
def consequent():
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400


        return jsonify(conner_consequents(data))

    except Exception as e:
        if e: log_error(f'/api/ia/consequent: {e}')
        return jsonify({'message' : "Couldn't get consequent products!"}), 500

@routes.route('/api/ia/asociation/rules', methods=['GET'])
@jwt_required()
def asociation_rules():
    try:
        
        return jsonify(conner_asociation_rules())

    except Exception as e:
        if e: log_error(f'/api/ia/asociation/rules: {e}')
        return jsonify({'message' : "Couldn't get asociation rules!"}), 500