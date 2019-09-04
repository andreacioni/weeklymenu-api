import pprint

from flask import jsonify
from flask_restful import Resource, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField

from .schemas import UserSchema
from ...models import User
from ... import validate_payload, paginated, mongo, update_document
from ...exceptions import DuplicateEntry, BadRequest

class UserInstance(Resource):
    @jwt_required
    def get(self, user_id: str):
        if user_id == 'me':
            return User.objects(username=get_jwt_identity()).get_or_404()
        else:
            raise BadRequest()
