import marshmallow_mongoengine as me

from marshmallow import Schema, fields

from ... import mongo
from ...models import User

class UserSchema(me.ModelSchema):
    class Meta:
        model = User

class PostGetSchema(Schema):
    username = fields.String()
    password = fields.String()