from flask_restful import Api

api = Api()

def create_module(app):
    api.init_app(app)