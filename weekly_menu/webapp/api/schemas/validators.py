from marshmallow import Schema, validates_schema, ValidationError

from ...exceptions import CannotUpdateResourceOwner, CannotSetResourceId


class SchemaValidators(Schema):

  # Owner is not required because it will be attached server side based on token
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