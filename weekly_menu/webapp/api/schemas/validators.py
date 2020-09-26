from marshmallow import fields, Schema, validates_schema, ValidationError

from ..exceptions import CannotUpdateResourceOwner, CannotSetResourceId

class OwnerNotRequiredMixin:
  # Owner is not required because it will be attached server side based on token
  owner = fields.String(required=False)

class CheckUnknownFieldsMixin:
  @validates_schema(pass_original=True)
  def check_unknown_fields(self, data, original_data):
      unknown = set(original_data) - set(self.fields)
      if unknown:
          raise ValidationError('Unknown field', unknown)

class DenyOwnerOverrideMixin:
  @validates_schema
  def check_owner_overwrite(self, data):
      if 'owner' in data:
          raise CannotUpdateResourceOwner('Can\'t overwrite owner property')

class DenyIdOverrideMixin:
  @validates_schema
  def id_not_allowed(self, data):
      if 'id' in data:
          raise CannotSetResourceId()

class DenyOfflineIdOverrideMixin:
  @validates_schema
  def offline_id_not_allowed(self, data):
      if 'offline_id' in data:
          raise CannotSetResourceId()

class BaseValidatorsMixin(OwnerNotRequiredMixin, CheckUnknownFieldsMixin, DenyIdOverrideMixin, DenyOwnerOverrideMixin):
    pass