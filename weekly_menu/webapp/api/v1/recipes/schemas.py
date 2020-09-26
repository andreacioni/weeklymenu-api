import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import Recipe, RecipeIngredient
from ...exceptions import CannotUpdateResourceOwner, CannotSetResourceId
from ...schemas import BaseValidatorsMixin

class RecipeSchema(me.ModelSchema, BaseValidatorsMixin):

    class Meta:
        model = Recipe

class RecipeSchemaWithoutName(RecipeSchema):

    #Overriding name property
    name = fields.String(required=False)

class RecipeIngredientSchema(me.ModelSchema):

    class Meta:
        model = RecipeIngredient

class RecipeIngredientWithoutRequiredIngredientSchema(RecipeIngredientSchema):
    ingredient = fields.String(required=False)