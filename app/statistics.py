from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from helpers.statistics import statitistic_ticket_day, statitistic_ticket_range


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
    
@routesStat.route('/statistics/tickets/range/<string:start_date>/<string:end_date>', methods=['GET'])
@jwt_required()
def ticket_statistics_range(start_date, end_date):
    try:
        jwt_claims = get_jwt()
        role = jwt_claims.get("role")
        
        if role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401
        
        return jsonify(statitistic_ticket_range(start_date, end_date))
    except Exception as e:
        if e == 'NO DATA': return jsonify({'message': 'NO DATA'}), 404
        return jsonify({'message': 'could not fetch data'}), 500