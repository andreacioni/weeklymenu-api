import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from conftest import TEST_USERNAME, TEST_PASSWORD, TEST_EMAIL

def test_bad_request_registration(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={})

  assert response.status_code == 400

  response = client.post('/api/v1/auth/register', json={'username':'a'})

  assert response.status_code == 400

def test_user_creation(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={
    'username':TEST_USERNAME + "a", 
    'password':TEST_PASSWORD,
    'email':TEST_EMAIL
    })

  assert response.status_code == 200

  response = client.post('/api/v1/auth/token', json={
    'username':TEST_USERNAME + "a", 
    'password':'wrong-password'
  })

  assert response.status_code == 401

  response = client.post('/api/v1/auth/token', json={
    'username':TEST_USERNAME + "a", 
    'password':TEST_PASSWORD
  })

  assert response.status_code == 200 and response.json['access_token'] is not None
