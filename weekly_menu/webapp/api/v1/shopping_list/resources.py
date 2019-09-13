import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.queryset.visitor import Q

from .schemas import ShoppingListSchema, ShoppingListItemSchema
from ...models import ShoppingList, ShoppingListItem, User
from ... import validate_payload, paginated, mongo, update_document, laod_user_info
from ...exceptions import DuplicateEntry, BadRequest, Forbidden, Conflict

class ShoppingListResource(Resource):
    @jwt_required
    @laod_user_info
    def get(self, user_info: User, shopping_list_id: str):        
        if (str(user_info.shopping_list_doc.id) != shopping_list_id):
            raise Forbidden()

        return user_info.shopping_list_doc, 200

class ShoppingListItemsResource(Resource):
    @jwt_required
    @laod_user_info
    @validate_payload(ShoppingListItemSchema(), 'shopping_list_item')
    def post(self, user_info: User, shopping_list_id: str, shopping_list_item: ShoppingListItem):        
        if (str(user_info.shopping_list_doc.id) != shopping_list_id):
            raise Forbidden()

        current_ingredients_in_list = [str(item.ingredient.id) for item in user_info.shopping_list_doc.items]

        if str(shopping_list_item.ingredient.id) in current_ingredients_in_list:
            raise Conflict('ingredient already present inside shopping list')

        user_info.shopping_list_doc.items.append(shopping_list_item)
        user_info.shopping_list_doc.save()

        return user_info.shopping_list_doc, 200