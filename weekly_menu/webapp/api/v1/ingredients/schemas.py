import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Ingredient

class IngredientSchema(me.ModelSchema):
    
    #Overriding owner property
    owner = fields.String(required=False)

    class Meta:
        model = Ingredient