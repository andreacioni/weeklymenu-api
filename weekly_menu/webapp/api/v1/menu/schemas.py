import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Menu

class MenuSchema(me.ModelSchema):
    class Meta:
        model = Menu