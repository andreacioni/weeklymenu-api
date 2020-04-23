import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import NotUniqueError
from mongoengine.queryset.visitor import Q
from bson import ObjectId

from .schemas import ShoppingListSchema, ShoppingListItemSchema, ShoppingListItemWithoutRequiredItemSchema, ShoppingListItemWithoutRequiredItemSchema
from ...models import ShoppingList, ShoppingListItem, User
from ... import validate_payload, paginated, mongo, load_user_info, put_embedded_document, patch_embedded_document, put_document, patch_document
from ...exceptions import DuplicateEntry, BadRequest, Forbidden, Conflict, NotFound

def _dereference_item(shopping_list: ShoppingListItem):
    if shopping_list.items != None:
        shopping_list_items = [item.item.to_mongo()
                            for item in shopping_list.items]
        shopping_list = shopping_list.to_mongo()
        for i in range(len(shopping_list_items)):
            shopping_list['items'][i]['item'] = shopping_list_items[i]
    return shopping_list

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
        
        try:
            shopping_list.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(
                description="duplicate entry found for a shopping list", details=nue.args or [])

        return shopping_list, 201

class UserShoppingList(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, shopping_list_id: str): 
        shopping_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).get_or_404()

        #return _dereference_item(shopping_list)
        return shopping_list

    @jwt_required
    @load_user_info
    def delete(self, user_info: User, shopping_list_id=''):
        ShoppingList.objects(Q(id=shopping_list_id) & Q(
            owner=str(user_info.id))).get_or_404().delete()
        return "", 204

    @jwt_required
    @validate_payload(ShoppingListSchema(), 'new_list')
    @load_user_info
    def put(self, new_list: ShoppingList, user_info: User, shopping_list_id=''):
        old_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).get_or_404()

        result = put_document(ShoppingList, new_list, old_list)

        if(result['n'] != 1):
            raise BadRequest(description='no matching shopping list with id: {}'.format(shopping_list_id))
        
        old_list.reload()
        return old_list, 200
    
    @jwt_required
    @validate_payload(ShoppingListSchema(), 'new_list')
    @load_user_info
    def patch(self, new_list: ShoppingList, user_info: User, shopping_list_id=''):
        old_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).get_or_404()

        result = patch_document(ShoppingList, new_list, old_list)

        if(result['n'] != 1):
            raise BadRequest(description='no matching shopping list with id: {}'.format(shopping_list_id))
        
        old_list.reload()
        return old_list, 200

def _retrieve_base_shopping_list(shopping_list_id: str, user_id: str) -> ShoppingList:
    return ShoppingList.objects(Q(owner=user_id) & Q(id=shopping_list_id)).get_or_404()

class UserShoppingListItems(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, shopping_list_id=''):
        shopping_list = _retrieve_base_shopping_list(shopping_list_id, str(user_info.id))
        return [shopping_list.to_mongo() for shopping_list in shopping_list.ingredients] if shopping_list.ingredients != None else []

    @jwt_required
    @load_user_info
    @validate_payload(ShoppingListItemSchema(), 'shopping_list_item')
    def post(self, user_info: User, shopping_list_id: str, shopping_list_item: ShoppingListItem):        
        shopping_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).get_or_404()

        # NOTE Check if an ingredient is already present in a specific list
        current_ingredients_in_list = [str(it.item.id) for it in shopping_list.items]
        if str(shopping_list_item.item.id) in current_ingredients_in_list:
            raise Conflict('ingredient already present inside shopping list')

        shopping_list.items.append(shopping_list_item)
        shopping_list.save()

        return shopping_list, 201
    
class UserShoppingListItem(Resource):

    @jwt_required
    @load_user_info
    def get(self, user_info: User, shopping_list_id: str, shopping_list_item_id: str):

        base_shopping_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id)) & Q(items__item=shopping_list_item_id)).get_or_404()

        for item_doc in base_shopping_list.items:
            if str(item_doc.item.id) == shopping_list_item_id:
                return item_doc, 200


        raise NotFound(description='can\'t find ingredient with id {} in list {}'.format(shopping_list_id, shopping_list_item_id))

    @jwt_required
    @load_user_info
    @validate_payload(ShoppingListItemWithoutRequiredItemSchema(), 'shopping_list_item')
    def patch(self, user_info: User, shopping_list_id: str, shopping_list_item_id: str, shopping_list_item: ShoppingListItem):

        # NOTE An item could be changed
        #if shopping_list_item.item != None and shopping_list_item_id != str(shopping_list_item.item.id):
        #    raise Conflict("can't update item {} with different item {}".format(str(shopping_list_item.item.id), shopping_list_item_id))

        base_shopping_list = ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id)) & Q(items__item=shopping_list_item_id)).get_or_404()

        for item_doc in base_shopping_list.items:
            if str(item_doc.item.id) == shopping_list_item_id:
                shopping_list_item = item_doc = patch_embedded_document(shopping_list_item, item_doc)
                break

        base_shopping_list.save()

        return shopping_list_item, 200

    @jwt_required
    @load_user_info
    @validate_payload(ShoppingListItemSchema(), 'shopping_list_item')
    def put(self, user_info: User, shopping_list_id: str, shopping_list_item_id: str, shopping_list_item: ShoppingListItem):

        # NOTE An item could be changed
        #if shopping_list_item.item != None and shopping_list_item_id != str(shopping_list_item.item.id):
        #    raise Conflict("can't update item {} with different item {}".format(str(shopping_list_item.item.id), shopping_list_item_id))

        ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id)) & Q(items__item=shopping_list_item_id)).update(set__items__S=shopping_list_item)

        return shopping_list_item, 200

    @jwt_required
    @load_user_info
    def delete(self, user_info: User, shopping_list_id: str, shopping_list_item_id: str):
        ShoppingList.objects(Q(id=shopping_list_id) & Q(owner=str(user_info.id))).update(pull__items__item=ObjectId(shopping_list_item_id))

        return '', 204
