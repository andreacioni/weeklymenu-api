import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient

def create_shopping_list(client, json, auth_headers):
  return client.post('/api/v1/shopping-lists', json=json, headers=auth_headers)

def add_item_in_shopping_list(client, shopping_list_id, json, auth_headers):
  return client.post('/api/v1/shopping-lists/{}/item'.format(shopping_list_id), json=json, headers=auth_headers)

def get_shopping_list(client, shopping_list_id, auth_headers):
  return client.get('/api/v1/shopping-lists/{}'.format(shopping_list_id), headers=auth_headers)

def get_all_shopping_list(client, auth_headers, page=1, per_page=10):
  return client.get('/api/v1/shopping-lists?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def test_not_authorized(client: FlaskClient):
  response = get_all_shopping_list(client, {})
  
  assert response.status_code == 401

def test_shooping_list_pagination(client: FlaskClient, auth_headers):
  response = create_shopping_list(client, {
    'name' : 'list1'
  }, auth_headers)

  assert response.status_code == 201

  response = get_all_shopping_list(client, auth_headers)

  assert response.status_code == 200 and response.json['pages'] == 1 and len(response.json['results']) == 1

  response = create_shopping_list(client, {
    'name' : 'list2'
  }, auth_headers)

  assert response.status_code == 201

  response = get_all_shopping_list(client, auth_headers)

  assert response.status_code == 200 and response.json['pages'] == 1 and len(response.json['results']) == 2

def test_create_shopping_list(client: FlaskClient, auth_headers):

  ham = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers)

  tuna = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers)

  response = create_shopping_list(client, {
    'name' : 'list1',
    'items' : [
      {
        'ingredient'
      }
    ]
  }, auth_headers)

  assert response.status_code == 201

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
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes'
  } , auth_headers)

  assert response.status_code == 409

  response = create_recipe(client, {
    'name': 'Pizza'
  } , auth_headers)

  assert response.status_code == 201 and response.json['name'] == 'Pizza'

  #Check pagination 
  response = get_all_recipes(client, auth_headers, 1, 1)

  assert response.status_code == 200 and response.json['pages'] == 2

def test_update_recipe(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 2
  } , auth_headers)

  assert response.status_code == 201 and response.json['servs'] == 2

  response = update_recipe(client, response.json['_id']['$oid'], {
    'name': 'Tuna and tomatoes',
    'servs': 3
  }, auth_headers)
  
  assert response.status_code == 200 and response.json['servs'] == 3

def test_duplicate_recipe_not_allowed(client: FlaskClient, auth_headers):
  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 2
  } , auth_headers)

  assert response.status_code == 201

  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'servs': 3
  }, auth_headers)
  
  assert response.status_code == 409

def test_ingredient_remove_from_recipe(client: FlaskClient, auth_headers):
  tuna = create_ingredient(client, {
    'name' : 'Tuna'
  }, auth_headers).json

  tomatoes = create_ingredient(client, {
    'name' : 'Tomatoes'
  }, auth_headers).json

  response = create_recipe(client, {
    'name': 'Tuna and tomatoes',
    'ingredients' : [
      {
        'ingredient' : tuna['_id']['$oid']
      },{
        'ingredient' : tomatoes['_id']['$oid']
      }],
    'servs': 3
  }, auth_headers)

  assert response.status_code == 201 and len(response.json['ingredients']) == 2

  recipe = response.json

  delete_ingredient(client, tuna['_id']['$oid'], auth_headers)

  recipe = get_recipe(client, recipe['_id']['$oid'], auth_headers).json

  assert len(recipe['ingredients']) == 1

  delete_ingredient(client, tomatoes['_id']['$oid'], auth_headers)

  recipe = get_recipe(client, recipe['_id']['$oid'], auth_headers).json

  assert len(recipe['ingredients']) == 0


  





