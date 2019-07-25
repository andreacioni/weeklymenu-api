import pprint

from flask_restful import Resource, abort, request

import weekly_menu.db as db

class Ingredients(Resource):
    def get(self):
        print(pprint.pprint(db.get_client().test.ingredients.find().limit(5)))
        return pprint.pprint(db.get_client().test.ingredients.find().limit(5))