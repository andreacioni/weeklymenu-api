import logging

from flask import Flask, render_template, send_file, Response
from flask_restful import Api, Resource, abort, request

API_PREFIX = '/api'

class WeeklyMenuAPI(object):
    _logger = logging.getLogger(__name__)
    _app = Flask(__name__)

    def __init__(self, host: str, port: int, debug=False):
        self._host = host
        self._port = port
        self._debug = debug

        self._app = Flask(__name__)
        self._api = Api(self._app)




