from marshmallow_mongoengine import ModelSchema

from flask_restful import Api

from flask_mongoengine import MongoEngine

API_PREFIX = '/api'

api = Api()
mongo = MongoEngine()

def create_module(app):

    mongo.init_app(app)

    from .v1 import create_module as create_api_v1

    create_api_v1(app, api)

    api.init_app(app)

def validate_payload(model_schema: ModelSchema):
    data, errors = UserSchema().load(request.get_json())

    if len(errors) != 0:
        return jsonify({'msg' : 'dhe'}), 400
    else:
        return jsonify({'msg' : data}), 200
    def decorate(func):
        def wrapper(*args, **kwargs):
            pass
        return wrapper
    
    return decorate