from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow_mongoengine import schema

from . import authenticate, encode_password
from .schemas import UserSchema, PostGetSchema
from .. import BASE_PATH
from ... import validate_payload
from ...models import User
from ...exceptions import InvalidCredentials

auth_blueprint = Blueprint(
    'auth',
    __name__,
    url_prefix = BASE_PATH + '/auth'
)

@auth_blueprint.route('/token', methods=['POST'])
@validate_payload(PostGetSchema(), 'user')
def get_token(user: PostGetSchema):
    user = authenticate(user['username'], user['password'])
    
    if not user:
        raise InvalidCredentials("Provided credentials doesn't match for specific user")

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token), 200


@auth_blueprint.route('/register', methods=['POST'])
@validate_payload(UserSchema(), 'user')
def register_user(user: User):
    user.password = encode_password(user.password)
    user.save()
    return jsonify(user), 200