import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField, ObjectId
from mongoengine.queryset.visitor import Q

from .schemas import MenuRecipeSchema
from ...models import Recipe, Menu, User
from ... import validate_payload, paginated, mongo, load_user_info, put_document, patch_document
from ...exceptions import DuplicateEntry, BadRequest


def _retrieve_base_menu(menu_id: str, user_id: str) -> Recipe:
    return Recipe.objects(Q(owner=user_id) & Q(id=menu_id)).get_or_404()


class MenuRecipeList(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, menu_id=''):
        menu = _retrieve_base_menu(menu_id, str(user_info.id))
        return [menu_menu.to_mongo() for menu_menu in menu.recipes] if menu.recipes != None else []

    @jwt_required
    @validate_payload(MenuRecipeSchema(), 'menu_recipe')
    @load_user_info
    def post(self, menu_id, menu_recipe: Recipe, user_info: User):
        menu = _retrieve_base_menu(menu_id, str(user_info.id))
        menu.recipes.append(menu_recipe)
        menu.save()
        return menu_recipe, 201


class MenuRecipeInstance(Resource):
    @jwt_required
    @load_user_info
    def delete(self, user_info: User, menu_id='', ingredient_id=''):
        menu = _retrieve_base_menu(menu_id, str(user_info.id))
        
        if menu.recipes != None and len(menu.recipes) == 1:
            raise BadRequest('no recipes to delete for this menu')

        ingredient_id = ObjectId(ingredient_id)

        menu.recipes = [menu_menu for menu_menu in menu.recipes if menu_menu.ingredient.id != ingredient_id]

        menu.save()

        return "", 204
