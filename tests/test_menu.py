import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient
from test_recipe import create_recipe

def create_menu(client, json, auth_headers):
  return client.post('/api/v1/menus', json=json, headers=auth_headers)

def update_menu(client, menu_id, json, auth_headers):
  return client.patch('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)

def get_menu(client, menu_id, auth_headers):
  return client.get('/api/v1/menus/{}'.format(menu_id), headers=auth_headers)

def get_all_menus(client, auth_headers, page=1, per_page=10):
  return client.get('/api/v1/menus?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def test_not_authorized(client: FlaskClient):
  response = get_all_menus(client, {})
  
  assert response.status_code == 401

def test_menu_date_required(client: FlaskClient, auth_headers):
  response = create_menu(client, {
    'name' : 'Menu1'
  }, auth_headers)
  
  assert response.status_code == 400 and response.json['error'] == 'BAD_REQUEST'

  response = create_menu(client, {
    'name' : 'Menu1',
    'date' : '2019-12-13'
  }, auth_headers)
  
  assert response.status_code == 201

def test_menu_pagination(client: FlaskClient, auth_headers):
  response = create_menu(client, {
    'name' : 'Menu1',
    'date' : '2019-12-13'
  }, auth_headers)

  assert response.status_code == 201

  response = get_all_menus(client, auth_headers)

  assert response.status_code == 200 and response.json['pages'] == 1 and len(response.json['results']) == 1

  response = create_menu(client, {
    'name' : 'list2',
    'date' : '2019-12-13'
  }, auth_headers)

  assert response.status_code == 201

  response = get_all_menus(client, auth_headers)

  assert response.status_code == 200 and response.json['pages'] == 1 and len(response.json['results']) == 2

def test_create_menu(client: FlaskClient, auth_headers):

  ham = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers).json

  tuna = create_ingredient(client, {
    'name': 'tuna'
  } , auth_headers).json

  response = create_recipe(client, {
    'name' : 'Tuna And Ham',
    'ingredients' : [
      {
        'ingredient' : ham['_id']['$oid']
      }, {
        'ingredient' : tuna['_id']['$oid']
      }
    ]
  }, auth_headers)

  assert response.status_code == 201

def test_update_menu(client: FlaskClient, auth_headers):
  ham = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers).json

  tuna = create_ingredient(client, {
    'name': 'tuna'
  } , auth_headers).json

  cheese = create_ingredient(client, {
    'name': 'cheese'
  } , auth_headers).json

  tuna_and_ham = create_recipe(client, {
    'name' : 'Tuna And Ham',
    'ingredients' : [
      {
        'ingredient' : ham['_id']['$oid']
      }, {
        'ingredient' : tuna['_id']['$oid']
      }
    ]
  }, auth_headers).json

  ham_and_cheese = create_recipe(client, {
    'name' : 'Ham And Cheese',
    'ingredients' : [
      {
        'ingredient' : ham['_id']['$oid']
      }, {
        'ingredient' : cheese['_id']['$oid']
      }
    ]
  }, auth_headers).json

  shop_list = create_menu(client, {
    'name' : 'Menu 1',
    'date' : '2019-10-11',
    'recipes' : [
      tuna_and_ham['_id']['$oid'],
      ham_and_cheese['_id']['$oid']
    ]
  }, auth_headers).json

  assert len(shop_list['recipes']) == 2

  return 
  
  response = update_recipe_in_menu(client, shop_list['_id']['$oid'], tuna['_id']['$oid'],{
      'recipe' : ham['_id']['$oid'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 409

  response = update_recipe_in_menu(client, shop_list['_id']['$oid'], tuna['_id']['$oid'],{
      'recipe' : tuna['_id']['$oid'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 204

  shop_list = get_menu(client, shop_list['_id']['$oid'], auth_headers).json

  assert (shop_list['recipes'][0]['checked'] == False) and (shop_list['recipes'][1]['checked'] == True)

  response = update_recipe_in_menu(client, shop_list['_id']['$oid'], ham['_id']['$oid'],{
      'recipe' : ham['_id']['$oid'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 204

  shop_list = get_menu(client, shop_list['_id']['$oid'], auth_headers).json

  assert (shop_list['recipes'][0]['checked'] == True) and (shop_list['recipes'][1]['checked'] == True)


