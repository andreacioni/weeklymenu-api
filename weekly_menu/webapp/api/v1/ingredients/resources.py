import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError

from .schemas import IngredientSchema
from ...models import Ingredient
from .. import mongopage_to_json
from ... import validate_payload, paginated
from ...exceptions import DuplicateEntry

class Ingredients(Resource):
    @jwt_required
    @paginated
    def get(self, req_args):
        page = Ingredient.objects.paginate(page=req_args['page'], per_page=req_args['per_page'])
        return mongopage_to_json(page)

    @jwt_required
    @validate_payload(IngredientSchema(), 'ingredient')
    def post(self, ingredient: Ingredient):
        try:
            ingredient.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for an ingredient", details=nue.args)
        
        return jsonify(ingredient), 201

