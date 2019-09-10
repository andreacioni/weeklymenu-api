import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField
from mongoengine.queryset.visitor import Q

from .schemas import ShoppingListSchema, ShoppingListItemSchema
from ...models import ShoppingList, ShoppingListItem, User
from ... import validate_payload, paginated, mongo, update_document, laod_user_info
from ...exceptions import DuplicateEntry, BadRequest, Forbidden

class ShoppingListResource(Resource):
    @jwt_required
    @laod_user_info
    def get(self, user_info: User, shopping_list_id:str):
        if (user_info.shopping_list_doc.id != shopping_list_id):
            raise Forbidden()