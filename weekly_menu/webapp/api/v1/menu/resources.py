import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField
from mongoengine.queryset.visitor import Q

from .schemas import MenuSchema
from ...models import Ingredient, User, menu, ShoppingList, Menu
from ... import validate_payload, paginated, mongo, load_user_info, put_document, patch_document
from ...exceptions import DuplicateEntry, BadRequest

def _dereference_recipes(menu: Menu):
    if menu.recipes != None:
        menu_recipes = [recipe.to_mongo()
                            for recipe in menu.recipes]
        menu = menu.to_mongo()
        for i in range(len(menu_recipes)):
            menu['recipes'][i] = menu_recipes[i]
    return menu

class MenuList(Resource):
    @jwt_required
    @paginated
    @load_user_info
    def get(self, req_args, user_info: User):
        page = Menu.objects(owner=str(user_info.id)).paginate(
            page=req_args['page'], per_page=req_args['per_page'])
        page.items = [_dereference_recipes(item) for item in page.items]
        return page
    
    @jwt_required
    @validate_payload(MenuSchema(), 'menu')
    @load_user_info
    def post(self, menu: Menu, user_info: User):
        #Associate user id
        menu.owner = user_info.id
        
        try:
            menu.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for a menu", details=nue.args or [])
        
        return menu, 201

class MenuInstance(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, menu_id=''):
        menu = Menu.objects(Q(owner=str(user_info.id)) & Q(id=menu_id)).get_or_404()

        return _dereference_recipes(menu)
    
    @jwt_required
    @load_user_info
    def delete(self, user_info: User, menu_id=''):
        Menu.objects(Q(owner=str(user_info.id)) & Q(id=menu_id)).get_or_404().delete()
        return "", 204
    
    @jwt_required
    @validate_payload(MenuSchema(), 'new_menu')
    @load_user_info
    def put(self, new_menu: Ingredient, user_info: User, menu_id=''):
        old_menu = Menu.objects(Q(id=menu_id) & Q(owner=str(user_info.id))).get_or_404()

        result = put_document(Menu, new_menu, old_menu)

        if(result['n'] != 1):
            BadRequest(description='no matching menu with id: {}'.format(menu_id))
        
        old_menu.reload()
        return old_menu, 200

    @jwt_required
    @validate_payload(MenuSchema(), 'new_menu')
    @load_user_info
    def patch(self, new_menu: Menu, user_info: User, menu_id=''):
        old_menu = Menu.objects(Q(id=menu_id) & Q(owner=str(user_info.id))).get_or_404()

        result = patch_document(Menu, new_menu, old_menu)

        if(result['n'] != 1):
            BadRequest(description='no matching menu with id: {}'.format(menu_id))
        
        old_menu.reload()
        return old_menu, 200