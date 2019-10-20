import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.queryset.visitor import Q

from .schemas import ShoppingListSchema, ShoppingListItemSchema
from ...models import ShoppingList, ShoppingListItem, User
from ... import validate_payload, paginated, mongo, update_document, load_user_info
from ...exceptions import DuplicateEntry, BadRequest, Forbidden, Conflict

class UserShoppingLists(Resource):
    @jwt_required
    @paginated
    @load_user_info
    def get(self, req_args, user_info: User): 
        return ShoppingList.objects(owner=str(user_info.id)).paginate(page=req_args['page'], per_page=req_args['per_page'])

    @jwt_required
    @load_user_info
    @validate_payload(ShoppingListSchema(), 'shopping_list')
    def post(self, user_info: User, shopping_list: ShoppingList): 
        #Associate user id
        shopping_list.owner = user_info.id
        
        shopping_list.save()

        return shopping_list, 201

class UserShoppingList(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, shopping_list_id: str): 
        return ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).get_or_404(), 200

class UserShoppingListItems(Resource):
    @jwt_required
    @load_user_info
    @validate_payload(ShoppingListItemSchema(), 'shopping_list_item')
    def post(self, user_info: User, shopping_list_id: str, shopping_list_item: ShoppingListItem):        
        shopping_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).get_or_404()

        current_ingredients_in_list = [str(item.ingredient.id) for item in shopping_list.items]

        if str(shopping_list_item.ingredient.id) in current_ingredients_in_list:
            raise Conflict('ingredient already present inside shopping list')

        shopping_list.items.append(shopping_list_item)
        shopping_list.save()

        return shopping_list, 200
    
class UserShoppingListItem(Resource):
    @jwt_required
    @load_user_info
    @validate_payload(ShoppingListItemSchema(), 'shopping_list_item')
    def put(self, user_info: User, shopping_list_id: str, shopping_list_item_id: str, shopping_list_item: ShoppingListItem):

        if shopping_list_item_id != str(shopping_list_item.item.id):
            raise Conflict("can't update item {} with different item {}".format(str(shopping_list_item.item.id), shopping_list_item_id))

        ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id)) & Q(items__item=shopping_list_item_id)).update(set__items__S=shopping_list_item)

        return '', 204
