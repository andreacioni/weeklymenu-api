import pprint

from flask import jsonify
from flask_restful import Resource, abort, request, marshal_with
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError

from .schemas import IngredientSchema
from ...models import Ingredient
from ... import validate_payload, paginated, mongo
from ...exceptions import DuplicateEntry

class Ingredients(Resource):
    @jwt_required
    @paginated
    def get(self, req_args, ing_id=None):
        if ing_id != None:
            return Ingredient.objects(_id__exact=mongo.ObjectIdField(ing_id))
        else:
            page = Ingredient.objects.paginate(page=req_args['page'], per_page=req_args['per_page'])
            return page

    @jwt_required
    @validate_payload(IngredientSchema(), 'ingredient')
    @marshal_with(Ingredient())
    def post(self, ingredient: Ingredient):
        try:
            ingredient.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for an ingredient", details=nue.args or [])
        
        return ingredient, 201

