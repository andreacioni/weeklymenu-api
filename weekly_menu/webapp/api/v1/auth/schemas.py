import marshmallow_mongoengine as me

from ... import mongo

from ...models import User

class UserSchema(me.ModelSchema):
    class Meta:
        model = User