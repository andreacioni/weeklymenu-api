from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow_mongoengine import schema

from . import authenticate, encode_password
from .schemas import PostRegisterUserSchema, PostUserTokenSchema
from .. import BASE_PATH
from ... import validate_payload
from ...models import User, ShoppingList
from ...exceptions import InvalidCredentials

auth_blueprint = Blueprint(
    'auth',
    __name__,
    url_prefix = BASE_PATH + '/auth'
)

@auth_blueprint.route('/token', methods=['POST'])
@validate_payload(PostUserTokenSchema(), 'user')
def get_token(user: PostUserTokenSchema):
    user = authenticate(user['username'], user['password'])
    
    if not user:
        raise InvalidCredentials("Provided credentials doesn't match for specific user")

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token), 200


@auth_blueprint.route('/register', methods=['POST'])
@validate_payload(PostRegisterUserSchema(), 'user_meta')
def register_user(user_meta: PostRegisterUserSchema):
    user = User()
    user.username = user_meta['username']
    user.password = encode_password(user_meta['password'])
    user.email = user_meta['email']
    user.save()
    
    return jsonify(user.to_mongo()), 200