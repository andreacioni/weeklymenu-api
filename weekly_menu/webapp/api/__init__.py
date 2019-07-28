from flask_restful import Api

from .resources import Ingredients

API_VERSION = 'v1'
API_PREFIX = '/api'
BASE_PATH = API_PREFIX + '/' + API_VERSION

api = Api()

def create_module(app):
    
    #Ingredients
    api.add_resource(
        Ingredients,
        BASE_PATH + '/ingredients'
    )

    api.init_app(app)