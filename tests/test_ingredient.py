import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

def create_ingredient(client, json, auth_headers):
  return client.post('/api/v1/ingredients', json=json, headers=auth_headers)

def update_ingredient(client, ing_id, json, auth_headers):
  return client.patch('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)

def delete_ingredient(client, ing_id, auth_headers):
  return client.delete('/api/v1/ingredients/{}'.format(ing_id), headers=auth_headers)

def get_all_ingredients(client, auth_headers, page=1, per_page=10):
  return client.get('/api/v1/ingredients?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def test_not_authorized(client: FlaskClient):
  response = get_all_ingredients(client, {})
  
  assert response.status_code == 401

def test_create_ingredient(client: FlaskClient, auth_headers):
  response = get_all_ingredients(client, auth_headers)

  assert response.status_code == 200 and len(response.json['results']) == 0 and response.json['pages'] == 0

  response = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'ham' and response.json['freezed'] == False

  # Test fail duplicating ingredient
  response = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers)

  assert response.status_code == 409

  response = create_ingredient(client, {
    'name': 'cheese',
    'freezed': True
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'cheese' and response.json['freezed'] == True

  #Check pagination 
  response = get_all_ingredients(client, auth_headers, 1, 1)

  assert response.status_code == 200 and response.json['pages'] == 2

  #Remove one ingredient
  response = delete_ingredient(client, response.json['results'][0]['_id']['$oid'], auth_headers)

  assert response.status_code == 204

  response = get_all_ingredients(client, auth_headers)

  assert response.status_code == 200 and response.json['pages'] == 1 and len(response.json['results']) == 1

def test_update_ingredient(client: FlaskClient, auth_headers):
  response = create_ingredient(client, {
    'name': 'Tuna',
    'description': 'this is a tuna'
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'Tuna' and response.json['description'] == 'this is a tuna'

  response = update_ingredient(client, response.json['_id']['$oid'], {
    'name': 'Tuna',
    'description': 'always a tuna',
    'note': 'note about tuna'
  }, auth_headers)
  
  assert response.status_code == 200 and response.json['description'] == 'always a tuna' and response.json['note'] == 'note about tuna'

def test_duplicate_ingredient_not_allowed(client: FlaskClient, auth_headers):
  response = create_ingredient(client, {
    'name': 'Tuna',
    'description': 'this is a tuna'
  } , auth_headers)

  assert response.status_code == 201

  response = create_ingredient(client, {
    'name': 'Tuna',
    'description': 'always a tuna',
    'note': 'note about tuna'
  }, auth_headers)
  
  assert response.status_code == 409
  
def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):
  
  response = create_ingredient(client, {
    'name': 'Garlic',
    'owner': '123abc'
  }, auth_headers)

  assert response.status_code == 201 and str(response.json['owner']) != '123abc'