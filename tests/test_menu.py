import pytest

from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from conftest import add_offline_id
from test_ingredient import create_ingredient, delete_ingredient
from test_recipe import create_recipe

@add_offline_id
def create_menu(client, json, auth_headers, generate_offline_id: bool = True):
  if generate_offline_id == False:
      del json['offline_id']
    
  return client.post('/api/v1/menus', json=json, headers=auth_headers)


def replace_menu(client, menu_id, json, auth_headers):
    return client.put('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)


def patch_menu(client, menu_id, json, auth_headers):
    return client.patch('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)


def put_menu(client, menu_id, json, auth_headers):
    return client.put('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)


def get_menu(client, menu_id, auth_headers):
    return client.get('/api/v1/menus/{}'.format(menu_id), headers=auth_headers)


def get_all_menus(client, auth_headers, page=1, per_page=10):
    return client.get('/api/v1/menus?page={}&per_page={}'.format(page, per_page), headers=auth_headers)


def get_all_menus_by_day(client, auth_headers, day):
    return client.get('/api/v1/menus?day={}'.format(day), headers=auth_headers)


def test_not_authorized(client: FlaskClient):
    response = get_all_menus(client, {})

    assert response.status_code == 401


def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name': 'Menu',
        'id': '5e4ae04561fe8235a5a18824'
    }, auth_headers)

    assert response.status_code == 403

    response = patch_menu(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Menu',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403

    response = put_menu(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Menu',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403


def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

    response = create_menu(client, {
        'name': 'Menu1',
        'date': '2019-12-13',
        'owner': '123456'
    }, auth_headers)

    assert response.status_code == 403


def test_owner_update(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name': 'Menu1',
        'date': '2019-12-13'
    }, auth_headers)

    menu_id = response.json['_id']

    # Try to update owner using an integer instead of a string
    response = patch_menu(client, menu_id, {
        'owner': 1
    }, auth_headers)

    assert response.status_code == 400

    # Try to update owner using a valid objectId (from menu)
    response = patch_menu(client, menu_id, {
        'owner': menu_id
    }, auth_headers)

    assert response.status_code == 403


def test_menu_date_required(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name': 'Menu1'
    }, auth_headers)

    assert response.status_code == 400 and response.json['error'] == 'BAD_REQUEST'

    response = create_menu(client, {
        'name': 'Menu1',
        'date': '2019-12-13'
    }, auth_headers)

    assert response.status_code == 201


def test_menu_pagination(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name': 'Menu1',
        'date': '2019-12-13'
    }, auth_headers)

    assert response.status_code == 201

    response = get_all_menus(client, auth_headers)

    assert response.status_code == 200 and response.json['pages'] == 1 and len(
        response.json['results']) == 1

    response = create_menu(client, {
        'name': 'list2',
        'date': '2019-12-13'
    }, auth_headers)

    assert response.status_code == 201

    response = get_all_menus(client, auth_headers)

    assert response.status_code == 200 and response.json['pages'] == 1 and len(
        response.json['results']) == 2


def test_retrieve_menu_by_day(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name': 'Menu1',
        'date': '2019-12-13'
    }, auth_headers)

    response = create_menu(client, {
        'name': 'Menu2',
        'date': '2019-12-12'
    }, auth_headers)

    assert response.status_code == 201

    response = get_all_menus_by_day(client, auth_headers, '2019-12-13')

    assert response.status_code == 200 and len(
        response.json['results']) == 1

    # KO tests

    response = get_all_menus_by_day(client, auth_headers, '1993-12-33')

    assert response.status_code == 400

    response = get_all_menus_by_day(client, auth_headers, '1993-13-01')

    assert response.status_code == 400


def test_create_menu(client: FlaskClient, auth_headers):
    ham = create_ingredient(client, {
        'name': 'ham'
    }, auth_headers).json

    tuna = create_ingredient(client, {
        'name': 'tuna'
    }, auth_headers).json

    cheese = create_ingredient(client, {
        'name': 'cheese'
    }, auth_headers).json

    tuna_and_ham = create_recipe(client, {
        'name': 'Tuna And Ham',
        'ingredients': [
            {
                'ingredient': ham['_id']
            }, {
                'ingredient': tuna['_id']
            }
        ]
    }, auth_headers).json

    ham_and_cheese = create_recipe(client, {
        'name': 'Ham And Cheese',
        'ingredients': [
            {
                'ingredient': ham['_id']
            }, {
                'ingredient': cheese['_id']
            }
        ]
    }, auth_headers).json

    response = create_menu(client, {
        'name': 'Menu 1',
        'date': '2019-10-11',
        'recipes': [
            tuna_and_ham['_id'],
            ham_and_cheese['_id']
        ]
    }, auth_headers)

    assert response.status_code == 201

    response = get_menu(client, response.json['_id'], auth_headers)

    assert response.status_code == 200 and response.json['date'] == '2019-10-11'


def test_update_menu(client: FlaskClient, auth_headers):
    ham = create_ingredient(client, {
        'name': 'ham'
    }, auth_headers).json

    tuna = create_ingredient(client, {
        'name': 'tuna'
    }, auth_headers).json

    cheese = create_ingredient(client, {
        'name': 'cheese'
    }, auth_headers).json

    tuna_and_ham = create_recipe(client, {
        'name': 'Tuna And Ham',
        'ingredients': [
            {
                'ingredient': ham['_id']
            }, {
                'ingredient': tuna['_id']
            }
        ]
    }, auth_headers).json

    ham_and_cheese = create_recipe(client, {
        'name': 'Ham And Cheese',
        'ingredients': [
            {
                'ingredient': ham['_id']
            }, {
                'ingredient': cheese['_id']
            }
        ]
    }, auth_headers).json

    menu_response = create_menu(client, {
        'name': 'Menu 1',
        'date': '2019-10-11',
        'recipes': [
            tuna_and_ham['_id'],
            ham_and_cheese['_id']
        ]
    }, auth_headers).json

    assert len(menu_response['recipes']
               ) == 2 and menu_response['date'] == '2019-10-11'

    response = patch_menu(client, menu_response['_id'],  {
        'date': '2019-10-12'
    }, auth_headers)

    assert response.status_code == 200 and response.json[
        '_id'] == menu_response['_id'] and response.json['date'] == '2019-10-12'

def test_date_format(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name' : 'Fish',
        'date' : '2012-09-1212'
    }, auth_headers)

    assert response.status_code == 400

    response = create_menu(client, {
        'name' : 'Fish',
        'date' : '2012-31-31'
    }, auth_headers)

    assert response.status_code == 400

    response = create_menu(client, {
        'name' : 'Fish',
        'date' : '2012-12-31'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['date'] == '2012-12-31'

def test_offline_id(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'name' : 'Fish',
        'date' : '2012-09-12'
    }, auth_headers, False)

    assert response.status_code == 400

    response = create_menu(client, {
        'name' : 'Fish',
        'date' : '2012-09-12'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] is not None \
        and response.json['offline_id'] is not None

    idx = response.json['_id']
    offline_id = response.json['offline_id']

    response = put_menu(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'

    response = patch_menu(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'
    
    response = get_menu(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['offline_id'] == offline_id
