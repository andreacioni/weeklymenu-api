import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import Ingredient
from ...exceptions import CannotUpdateResourceOwner, CannotSetResourceId


class IngredientSchema(me.ModelSchema):

    # Overriding owner property
    owner = fields.String(required=False)

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', unknown)

    @validates_schema
    def check_owner_overwrite(self, data):
        if 'owner' in data:
            raise CannotUpdateResourceOwner('Can\'t overwrite owner property')

    @validates_schema
    def id_not_allowed(self, data):
        if 'id' in data:
            raise CannotSetResourceId()

    class Meta:
        model = Ingredient

class IngredientSchemaWithoutName(IngredientSchema):

    #Overriding name property
    name = fields.String(required=False)
