import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import ShoppingList, ShoppingListItem
from ...exceptions import CannotUpdateResourceOwner
from ...schemas import BaseValidatorsMixin, CheckUnknownFieldsMixin

class ShoppingListSchema(me.ModelSchema, BaseValidatorsMixin):

    class Meta:
        model = ShoppingList
class PutShoppingListSchema(ShoppingListSchema):

    offline_id = fields.String(required=False)

class PatchShoppingListSchema(PutShoppingListSchema):

    #Overriding name property
    name = fields.String(required=False)

class ShoppingListItemSchema(me.ModelSchema, CheckUnknownFieldsMixin):
    
    class Meta:
        model = ShoppingListItem

class ShoppingListItemWithoutRequiredItemSchema(ShoppingListItemSchema):
    item = fields.String(required=False)