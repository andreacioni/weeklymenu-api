import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import Menu, Recipe
from ...exceptions import CannotUpdateResourceOwner, CannotSetResourceId
from ...schemas import BaseValidatorsMixin, DenyOfflineIdOverrideMixin


class MenuSchema(me.ModelSchema, BaseValidatorsMixin):

    # Overriding datefield
    date = fields.Date(required=True)

    class Meta:
        model = Menu

class PutMenuSchema(MenuSchema, DenyOfflineIdOverrideMixin):

    offline_id = fields.String(required=False)

class PatchMenuSchema(PutMenuSchema):

    date = fields.Date(required=False)

class MenuRecipeSchema(Schema):

    recipe_id = fields.String()

