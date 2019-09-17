import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField
from mongoengine.queryset.visitor import Q

from .schemas import MenuSchema
from ...models import Ingredient, User, menu, ShoppingList, Menu
from ... import validate_payload, paginated, mongo, update_document, load_user_info
from ...exceptions import DuplicateEntry, BadRequest

class MenuList(Resource):
    @jwt_required
    @paginated
    @load_user_info
    def get(self, req_args, user_info: User):
        page = Menu.objects(user=user_info).paginate(page=req_args['page'], per_page=req_args['per_page'])
        return page
    
    @jwt_required
    @validate_payload(MenuSchema(), 'menu')
    @load_user_info
    def post(self, menu: Menu, user_info: User):
        try:
            menu.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for a menu", details=nue.args or [])
        
        return menu, 201

class MenuInstance(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, menu_id=''):
        return Menu.objects(Q(user=user_info) & Q(id=menu_id)).get_or_404()
    
    @jwt_required
    @load_user_info
    def delete(self, user_info: User, menu_id=''):
        Menu.objects(Q(user=user_info) & Q(id=menu_id)).get_or_404().delete()
        return "", 204
    
    @jwt_required
    @validate_payload(MenuSchema(), 'new_menu')
    @load_user_info
    def patch(self, new_menu: Ingredient, user_info: User, menu_id=''):
        if menu_id != None:
            old_menu = Menu.objects(Q(user=user_info) & Q(id=menu_id)).get_or_404()
            new_menu = update_document(old_menu, new_menu)
            return new_menu, 200
