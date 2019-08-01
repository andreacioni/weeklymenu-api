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