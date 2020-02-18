import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import Menu, Recipe


class MenuSchema(me.ModelSchema):

    # Overriding owner property
    owner = fields.String(required=False)

    # Overriding datetimefield
    date = fields.Date(required=True)

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', unknown)

    class Meta:
        model = Menu

class MenuWithoutDateSchema(MenuSchema):

    date = fields.Date(required=False)

class MenuRecipeSchema(me.ModelSchema):

    class Meta:
        model = Recipe