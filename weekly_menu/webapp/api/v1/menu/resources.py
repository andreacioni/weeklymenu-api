import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField
from mongoengine.queryset.visitor import Q

from .schemas import MenuSchema
from ...models import Ingredient, User, Recipe, ShoppingList, Menu
from ... import validate_payload, paginated, mongo, update_document, laod_user_info
from ...exceptions import DuplicateEntry, BadRequest

class MenuList(Resource):
    @jwt_required
    @paginated
    @laod_user_info
    def get(self, req_args, user_info: User):
        page = Menu.objects(user=user_info).paginate(page=req_args['page'], per_page=req_args['per_page'])
        return page
    
    @jwt_required
    @validate_payload(MenuSchema(), 'menu')
    @laod_user_info
    def post(self, menu: Menu, user_info: User):
        try:
            menu.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for a menu", details=nue.args or [])
        
        return menu, 201

class MenuInstance(Resource):
    @jwt_required
    @laod_user_info
    def get(self, user_info: User, menu_id=''):
        pass
    
    @jwt_required
    @laod_user_info
    def delete(self, user_info: User, menu_id=''):
        pass
    
    @jwt_required
    @validate_payload(MenuSchema(), 'new_menu')
    @laod_user_info
    def patch(self, new_menu: Ingredient, user_info: User, menu_id=''):
        pass
