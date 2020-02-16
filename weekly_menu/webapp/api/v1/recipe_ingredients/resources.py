import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField, ObjectId
from mongoengine.queryset.visitor import Q

from .schemas import RecipeIngredientSchema
from ...models import Recipe, RecipeIngredient, User
from ... import validate_payload, paginated, mongo, load_user_info, put_document, patch_document
from ...exceptions import DuplicateEntry, BadRequest


def _retrieve_base_recipe(recipe_id: str, user_id: str) -> Recipe:
    return Recipe.objects(Q(owner=user_id) & Q(id=recipe_id)).get_or_404()


class RecipeIngredientList(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, recipe_id=''):
        recipe = _retrieve_base_recipe(recipe_id, str(user_info.id))
        return [recipe_ingredient.to_mongo() for recipe_ingredient in recipe.ingredients] if recipe.ingredients != None else []

    @jwt_required
    @validate_payload(RecipeIngredientSchema(), 'recipe_ingredient')
    @load_user_info
    def post(self, recipe_id, recipe_ingredient: RecipeIngredient, user_info: User):
        recipe = _retrieve_base_recipe(recipe_id, str(user_info.id))
        recipe.ingredients.append(recipe_ingredient)
        recipe.save()
        return recipe_ingredient, 201


class RecipeIngredientInstance(Resource):
    @jwt_required
    @load_user_info
    def delete(self, user_info: User, recipe_id='', ingredient_id=''):
        recipe = _retrieve_base_recipe(recipe_id, str(user_info.id))
        
        if recipe.ingredients != None and len(recipe.ingredients) == 1:
            raise BadRequest('no ingredients to delete for this recipe')

        ingredient_id = ObjectId(ingredient_id)

        recipe.ingredients = [recipe_ingredient for recipe_ingredient in recipe.ingredients if recipe_ingredient.ingredient.id != ingredient_id]

        recipe.save()

        return "", 204
