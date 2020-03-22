import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_menu import create_menu, patch_menu
from test_recipe import create_recipe


def add_recipe_to_menu(client, menu_id, json, auth_headers):
    return client.post('/api/v1/menus/{}/recipes'.format(menu_id), json=json, headers=auth_headers)


def get_menu_recipes(client, menu_id, auth_headers):
    return client.get('/api/v1/menus/{}/recipes'.format(menu_id), headers=auth_headers)


def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    menu = create_menu(client, {
        'name': 'Menu',
        'date': '2020-01-21'
    }, auth_headers).json

    recipe1 = create_recipe(client, {
        'name': 'ham'
    }, auth_headers).json

    recipe2 = create_recipe(client, {
        'name': 'cheese'
    }, auth_headers).json

    response = add_recipe_to_menu(client, menu['_id'], {
        'recipe_id': recipe1['_id']
    }, auth_headers)

    assert response.status_code == 200 and len(response.json) == 1

    response = add_recipe_to_menu(client, menu['_id'], {
        'recipe_id': recipe2['_id']
    }, auth_headers)

    assert response.status_code == 200 and len(response.json) == 2


def test_delete_recipe_from_menu(client: FlaskClient, auth_headers):
    menu = create_menu(client, {
        'name': 'Menu',
        'date': '2020-01-21'
    }, auth_headers).json

    recipe1 = create_recipe(client, {
        'name': 'ham'
    }, auth_headers).json

    recipe2 = create_recipe(client, {
        'name': 'cheese'
    }, auth_headers).json

    response = get_menu_recipes(client, menu['_id'], auth_headers)

    assert response.status_code == 200 and len(response.json) == 0

    patch_menu(client, menu['_id'], {
        'recipes': [recipe1['_id'], recipe2['_id']]
    }, auth_headers)

    response = get_menu_recipes(client, menu['_id'], auth_headers)

    assert response.status_code == 200 and len(response.json) == 2
