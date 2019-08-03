from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Response
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
    def decorate(func):
        def wrapper(*args, **kwargs):
            data, errors = model_schema.load(request.get_json())

            if len(errors) != 0:
                return BadRequest('Unexpected payload format', response=jsonify({'msg':'invalid payload supplied'})), 400


            kwargs['payload'] = data
            
            return func(*args, **kwargs)
        return wrapper
    
    return decorate