import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField

from .schemas import RecipeSchema
from ...models import Recipe
from ... import validate_payload, paginated, mongo, update_document
from ...exceptions import DuplicateEntry, BadRequest

class RecipeList(Resource):
    @jwt_required
    @paginated
    def get(self, req_args):
        page = Recipe.objects.paginate(page=req_args['page'], per_page=req_args['per_page'])
        return page
    
    @jwt_required
    @validate_payload(RecipeSchema(), 'recipe')
    def post(self, recipe: Recipe):
        try:
            recipe.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for a recipe", details=nue.args or [])
        
        return recipe, 201

class RecipeInstance(Resource):
    @jwt_required
    def get(self, recipe_id=''):
        if recipe_id != None:
            return Recipe.objects(id=recipe_id).get_or_404()
    
    @jwt_required
    def delete(self, recipe_id=''):
        if recipe_id != None:
            Recipe.objects(id=recipe_id).get_or_404().delete()
            return "", 204
    
    @jwt_required
    @validate_payload(RecipeSchema(), 'new_recipe')
    def patch(self, new_recipe: Recipe, recipe_id=''):
        if recipe_id != None:
            old_recipe = Recipe.objects(id=recipe_id).get_or_404()
            new_recipe = update_document(old_recipe, new_recipe)
            return new_recipe, 200
