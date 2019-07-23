from flask_restful import Resource, abort, request

class Ingredients(Resource):
    def get(self):
        return 'ciao'