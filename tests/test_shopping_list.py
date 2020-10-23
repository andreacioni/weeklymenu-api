import pytest

from datetime import datetime
from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient

def create_shopping_list(client, json, auth_headers):
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

def get_all_shopping_list(client, auth_headers, page=1, per_page=10, order_by='', desc=False):
  return client.get('/api/v1/shopping-lists?page={}&per_page={}&order_by={}&desc={}'.format(page, per_page, order_by, desc), headers=auth_headers)

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
        'id': 'Mf5cd7d4f8cb6cd5acaec6f', # invalid ObjectId
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 400

    response = create_shopping_list(client, {
        'id': '5f5cd7d4f8cb6cd5acaec6f5',
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] == '5f5cd7d4f8cb6cd5acaec6f5'

    idx = response.json['_id']

    response = put_shopping_list(client, idx, {
        'id': '5f5cd7d4f8cb6cd5acaec6f8', # Different ObjectId
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'

    response = patch_shopping_list(client, idx, {
        'id': '5f5cd7d4f8cb6cd5acaec6f8', # Different ObjectId
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'
    
    response = get_shopping_list(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx
  
def test_create_update_timestamp(client: FlaskClient, auth_headers):
    response = create_shopping_list(client, {
        'name': 'Rice',
        'insert_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_shopping_list(client, {
        'name': 'Rice',
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_shopping_list(client, {
        'name': 'Rice',
        'update_timestamp': str(datetime.now()),
        'insert_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_shopping_list(client, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['insert_timestamp'] is not None \
            and isinstance(response.json['insert_timestamp'], int) \
        and response.json['update_timestamp'] is not None \
            and isinstance(response.json['update_timestamp'], int)    
    
    idx = response.json['_id']
    insert_timestamp = response.json['insert_timestamp']
    update_timestamp = response.json['update_timestamp']
    
    response = put_shopping_list(client, idx, {
        'name': 'Tomato',
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_shopping_list(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_shopping_list(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': str(datetime.now()),
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = put_shopping_list(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': str(datetime.now()),
        'update_timestamp': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_shopping_list(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp
    
    update_timestamp = response.json['update_timestamp']

    response = put_shopping_list(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['name'] == 'Tomato' \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp

def test_get_last_updated(client: FlaskClient, auth_headers):
    response = create_shopping_list(client, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 201  
    
    idx_1 = response.json['_id']
    insert_timestamp_1 = response.json['insert_timestamp']
    update_timestamp_1 = response.json['update_timestamp']

    response = create_shopping_list(client, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 201  
    
    idx_2 = response.json['_id']
    insert_timestamp_2 = response.json['insert_timestamp']
    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_shopping_list(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2

    response = patch_shopping_list(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1
    
    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_shopping_list(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1

    response = put_shopping_list(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1

    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_shopping_list(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1
    
    response = patch_shopping_list(client, idx_2, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2
    
    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_shopping_list(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2

    response = put_shopping_list(client, idx_2, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2

    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_shopping_list(client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2
        