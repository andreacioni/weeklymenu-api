import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField, ObjectId
from mongoengine.queryset.visitor import Q

from .schemas import RecipeSchema, RecipeSchemaWithoutName, RecipeIngredientSchema
from ...models import Recipe, User, RecipeIngredient
from ... import validate_payload, paginated, mongo, put_document, patch_document, load_user_info
from ...exceptions import DuplicateEntry, BadRequest


def _dereference_ingredients(recipe: Recipe):
    if recipe.ingredients != None:
        recipe_ingredients = [ing.ingredient.to_mongo()
                            for ing in recipe.ingredients]
        recipe = recipe.to_mongo()
        for i in range(len(recipe_ingredients)):
            recipe['ingredients'][i]['ingredient'] = recipe_ingredients[i]
    return recipe


class RecipeList(Resource):
    @jwt_required
    @paginated
    @load_user_info
    def get(self, req_args, user_info: User):
        page = Recipe.objects(owner=str(user_info.id)).paginate(
            page=req_args['page'], per_page=req_args['per_page'])
        page.items = [_dereference_ingredients(item) for item in page.items]
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


class RecipeInstance(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, recipe_id=''):
        recipe = Recipe.objects(Q(id=recipe_id) & Q(
            owner=str(user_info.id))).get_or_404()

        return _dereference_ingredients(recipe)

    @jwt_required
    @load_user_info
    def delete(self, user_info: User, recipe_id=''):
        Recipe.objects(Q(id=recipe_id) & Q(
            owner=str(user_info.id))).get_or_404().delete()
        return "", 204

    @jwt_required
    @validate_payload(RecipeSchema(), 'new_recipe')
    @load_user_info
    def put(self, new_recipe: Recipe, user_info: User, recipe_id=''):
        old_recipe = Recipe.objects(Q(id=recipe_id) & Q(owner=str(user_info.id))).get_or_404()

        result = put_document(Recipe, new_recipe, old_recipe)

        if(result['n'] != 1):
            BadRequest(description='no matching recipe with id: {}'.format(recipe_id))
        
        old_recipe.reload()
        return old_recipe, 200

    @jwt_required
    @validate_payload(RecipeSchemaWithoutName(), 'new_recipe')
    @load_user_info
    def patch(self, new_recipe: Recipe, user_info: User, recipe_id=''):
        old_recipe = Recipe.objects(Q(id=recipe_id) & Q(owner=str(user_info.id))).get_or_404()

        result = patch_document(Recipe, new_recipe, old_recipe)

        if(result['n'] != 1):
            BadRequest(description='no matching recipe with id: {}'.format(recipe_id))
        
        old_recipe.reload()
        return old_recipe, 200

def _retrieve_base_recipe(recipe_id: str, user_id: str) -> Recipe:
    return Recipe.objects(Q(owner=user_id) & Q(id=recipe_id)).get_or_404()


class RecipeIngredientsList(Resource):
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