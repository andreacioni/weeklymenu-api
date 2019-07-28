from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from . import authenticate

auth_blueprint = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)

@auth_blueprint.route('/token', methods=['POST'])
def get_token():
    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify({'msg': 'Missing username parameter'}), 400
    if not password:
        return jsonify({'msg': 'Missing password parameter'}), 400
    
    user = authenticate(username, password)
    if not user:
        return jsonify({'msg': 'Bad username or password'}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200