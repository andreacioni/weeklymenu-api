import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient

def create_recipe(client, json, auth_headers):
  return client.post('/api/v1/recipes', json=json, headers=auth_headers)

def patch_recipe(client, recipe_id, json, auth_headers):
  return client.patch('/api/v1/recipes/{}'.format(recipe_id), json=json, headers=auth_headers)

def put_recipe(client, recipe_id, json, auth_headers):
  return client.put('/api/v1/recipes/{}'.format(recipe_id), json=json, headers=auth_headers)

def replace_recipe(client, recipe_id, json, auth_headers):
  return client.put('/api/v1/recipes/{}'.format(recipe_id), json=json, headers=auth_headers)

def get_recipe(client, recipe_id, auth_headers):
  return client.get('/api/v1/recipes/{}'.format(recipe_id), headers=auth_headers)

def get_all_recipes(client, auth_headers, page=1, per_page=10):
  return client.get('/api/v1/recipes?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def test_not_authorized(client: FlaskClient):
  response = get_all_recipes(client, {})
  
  assert response.status_code == 401

def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_recipe(client, {
        'name': 'Menu',
        'id': '5e4ae04561fe8235a5a18824'
    }, auth_headers)

    assert response.status_code == 403

    response = patch_recipe(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Menu',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403

    response = put_recipe(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Menu',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403

def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

    response = create_recipe(client, {
        'name': 'ham',
        'owner': 'pippo'
    }, auth_headers)

    assert response.status_code == 403

def test_owner_update(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'ham'
    }, auth_headers)

    recipe_id = response.json['_id']['$oid']

    # Try to update owner using an integer instead of a string
    response = patch_recipe(client, response.json['_id']['$oid'], {
        'owner': 1
    }, auth_headers)

    assert response.status_code == 400

    # Try to update owner using a valid objectId (from recipe_id)
    response = patch_recipe(client, recipe_id, {
        'owner': recipe_id
    }, auth_headers)

    assert response.status_code == 403

def test_create_recipe(client: FlaskClient, auth_headers):
  response = get_all_recipes(client, auth_headers)

  assert response.status_code == 200 and len(response.json['results']) == 0 and response.json['pages'] == 0

  tuna_resp = create_ingredient(client, {
    'name' : 'Tuna'
  }, auth_headers)

  tomato_resp = create_ingredient(client, {
    'name' : 'Tomatoes'
  }, auth_headers)

  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'ingredients' : [
      {
      'ingredient': tuna_resp.json['_id']['$oid']
      },{
      'ingredient': tomato_resp.json['_id']['$oid']
      }
    ]
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'Tuna and tomatoes'

  # Test fail duplicating ingredient
  #response = create_recipe(client, {
  #  'name': 'Tuna and tomatoes'
  #} , auth_headers)

  #assert response.status_code == 409

  response = create_recipe(client, {
    'name': 'Pizza'
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'Pizza'

  #Check pagination 
  response = get_all_recipes(client, auth_headers, 1, 1)

  assert response.status_code == 200 and response.json['pages'] == 2

def test_replace_recipe(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 2
  } , auth_headers)

  assert response.status_code == 201 and response.json['servs'] == 2

  response = replace_recipe(client, response.json['_id']['$oid'], {
    'name': 'Tuna and tomatoes',
    'servs': 3
  }, auth_headers)
  
  assert response.status_code == 200 and response.json['servs'] == 3

def test_duplicate_recipe_allowed(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 2
  } , auth_headers)

  assert response.status_code == 201

  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 3
  }, auth_headers)
  
  assert response.status_code == 201

  response = get_all_recipes(client, auth_headers)

  assert response.status_code == 200 and len(response.json['results']) == 2 and response.json['pages'] == 1





