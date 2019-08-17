import os
import logging

from flask import Flask, request, jsonify

from .api.exceptions import BaseRESTException

_logger = logging.getLogger(__name__)

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

@app.errorhandler(Exception)
def handle_generic_exception(e: Exception):
        _logger.error(e)
        e = BaseRESTException(description=e.args[0], details=e.args[1:])
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