import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Ingredient
from ...schemas import BaseValidatorsMixin, DenyOfflineIdOverrideMixin

class IngredientSchema(me.ModelSchema, BaseValidatorsMixin):

    class Meta:
        model = Ingredient

class UpdateIngredientSchema(IngredientSchema, DenyOfflineIdOverrideMixin):

    #Overriding name property
    name = fields.String(required=False)
