import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient
from test_recipe import create_recipe


def create_menu(client, json, auth_headers):
    return client.post('/api/v1/menus', json=json, headers=auth_headers)


def replace_menu(client, menu_id, json, auth_headers):
    return client.put('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)


def patch_menu(client, menu_id, json, auth_headers):
    return client.patch('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)


def get_menu(client, menu_id, auth_headers):
    return client.get('/api/v1/menus/{}'.format(menu_id), headers=auth_headers)


def get_all_menus(client, auth_headers, page=1, per_page=10):
    return client.get('/api/v1/menus?page={}&per_page={}'.format(page, per_page), headers=auth_headers)


def test_not_authorized(client: FlaskClient):
    response = get_all_menus(client, {})

    assert response.status_code == 401

def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

    response = create_menu(client, {
        'name': 'Menu1',
        'date': '2019-12-13',
        'owner' : '123456'
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
                'ingredient': ham['_id']['$oid']
            }, {
                'ingredient': tuna['_id']['$oid']
            }
        ]
    }, auth_headers).json

    ham_and_cheese = create_recipe(client, {
        'name': 'Ham And Cheese',
        'ingredients': [
            {
                'ingredient': ham['_id']['$oid']
            }, {
                'ingredient': cheese['_id']['$oid']
            }
        ]
    }, auth_headers).json

    response = create_menu(client, {
        'name': 'Menu 1',
        'date': '2019-10-11',
        'recipes': [
            tuna_and_ham['_id']['$oid'],
            ham_and_cheese['_id']['$oid']
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
                'ingredient': ham['_id']['$oid']
            }, {
                'ingredient': tuna['_id']['$oid']
            }
        ]
    }, auth_headers).json

    ham_and_cheese = create_recipe(client, {
        'name': 'Ham And Cheese',
        'ingredients': [
            {
                'ingredient': ham['_id']['$oid']
            }, {
                'ingredient': cheese['_id']['$oid']
            }
        ]
    }, auth_headers).json

    menu_response = create_menu(client, {
        'name': 'Menu 1',
        'date': '2019-10-11',
        'recipes': [
            tuna_and_ham['_id']['$oid'],
            ham_and_cheese['_id']['$oid']
        ]
    }, auth_headers).json

    assert len(menu_response['recipes']) == 2 and menu_response['date'] == '2019-10-11'

    response = patch_menu(client, menu_response['_id'],  {
        'date': '2019-10-12'
    }, auth_headers)

    assert response.status_code == 200 and response.json['_id'] == menu_response['_id'] and response.json['date'] == '2019-10-12'