import os

from flask import Flask, request, jsonify
from mongoengine.errors import NotUniqueError

from .api.exceptions import BaseRESTException


app = Flask(__name__)

def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app.config.from_object(object_name)

    from .api import create_module as create_api_module

    create_api_module(app)

    return app

@app.before_request
def before_request():
    if ((request.data != b'') and (not request.is_json)):
        return jsonify({'msg': 'payload does not contains json data'}), 400


@app.errorhandler(BaseRESTException)
def handle_rest_exception(error: BaseRESTException):
    return jsonify({
            'error': error.error,
            'descritpion': error.description,
            'details': error.details
    }), error.code