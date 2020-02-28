import os
import logging
import traceback

from flask import Flask, request, jsonify, json
from werkzeug.exceptions import NotFound, MethodNotAllowed
from mongoengine.fields import ObjectId, DateField, Binary
from mongoengine.errors import ValidationError
from datetime import datetime

from .api.exceptions import BaseRESTException

_logger = logging.getLogger(__name__)

class ObjectIdJSONEncoder(json.JSONEncoder): 
    def default(self, o): # pylint: disable=E0202
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, Binary):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)

app.json_encoder = ObjectIdJSONEncoder

def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app.config.from_object('configs.' + object_name)

    from .api import create_module as create_api_module

    create_api_module(app)

    return app

@app.before_request
def before_request():
    if ((request.data != b'') and (not request.is_json)):
        return jsonify({'msg': 'payload does not contains json data'}), 400

@app.errorhandler(Exception)
def handle_generic_exception(e: Exception):
        print(traceback.format_exc())
        if len(e.args) > 0:
          e = BaseRESTException(description=e.args[0], details=e.args[1:])
        else:
          e = BaseRESTException()
        return jsonify({
            'error': e.error,
            'descritpion': e.description,
            'details': e.details
        }), e.code

@app.errorhandler(BaseRESTException)
def handle_rest_exception(e: BaseRESTException):
    return jsonify({
            'error': e.error,
            'descritpion': e.description,
            'details': e.details
    }), e.code

@app.errorhandler(NotFound)
def handle_notfound(e):
        return jsonify({
            'error': 'NOT_FOUND',
            'descritpion': 'resource was not found on this server',
            'details': []
    }), 404

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(e):
        return jsonify({
            'error': 'METHOD_NOT_ALLOWED',
            'descritpion': 'method not allowed on selected resource',
            'details': []
    }), 405

@app.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError):
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'descritpion': e.message,
            'details': [{err : e.errors[err][1].message} for err in (e.errors or [])]
    }), 400