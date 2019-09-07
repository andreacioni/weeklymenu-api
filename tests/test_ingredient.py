import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from weekly_menu.webapp import app

@pytest.fixture
def test_client():
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
 
    yield testing_client
 
    ctx.pop()

def test_simple(test_client: FlaskClient):
  assert True