import os

from flask import Flask

from flask_mongoengine import MongoEngine

app = Flask(__name__)
mongo = MongoEngine()

def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app.config.from_object(object_name)

    mongo.init_app(app)

    from .auth import create_module as auth_create_module
    from .api import create_module as api_create_module

    auth_create_module(app)
    api_create_module(app)

    return app  