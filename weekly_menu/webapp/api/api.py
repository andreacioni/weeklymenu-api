import logging

from flask import Flask, render_template, send_file, Response
from flask_restful import Api, Resource, abort, request
from flask.testing import FlaskClient

from weekly_menu.db import get_client as mongodb
from .res import Ingredients

API_VERSION = 'v1'
API_PREFIX = '/api'
BASE_PATH = API_PREFIX + '/' + API_VERSION

logger = logging.getLogger(__name__)
app = None

def serve(host: str, port: int, debug=False):
    global app
    app = Flask(__name__)
    api = Api(app)

    #add resource endpoints
    add_resources(api)

    logging.info("Serving API (debug: %s)", debug)
    app.run(host=host, port=port, debug=debug)

def add_resources(api: Api):
    api.add_resource(Ingredients, BASE_PATH + '/ingredients')

def get_test_client() -> FlaskClient:
    """
        Only for test purpose
    """
    global app
    return app.test_client()

def get_context():
    """
        Only for test purpose
    """
    global app
    return app.app_context()

def shutdown():
    pass