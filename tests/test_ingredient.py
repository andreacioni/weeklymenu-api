import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

def test_not_authorized(client: FlaskClient):
  response = client.get('/api/v1/ingredients')
  
  assert response.status_code == 401

def test_create_ingredient(client: FlaskClient, auth_headers):
  response = client.get('/api/v1/ingredients', headers=auth_headers)

  assert response.status_code == 200 and len(response.json['results']) == 0

