from functools import wraps
from flask import request, jsonify, make_response
from json import dumps
from marshmallow_mongoengine import ModelSchema
from flask_restful import Api, reqparse
from flask_mongoengine import MongoEngine, DoesNotExist
from flask_jwt_extended import get_jwt_identity
from mongoengine.queryset.visitor import Q
from mongoengine.errors import ValidationError

from .exceptions import InvalidPayloadSupplied, BadRequest, Forbidden

API_PREFIX = '/api'

# Pagination
DEFAULT_PAGE_SIZE = 10

api = Api()

mongo = MongoEngine()


def create_module(app):

    mongo.init_app(app)

    from .v1 import create_module as create_api_v1

    create_api_v1(app, api)

    # Using workaround from here to handle inerith exception handling from flask: https://github.com/flask-restful/flask-restful/issues/280#issuecomment-280648790
    handle_exceptions = app.handle_exception
    handle_user_exception = app.handle_user_exception
    api.init_app(app)
    app.handle_user_exception = handle_exceptions
    app.handle_user_exception = handle_user_exception


@api.representation('application/json')
def output_json(data, code, headers=None):
    """
        NOTE: if a resource method is decorated with 'paginated' this method is not called
    """
    if isinstance(data, mongo.Document):
        data = data.to_mongo()
    
    resp = make_response(jsonify(data), code)
    resp.headers.extend(headers or {})
    return resp


def validate_payload(model_schema: ModelSchema, kwname='payload'):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data, errors = model_schema.load(request.get_json())

            if len(errors) != 0:
                raise InvalidPayloadSupplied(
                    'invalid payload supplied', errors)

            kwargs[kwname] = data

            return func(*args, **kwargs)
        return wrapper

    return decorate


def get_payload(kwname='payload'):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            kwargs[kwname] = data

            return func(*args, **kwargs)
        return wrapper

    return decorate


def load_user_info(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from .models import User
        try:
            user = User.objects(Q(username=get_jwt_identity())).get()
        except DoesNotExist:
            raise Forbidden()

        kwargs['user_info'] = user

        return func(*args, **kwargs)
    return wrapper


def paginated(func):
    pagination_reqparse = reqparse.RequestParser()
    pagination_reqparse.add_argument(
        'page',
        type=int,
        location=['args'],
        required=False,
        default=1
    )
    pagination_reqparse.add_argument(
        'per_page',
        type=int,
        location=['args'],
        required=False,
        default=DEFAULT_PAGE_SIZE
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        page_args = pagination_reqparse.parse_args()
        page = page_args['page']
        per_page = page_args['per_page']

        if page <= 0:
            raise BadRequest('page argument must be greater than zero')

        if per_page <= 0:
            raise BadRequest('per_page argument must be greater than zero')

        kwargs['req_args'] = {
            'page': page,
            'per_page': per_page
        }

        page = func(*args, **kwargs)

        return jsonify({
            #"results": page.items,
            "results": [item.to_mongo() if isinstance(item, mongo.Document) else item for item in page.items],
            "pages": page.pages
        })

    return wrapper

def _update_embedded_document(new_doc: mongo.EmbeddedDocument, old_doc: mongo.EmbeddedDocument, patch=True):
    if patch == True:
        for field in new_doc.__class__._fields:
            if new_doc[field] != None:
                old_doc[field] = new_doc[field]
        return old_doc
    else:
        return new_doc

def _update_document(coll_class: mongo.Document.__class__, new_doc: mongo.Document, old_doc: mongo.Document, patch=True):
    # Remove generated id and link new doc with current owner
    new_doc.id = None
    new_doc.owner = old_doc.owner

    if patch == True:
        return coll_class._get_collection().update(
            {'_id': old_doc.id}, {'$set': new_doc.to_mongo()})
    else:
        return coll_class._get_collection().update(
            {'_id': old_doc.id}, new_doc.to_mongo())


def put_document(coll_class: mongo.Document.__class__, new_doc: mongo.Document, old_doc: mongo.Document):
    return _update_document(coll_class, new_doc, old_doc, patch=False)


def patch_document(coll_class: mongo.Document.__class__, new_doc: mongo.Document, old_doc: mongo.Document):
    return _update_document(coll_class, new_doc, old_doc, patch=True)

def put_embedded_document(new_doc: mongo.EmbeddedDocument, old_doc: mongo.EmbeddedDocument):
    return _update_embedded_document(new_doc, old_doc, patch=False)

def patch_embedded_document(new_doc: mongo.EmbeddedDocument, old_doc: mongo.EmbeddedDocument):
    return _update_embedded_document(new_doc, old_doc, patch=True)
