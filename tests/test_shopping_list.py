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
  return client.patch('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), json=json, headers=auth_headers)

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
  } , auth_headers).json

  tuna = create_ingredient(client, {
    'name': 'tuna'
  } , auth_headers).json

  response = create_shopping_list(client, {
    'name' : 'list1',
    'items' : [
      {
        'item' : ham['_id']['$oid']
      },{
        'item' : tuna['_id']['$oid']
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
        'item' : ham['_id']['$oid']
      },{
        'item' : tuna['_id']['$oid']
      }
    ]
  }, auth_headers)

  response = update_item_in_shopping_list(client, shop_list['_id']['$oid'], tuna['_id']['$oid'],{
      'item' : ham['_id']['$oid']
  }, auth_headers)

  assert response.status_code == 204
