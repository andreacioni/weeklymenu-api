import pytest

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_recipe import create_recipe
from test_ingredient import create_ingredient


def get_all_recipe_ingredient(client, recipe_id, auth_headers):
    return client.get('/api/v1/recipes/{}/ingredients'.format(recipe_id), headers=auth_headers)


def get_recipe_ingredient(client, recipe_id, ingredient_id, auth_headers):
    return client.get('/api/v1/recipes/{}/ingredients/{}'.format(recipe_id, ingredient_id), headers=auth_headers)


def add_recipe_ingredient(client, recipe_id, json, auth_headers):
    return client.post('/api/v1/recipes/{}/ingredients'.format(recipe_id), json=json, headers=auth_headers)


def remove_recipe_ingredient(client, recipe_id, ingredient_id, auth_headers):
    return client.delete('/api/v1/recipes/{}/ingredients/{}'.format(recipe_id, ingredient_id), headers=auth_headers)


def update_recipe_ingredient(client, recipe_id, ingredient_id, json, auth_headers):
    return client.patch('/api/v1/recipes/{}/ingredients/{}'.format(recipe_id, ingredient_id), json=json, headers=auth_headers)


def test_create_recipe_ingredient(client: FlaskClient, auth_headers):
    tuna_resp = create_ingredient(client, {
        'name': 'Tuna'
    }, auth_headers)

    tomato_resp = create_ingredient(client, {
        'name': 'Tomatoes'
    }, auth_headers)

    oil_resp = create_ingredient(client, {
        'name': 'Olive Oil'
    }, auth_headers)

    recipe_resp = create_recipe(client, {
        'name': 'Tuna and tomatoes',
        'ingredients': [
            {
                'ingredient': tuna_resp.json['_id'],
                'name': 'tuna'
            }, {
                'ingredient': tomato_resp.json['_id'],
                'name': 'tomato'
            }
        ]
    }, auth_headers)

    assert len(recipe_resp.json['ingredients']) == 2

    response = get_all_recipe_ingredient(
        client, recipe_resp.json['_id'], auth_headers)

    assert response.status_code == 200 and len(response.json) == 2

    response = add_recipe_ingredient(client, recipe_resp.json['_id'], {
        'ingredient': oil_resp.json['_id'],
        'name': 'oil'
    }, auth_headers)

    assert response.status_code == 201

    response = add_recipe_ingredient(client, recipe_resp.json['_id'], {
        'ingredient': oil_resp.json['_id'],
        'name': 'oil'
    }, auth_headers)

    assert response.status_code == 409

    response = get_all_recipe_ingredient(
        client, recipe_resp.json['_id'], auth_headers)

    assert response.status_code == 200 and len(response.json) == 3


def test_recipe_ingredient_delete(client: FlaskClient, auth_headers):
    tuna_resp = create_ingredient(client, {
        'name': 'Tuna'
    }, auth_headers)

    tomato_resp = create_ingredient(client, {
        'name': 'Tomatoes'
    }, auth_headers)

    recipe_resp = create_recipe(client, {
        'name': 'Tuna and tomatoes',
        'ingredients': [
            {
                'ingredient': tuna_resp.json['_id'],
                'name': 'tuna'
            }, {
                'ingredient': tomato_resp.json['_id'],
                'name': 'tomato'
            }
        ]
    }, auth_headers)

    assert len(recipe_resp.json['ingredients']) == 2

    response = get_all_recipe_ingredient(
        client, recipe_resp.json['_id'], auth_headers)

    assert response.status_code == 200 and len(response.json) == 2

    response = remove_recipe_ingredient(
        client, recipe_resp.json['_id'], tomato_resp.json['_id'], auth_headers)

    assert response.status_code == 204

    response = get_all_recipe_ingredient(
        client, recipe_resp.json['_id'], auth_headers)

    assert response.status_code == 200 and len(response.json) == 1


def test_update_recipe_ingredient(client: FlaskClient, auth_headers):
    tuna_resp = create_ingredient(client, {
        'name': 'Tuna'
    }, auth_headers)

    recipe_resp = create_recipe(client, {
        'name': 'Tuna',
        'ingredients': [
            {
                'quantity': 10,
                'ingredient': tuna_resp.json['_id'],
                'name': 'tuna',
                'unitOfMeasure': 'grams'
            }
        ]
    }, auth_headers)

    response = update_recipe_ingredient(client, recipe_resp.json['_id'], tuna_resp.json['_id'], {
        'quantity': 2
    }, auth_headers)

    assert response.status_code == 200 and response.json[
        'quantity'] == 2 and response.json['unitOfMeasure'] == 'grams'

    response = get_recipe_ingredient(
        client, recipe_resp.json['_id'], tuna_resp.json['_id'], auth_headers)

    assert response.status_code == 200 and response.json[
        'quantity'] == 2 and response.json['unitOfMeasure'] == 'grams'
