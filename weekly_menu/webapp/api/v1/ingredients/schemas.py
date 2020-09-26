import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Ingredient
from ...schemas import BaseValidatorsMixin

class IngredientSchema(me.ModelSchema, BaseValidatorsMixin):

    class Meta:
        model = Ingredient

class IngredientSchemaWithoutName(IngredientSchema):

    #Overriding name property
    name = fields.String(required=False)
