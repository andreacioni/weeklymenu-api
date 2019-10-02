import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Recipe

class RecipeSchema(me.ModelSchema):

    #Overriding owner property
    owner = fields.String(required=False)

    class Meta:
        model = Recipe