import marshmallow_mongoengine as me

from marshmallow import Schema, fields
from marshmallow.validate import Length, Regexp, Range

from ... import mongo
from ...models import User

class PostUserTokenSchema(Schema):
    username = fields.String()
    password = fields.String()

class PostRegisterUserSchema(Schema):
    username = fields.Str(required=True, validate=Length(User.MIN_USERNAME_LENGTH,User.MAX_USERNAME_LENGTH))
    password = fields.Str(required=True, validate=Length(User.MIN_PASSWORD_LENGTH,User.MAX_PASSWORD_LENGTH))
    email = fields.Str(required=True, validate=Regexp(User.USER_EMAIL_REGEX))