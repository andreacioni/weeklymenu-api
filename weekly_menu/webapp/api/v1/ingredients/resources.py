import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField
from mongoengine.queryset.visitor import Q

from .schemas import IngredientSchema
from ...models import Ingredient, User, Recipe, ShoppingList
from ... import validate_payload, paginated, mongo, update_document, load_user_info
from ...exceptions import DuplicateEntry, BadRequest

class IngredientsList(Resource):
    @jwt_required
    @paginated
    @load_user_info
    def get(self, req_args, user_info: User):
        page = Ingredient.objects(owner=str(user_info.id)).paginate(page=req_args['page'], per_page=req_args['per_page'])
        return page
    
    @jwt_required
    @validate_payload(IngredientSchema(), 'ingredient')
    @load_user_info
    def post(self, ingredient: Ingredient, user_info: User):

        #Associate user id
        ingredient.owner = user_info.id

        try:
            ingredient.save()
        except NotUniqueError as nue:
            raise DuplicateEntry(description="duplicate entry found for an ingredient", details=nue.args or [])
        
        return ingredient, 201

class IngredientInstance(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, ingredient_id=''):
        if ingredient_id != None:
            return Ingredient.objects(Q(id=ingredient_id) & Q(owner=str(user_info.id))).get_or_404()
    
    @jwt_required
    @load_user_info
    def delete(self, user_info: User, ingredient_id=''):
        if ingredient_id != None:
            ingredient = Ingredient.objects(Q(id=ingredient_id) & Q(owner=str(user_info.id))).get_or_404()

            #Removing references in embedded documents is not automatic (see: https://github.com/MongoEngine/mongoengine/issues/1592)
            Recipe.objects(owner=user_info.id).update(pull__ingredients__ingredient=ingredient.id)
            ShoppingList.objects(owner=user_info.id).update(pull__items__ingredient=ingredient.id)

            ingredient.delete()

            return "", 204
    
    @jwt_required
    @validate_payload(IngredientSchema(), 'new_ingredient')
    @load_user_info
    def patch(self, new_ingredient: Ingredient, user_info: User, ingredient_id=''):
        if ingredient_id != None:
            old_ingredient = Ingredient.objects(Q(id=ingredient_id) & Q(owner=str(user_info.id))).get_or_404()
            new_ingredient = update_document(old_ingredient, new_ingredient)
            return new_ingredient, 200
