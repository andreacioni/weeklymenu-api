import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import RecipeIngredient

class RecipeIngredientSchema(me.ModelSchema):

    class Meta:
        model = RecipeIngredient