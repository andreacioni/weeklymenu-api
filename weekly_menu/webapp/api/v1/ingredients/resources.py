import pprint

from flask import jsonify
from flask_restful import Resource, abort, request

from ...models import Ingredient
from .. import mongopage_to_json

class Ingredients(Resource):
    def get(self):
        page = Ingredient.objects.paginate(page=1, per_page=10)
        return mongopage_to_json(page)