import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Recipe

class MenuRecipeSchema(me.ModelSchema):

    class Meta:
        model = Recipe