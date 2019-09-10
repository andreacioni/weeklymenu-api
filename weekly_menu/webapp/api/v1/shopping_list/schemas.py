import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import ShoppingList, ShoppingListItem

class ShoppingListSchema(me.ModelSchema):
    class Meta:
        model = ShoppingList

class ShoppingListItemSchema(me.ModelSchema):
    class Meta:
        model = ShoppingListItem