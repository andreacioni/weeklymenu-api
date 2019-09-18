import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

def test_bad_request_registration(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={})

  assert response.status_code == 400

  response = client.post('/api/v1/auth/register', json={'username':'a'})

  assert response.status_code == 400