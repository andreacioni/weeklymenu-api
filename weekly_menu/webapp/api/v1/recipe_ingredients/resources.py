import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField
from mongoengine.queryset.visitor import Q

from .schemas import RecipeSchema
from ...models import RecipeIngredient, User
from ... import validate_payload, paginated, mongo, update_document, load_user_info
from ...exceptions import DuplicateEntry, BadRequest


class RecipeIngredientList(Resource):
    @jwt_required
    @load_user_info
    def get(self, req_args, user_info: User):
        page = Recipe.objects(owner=str(user_info.id)).paginate(
            page=req_args['page'], per_page=req_args['per_page'])
        page.items = [_dereference_ingredient(item) for item in page.items]
        return page

    @jwt_required
    @validate_payload(RecipeSchema(), 'recipe')
    @load_user_info
    def post(self, recipe: Recipe, user_info: User):
        # Associate user id
        recipe.owner = user_info.id

        try:
            recipe.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(
                description="duplicate entry found for a recipe", details=nue.args or [])

        return recipe, 201


class RecipeIngredientInstance(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, recipe_id=''):
        if recipe_id != None:
            recipe = Recipe.objects(Q(id=recipe_id) & Q(
                owner=str(user_info.id))).get_or_404()

            return _dereference_ingredient(recipe)

    @jwt_required
    @load_user_info
    def delete(self, user_info: User, recipe_id=''):
        if recipe_id != None:
            Recipe.objects(Q(id=recipe_id) & Q(
                owner=str(user_info.id))).get_or_404().delete()
            return "", 204

    @jwt_required
    @validate_payload(RecipeSchema(), 'new_recipe')
    @load_user_info
    def put(self, new_recipe: Recipe, user_info: User, recipe_id=''):
        if recipe_id != None:
            old_recipe = Recipe.objects(id=recipe_id).get_or_404()
            new_recipe = update_document(old_recipe, new_recipe)
            return new_recipe, 200
