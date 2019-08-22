import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField

from .schemas import IngredientSchema
from ...models import Ingredient
from ... import validate_payload, paginated, mongo
from ...exceptions import DuplicateEntry, BadRequest

class IngredientsList(Resource):
    @jwt_required
    @paginated
    def get(self, req_args):
        page = Ingredient.objects.paginate(page=req_args['page'], per_page=req_args['per_page'])
        return page
    
    @jwt_required
    @validate_payload(IngredientSchema(), 'ingredient')
    def post(self, ingredient: Ingredient):
        try:
            ingredient.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for an ingredient", details=nue.args or [])
        
        return jsonify(ingredient), 201

class IngredientInstance(Resource):
    @jwt_required
    def get(self, ingredient_id=''):
        if ingredient_id != None:
            return jsonify(Ingredient.objects(id=ingredient_id).get_or_404())
    
    @jwt_required
    def delete(self, ingredient_id=''):
        if ingredient_id != None:
            Ingredient.objects(id=ingredient_id).get_or_404().delete()
            return "", 204
