import marshmallow_mongoengine as me

from marshmallow import Schema, fields, validates_schema, ValidationError

from ... import mongo
from ...models import DailyMenu
from ...exceptions import CannotUpdateResourceOwner
from ...schemas import BaseValidatorsMixin, DenyIdOverrideMixin


class DailyMenuSchema(me.ModelSchema, BaseValidatorsMixin):

    # Overriding datefield
    date = fields.Date(required=True)

    class Meta:
        model = DailyMenu


class PutMenuSchema(DailyMenuSchema):
    pass


class PatchMenuSchema(PutMenuSchema):
    date = fields.Date(required=False)
