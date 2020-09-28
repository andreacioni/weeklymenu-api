import pytest

from datetime import datetime
from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from conftest import add_offline_id

from test_ingredient import create_ingredient, delete_ingredient

@add_offline_id
def create_shopping_list(client, json, auth_headers, generate_offline_id: bool = True):
  if generate_offline_id == False:
      del json['offline_id']
  
  return client.post('/api/v1/shopping-lists', json=json, headers=auth_headers)

def add_item_in_shopping_list(client, shopping_list_id, json, auth_headers):
  return client.post('/api/v1/shopping-lists/{}/items'.format(shopping_list_id), json=json, headers=auth_headers)

def get_shopping_list_item(client, shopping_list_id, shopping_list_item_id, auth_headers):
  return client.get('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), headers=auth_headers)

def replace_item_in_shopping_list(client, shopping_list_id, shopping_list_item_id, json, auth_headers):
  return client.put('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), json=json, headers=auth_headers)

def update_item_in_shopping_list(client, shopping_list_id, shopping_list_item_id, json, auth_headers):
  return client.patch('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), json=json, headers=auth_headers)

def delete_item_in_shopping_list(client, shopping_list_id, shopping_list_item_id, auth_headers):
  return client.delete('/api/v1/shopping-lists/{}/items/{}'.format(shopping_list_id, shopping_list_item_id), headers=auth_headers)

def get_shopping_list(client, shopping_list_id, auth_headers):
  return client.get('/api/v1/shopping-lists/{}'.format(shopping_list_id), headers=auth_headers)

def get_all_shopping_list(client, auth_headers, page=1, per_page=10):
  return client.get('/api/v1/shopping-lists?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def patch_shopping_list(client, shopping_list_id, json, auth_headers):
  return client.patch('/api/v1/shopping-lists/{}'.format(shopping_list_id), json=json, headers=auth_headers)

def put_shopping_list(client, shopping_list_id, json, auth_headers):
  return client.put('/api/v1/shopping-lists/{}'.format(shopping_list_id), json=json, headers=auth_headers)

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
    response = create_shopping_list(client, {
        'owner': 'pippo',
        'name': 'ham'
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
        'item' : ham['_id'],
        'checked': False
      },{
        'item' : tuna['_id'],
        'checked': False
      }
    ]
  }, auth_headers)

  assert response.status_code == 201

def test_append_item_to_list(client: FlaskClient, auth_headers):

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
        'item' : ham['_id'],
        'checked': False
      }
    ]
  }, auth_headers).json

  response = add_item_in_shopping_list(client, shop_list['_id'], {
        'item' : tuna['_id'],
        'checked': False
  }, auth_headers)

  assert response.status_code == 201

  response = add_item_in_shopping_list(client, shop_list['_id'], {
        'item' : tuna['_id'],
        'checked': False
  }, auth_headers)

  assert response.status_code == 409

def test_item_change_shopping_list(client: FlaskClient, auth_headers):
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
        'item' : ham['_id'],
        'checked' : False
      },{
        'item' : tuna['_id'],
        'checked' : False
      }
    ]
  }, auth_headers).json

  response = replace_item_in_shopping_list(client, shop_list['_id'], tuna['_id'],{
      'item' : ham['_id'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 200

  response = get_shopping_list_item(client, shop_list['_id'], tuna['_id'], auth_headers)

  assert response.status_code == 404 and response.json['error'] == 'NOT_FOUND'

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
        'item' : ham['_id'],
        'checked': False,
        'supermarketSection': 'Groceries'
      },{
        'item' : tuna['_id'],
        'checked': False,
        'supermarketSection': 'Groceries'
      }
    ]
  }, auth_headers).json

  assert shop_list['items'][0]['checked'] == False and shop_list['items'][1]['checked'] == False

  response = patch_shopping_list(client, shop_list['_id'], {
      'items' : [
        {
          'item' : ham['_id'],
          'checked': True,
          'supermarketSection': 'Groceries'
        },{
          'item' : tuna['_id'],
          'checked': False,
          'supermarketSection': 'Groceries'
        }
      ]
  }, auth_headers)

  assert response.status_code == 200 \
    and response.json['items'][0]['checked'] == True \
    and response.json['items'][1]['checked'] == False
