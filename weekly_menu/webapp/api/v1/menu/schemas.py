import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import Menu

class MenuSchema(me.ModelSchema):

    #Overriding owner property
    owner = fields.String(required=False)

    #Overriding datetimefield
    date = fields.Date(required=True)

    class Meta:
        model = Menu