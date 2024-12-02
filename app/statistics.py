from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from helpers.statistics import statitistic_ticket_day


routesStat = Blueprint('routes_statistics', __name__)

@routesStat.route('/statistics/tickets/day/<string:date>', methods=['GET'])
@jwt_required()
def ticket_statistics(date):
    try:
        jwt_claims = get_jwt()
        role = jwt_claims.get("role")
        
        if role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401
        
        return jsonify(statitistic_ticket_day(date))
    except Exception as e:
        if e == 'NO DATA': return jsonify({'message': 'NO DATA'}), 404
        return jsonify({'message': 'could not fetch data'}), 500