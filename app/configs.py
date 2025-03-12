from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required

from app.helpers import log_error
from helpers.models.Config import Config


routesConfig = Blueprint('routes_configuration', __name__)

@routesConfig.route('/configs/ticket/headers', methods=['GET'])
@jwt_required()
def get_ticket_headers():
    try:
        return jsonify(Config.get_ticket_headers())
    except Exception as e:
        if e == 'NO DATA': return jsonify({'message': 'NO DATA'}), 404
        log_error(f'/configs/ticket/headers: {e}')
        return jsonify({'message': 'could not fetch data'}), 500
    
@routesConfig.route('/configs/ticket/footers', methods=['GET'])
@jwt_required()
def get_ticket_footers():
    try:
        return jsonify(Config.get_ticket_footers())
    except Exception as e:
        if e == 'NO DATA': return jsonify({'message': 'NO DATA'}), 404
        log_error(f'/configs/ticket/footers: {e}')
        return jsonify({'message': 'could not fetch data'}), 500