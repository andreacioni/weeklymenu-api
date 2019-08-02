from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow_mongoengine import schema

from . import authenticate
from .. import BASE_PATH
from ... import validate_payload
from .schemas import UserSchema

auth_blueprint = Blueprint(
    'auth',
    __name__,
    url_prefix = BASE_PATH + '/auth'
)

@auth_blueprint.route('/token', methods=['POST'])
def get_token():
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


@auth_blueprint.route('/register', methods=['POST'])
@validate_payload(UserSchema())
def register_user():
    pass