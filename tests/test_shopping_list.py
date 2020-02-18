import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient

def create_shopping_list(client, json, auth_headers):
  return client.post('/api/v1/shopping-lists', json=json, headers=auth_headers)

def add_item_in_shopping_list(client, shopping_list_id, json, auth_headers):
  return client.post('/api/v1/shopping-lists/{}/items'.format(shopping_list_id), json=json, headers=auth_headers)

def update_item_in_shopping_list(client, shopping_list_id, shopping_list_item_id, json, auth_headers):
  return client.put('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), json=json, headers=auth_headers)

def delete_item_in_shopping_list(client, shopping_list_id, shopping_list_item_id, auth_headers):
  return client.delete('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), headers=auth_headers)

def get_shopping_list(client, shopping_list_id, auth_headers):
  return client.get('/api/v1/shopping-lists/{}'.format(shopping_list_id), headers=auth_headers)

def get_all_shopping_list(client, auth_headers, page=1, per_page=10):
  return client.get('/api/v1/shopping-lists?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def test_not_authorized(client: FlaskClient):
  response = get_all_shopping_list(client, {})
  
  assert response.status_code == 401

def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

    response = create_shopping_list(client, {
      'name' : 'list1',
      'items' : [],
      'owner' : 'pippo'
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
  } , auth_headers).json

  tuna = create_ingredient(client, {
    'name': 'tuna'
  } , auth_headers).json

  response = create_shopping_list(client, {
    'name' : 'list1',
    'items' : [
      {
        'item' : ham['_id']['$oid'],
        'checked': False
      },{
        'item' : tuna['_id']['$oid'],
        'checked': False
      }
    ]
  }, auth_headers)

  assert response.status_code == 201

def test_update_shopping_list(client: FlaskClient, auth_headers):
  ham = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers).json

  tuna = create_ingredient(client, {
    'name': 'tuna'
  } , auth_headers).json

  shop_list = create_shopping_list(client, {
    'name' : 'list1',
    'items' : [
      {
        'item' : ham['_id']['$oid'],
        'checked': False
      },{
        'item' : tuna['_id']['$oid'],
        'checked': False
      }
    ]
  }, auth_headers).json

  assert shop_list['items'][0]['checked'] == False and shop_list['items'][1]['checked'] == False

  response = update_item_in_shopping_list(client, shop_list['_id']['$oid'], tuna['_id']['$oid'],{
      'item' : ham['_id']['$oid'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 409

  response = update_item_in_shopping_list(client, shop_list['_id']['$oid'], tuna['_id']['$oid'],{
      'item' : tuna['_id']['$oid'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 204

  shop_list = get_shopping_list(client, shop_list['_id']['$oid'], auth_headers).json

  assert (shop_list['items'][0]['checked'] == False) and (shop_list['items'][1]['checked'] == True)

  response = update_item_in_shopping_list(client, shop_list['_id']['$oid'], ham['_id']['$oid'],{
      'item' : ham['_id']['$oid'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 204

  shop_list = get_shopping_list(client, shop_list['_id']['$oid'], auth_headers).json

  assert (shop_list['items'][0]['checked'] == True) and (shop_list['items'][1]['checked'] == True)

def test_remove_shopping_list_item(client: FlaskClient, auth_headers):
  ham = create_ingredient(client, {
    'name': 'ham'
  } , auth_headers).json

  tuna = create_ingredient(client, {
    'name': 'tuna'
  } , auth_headers).json

  shop_list = create_shopping_list(client, {
    'name' : 'list1',
    'items' : [
      {
        'item' : ham['_id']['$oid'],
        'checked' : True
      },{
        'item' : tuna['_id']['$oid'],
        'checked' : True
      }
    ]
  }, auth_headers).json

  response = delete_item_in_shopping_list(client, shop_list['_id']['$oid'], tuna['_id']['$oid'], auth_headers)

  assert response.status_code == 204

  shop_list = get_shopping_list(client, shop_list['_id']['$oid'], auth_headers).json

  assert ham['_id'] in [ it['item'] for it in shop_list['items'] ] and not (tuna['_id'] in [ it['item'] for it in shop_list['items'] ])



