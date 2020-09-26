import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import Menu, Recipe
from ...exceptions import CannotUpdateResourceOwner, CannotSetResourceId
from ...schemas import BaseValidatorsMixin


class MenuSchema(me.ModelSchema, BaseValidatorsMixin):

    # Overriding datetimefield
    date = fields.Date(required=True)

    class Meta:
        model = Menu

class MenuWithoutDateSchema(MenuSchema):

    date = fields.Date(required=False)

class MenuRecipeSchema(Schema):

    recipe_id = fields.String()

