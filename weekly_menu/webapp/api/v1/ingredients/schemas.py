import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import Ingredient


class IngredientSchema(me.ModelSchema):

    # Overriding owner property
    owner = fields.String(required=False)

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', unknown)

    class Meta:
        model = Ingredient
