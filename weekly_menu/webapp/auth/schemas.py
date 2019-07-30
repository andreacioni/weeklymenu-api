from .. import mongo

from .models import User

class UserSchema(mongo.ModelSchema):
    class Meta:
        model = User