def test_update_shopping_list_item(client: FlaskClient, auth_headers):
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
        'item' : ham['_id'],
        'checked': False,
        'supermarketSection': 'Groceries',
      },{
        'item' : tuna['_id'],
        'checked': False,
        'supermarketSection': 'Groceries',
        'quantity': 12,
        'unitOfMeasure': 'L'
      }
    ]
  }, auth_headers).json

  assert shop_list['items'][0]['checked'] == False \
    and ('quantity' not in shop_list['items'][0]) \
    and ('unitOfMeasure') not in shop_list['items'][0] \
    and shop_list['items'][1]['quantity'] == 12 \
    and shop_list['items'][1]['unitOfMeasure'] == 'L' \
    and shop_list['items'][1]['checked'] == False
  
  # NOTE replaced with test_item_change_shopping_list test
  #response = update_item_in_shopping_list(client, shop_list['_id'], tuna['_id'],{
  #    'item' : ham['_id'],
  #    'checked' : True
  #}, auth_headers)

  #assert response.status_code == 409

  response = update_item_in_shopping_list(client, shop_list['_id'], tuna['_id'],{
      'checked' : True,
      'quantity' : 23
  }, auth_headers)

  assert response.status_code == 200 and \
    response.json['supermarketSection'] == 'Groceries' and \
    response.json['quantity'] == 23.0

  shop_list = get_shopping_list(client, shop_list['_id'], auth_headers).json

  assert (shop_list['items'][0]['checked'] == False) and (shop_list['items'][1]['checked'] == True)

  response = update_item_in_shopping_list(client, shop_list['_id'], ham['_id'],{
      'item' : ham['_id'],
      'checked' : True,
      'quantity': 33,
      'unitOfMeasure': 'cl'
  }, auth_headers)

  assert response.status_code == 200 and \
    response.json['supermarketSection'] == 'Groceries' and \
    response.json['quantity'] == 33 and \
    response.json['unitOfMeasure'] == 'cl'

  shop_list = get_shopping_list(client, shop_list['_id'], auth_headers).json

  assert (shop_list['items'][0]['checked'] == True) and (shop_list['items'][1]['checked'] == True)

def test_replace_shopping_list_item(client: FlaskClient, auth_headers):
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
        'item' : ham['_id'],
        'checked': False,
        'supermarketSection': 'Groceries'
      },{
        'item' : tuna['_id'],
        'checked': False,
        'supermarketSection': 'Groceries'
      }
    ]
  }, auth_headers).json

  assert shop_list['items'][0]['checked'] == False and shop_list['items'][1]['checked'] == False
 
  # NOTE replaced with test_item_change_shopping_list test
  #response = replace_item_in_shopping_list(client, shop_list['_id'], tuna['_id'],{
  #    'item' : ham['_id'],
  #    'checked' : True
  #}, auth_headers)

  #assert response.status_code == 409

  response = replace_item_in_shopping_list(client, shop_list['_id'], tuna['_id'],{
      'item' : tuna['_id'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 200

  shop_list = get_shopping_list(client, shop_list['_id'], auth_headers).json

  assert (shop_list['items'][0]['checked'] == False) and (shop_list['items'][1]['checked'] == True)

  response = update_item_in_shopping_list(client, shop_list['_id'], ham['_id'],{
      'item' : ham['_id'],
      'checked' : True
  }, auth_headers)

  assert response.status_code == 200

  shop_list = get_shopping_list(client, shop_list['_id'], auth_headers).json

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
        'item' : ham['_id'],
        'checked' : True
      },{
        'item' : tuna['_id'],
        'checked' : True
      }
    ]
  }, auth_headers).json

  response = delete_item_in_shopping_list(client, shop_list['_id'], tuna['_id'], auth_headers)

  assert response.status_code == 204

  shop_list = get_shopping_list(client, shop_list['_id'], auth_headers).json

  assert ham['_id'] in [ it['item'] for it in shop_list['items'] ] and not (tuna['_id'] in [ it['item'] for it in shop_list['items'] ])

def test_two_list_with_same_name(client: FlaskClient, auth_headers, auth_headers_2):
  response = create_shopping_list(client, {
    'name' : 'Main List'
  }, auth_headers)

  assert response.status_code == 201

  response = create_shopping_list(client, {
    'name' : 'Main List'
  }, auth_headers_2)

  assert response.status_code == 201


def test_offline_id(client: FlaskClient, auth_headers):
    response = create_shopping_list(client, {
        'name' : 'Fish'
    }, auth_headers, False)

    assert response.status_code == 400

    response = create_shopping_list(client, {
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] is not None \
        and response.json['offline_id'] is not None

    idx = response.json['_id']
    offline_id = response.json['offline_id']

    response = put_shopping_list(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'

    response = patch_shopping_list(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'
    
    response = get_shopping_list(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['offline_id'] == offline_id
  
def test_create_update_date(client: FlaskClient, auth_headers):
    response = create_shopping_list(client, {
        'name': 'Rice',
        'creation_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_shopping_list(client, {
        'name': 'Rice',
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_shopping_list(client, {
        'name': 'Rice',
        'update_date': str(datetime.now()),
        'creation_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_shopping_list(client, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['creation_date'] is not None \
            and isinstance(response.json['creation_date'], int) \
        and response.json['update_date'] is not None \
            and isinstance(response.json['update_date'], int)    
    
    idx = response.json['_id']
    creation_date = response.json['creation_date']
    update_date = response.json['update_date']
    
    response = put_shopping_list(client, idx, {
        'name': 'Tomato',
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_shopping_list(client, idx, {
        'name': 'Tomato',
        'creation_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_shopping_list(client, idx, {
        'name': 'Tomato',
        'creation_date': str(datetime.now()),
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = put_shopping_list(client, idx, {
        'name': 'Tomato',
        'creation_date': str(datetime.now()),
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_shopping_list(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['creation_date'] == creation_date \
        and response.json['update_date'] > update_date
    
    update_date = response.json['update_date']

    response = put_shopping_list(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['name'] == 'Tomato' \
        and response.json['creation_date'] == creation_date \
        and response.json['update_date'] > update_date