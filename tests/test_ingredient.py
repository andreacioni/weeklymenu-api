import pytest

from uuid import uuid4
from datetime import datetime, time

from conftest import add_offline_id

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient


@add_offline_id
def create_ingredient(client, json, auth_headers, generate_offline_id: bool = True):
    if generate_offline_id == False:
        del json['offline_id']
    
    return client.post('/api/v1/ingredients', json=json, headers=auth_headers)


def replace_ingredient(client, ing_id, json, auth_headers):
    return client.put('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)


def patch_ingredient(client, ing_id, json, auth_headers):
    return client.patch('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)


def put_ingredient(client, ing_id, json, auth_headers):
    return client.put('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)


def delete_ingredient(client, ing_id, auth_headers):
    return client.delete('/api/v1/ingredients/{}'.format(ing_id), headers=auth_headers)


def get_all_ingredients(client, auth_headers, page=1, per_page=10):
    return client.get('/api/v1/ingredients?page={}&per_page={}'.format(page, per_page), headers=auth_headers)

def get_ingredient(client, ing_id, auth_headers):
    return client.get('/api/v1/ingredients/{}'.format(ing_id), headers=auth_headers)


def test_not_authorized(client: FlaskClient):
    response = get_all_ingredients(client, {})

    assert response.status_code == 401


def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Garlic',
        'id': '5e4ae04561fe8235a5a18824'
    }, auth_headers)

    assert response.status_code == 403

    response = patch_ingredient(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Garlic',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403

    response = put_ingredient(client, '1fe8235a5a5e4ae045618824', {
        'name': 'Garlic',
        'id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 403


def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

    response = create_ingredient(client, {
        'name': 'Garlic',
        'owner': '123abc'
    }, auth_headers)

    assert response.status_code == 403


def test_owner_update(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'ham'
    }, auth_headers)

    ingredient_id = response.json['_id']

    # Try to update owner using an integer instead of a string
    response = patch_ingredient(client, response.json['_id'], {
        'owner': 1
    }, auth_headers)

    assert response.status_code == 400

    # Try to update owner using a valid objectId (from ingredient)
    response = patch_ingredient(client, ingredient_id, {
        'owner': ingredient_id
    }, auth_headers)

    assert response.status_code == 403


def test_create_ingredient(client: FlaskClient, auth_headers):
    response = get_all_ingredients(client, auth_headers)

    assert response.status_code == 200 and len(
        response.json['results']) == 0 and response.json['pages'] == 0

    response = create_ingredient(client, {
        'name': 'ham'
    }, auth_headers)

    assert response.status_code == 201 and response.json[
        'name'] == 'ham'

    # TODO uniqueness in collection cannot be guaranteed across different users
    # Test fail duplicating ingredient
    # response = create_ingredient(client, {
    #  'name': 'ham'
    # } , auth_headers)

    # assert response.status_code == 409

    response = create_ingredient(client, {
        'name': 'cheese',
        'freezed': True
    }, auth_headers)

    assert response.status_code == 201 and response.json[
        'name'] == 'cheese' and response.json['freezed'] == True

    # Check pagination
    response = get_all_ingredients(client, auth_headers, 1, 1)

    assert response.status_code == 200 and response.json['pages'] == 2

    # Remove one ingredient
    response = delete_ingredient(
        client, response.json['results'][0]['_id'], auth_headers)

    assert response.status_code == 204

    response = get_all_ingredients(client, auth_headers)

    assert response.status_code == 200 \
        and response.json['pages'] == 1 \
        and len(response.json['results']) == 1

def test_replace_ingredient(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Tuna',
        'description': 'this is a tuna'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['name'] == 'Tuna'  \
        and response.json['description'] == 'this is a tuna' \
        and response.json['_id'] is not None \
        and response.json['offline_id'] is not None

    original_id = response.json['_id']
    original_offline_id = response.json['offline_id']

    response = replace_ingredient(client, original_id, {
        'name': 'Tuna',
        'description': 'always a tuna',
        'note': 'note about tuna'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['description'] == 'always a tuna' \
        and response.json['note'] == 'note about tuna' \
        and original_id == response.json['_id'] \
        and original_offline_id == response.json['offline_id']


def test_duplicate_ingredient_allowed(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Tuna',
        'description': 'this is a tuna'
    }, auth_headers)

    assert response.status_code == 201

    response = create_ingredient(client, {
        'name': 'Tuna',
        'description': 'always a tuna',
        'note': 'note about tuna'
    }, auth_headers)

    assert response.status_code == 201

    response = get_all_ingredients(client, auth_headers)

    assert response.status_code == 200 and response.json['pages'] == 1 and len(
        response.json['results']) == 2


def test_partial_ingredient_update(client: FlaskClient, auth_headers):

    tuna = create_ingredient(client, {
        'name': 'Tuna',
        'description': 'always a tuna',
        'note': 'note about tuna',
        'availabilityMonths': [
            1, 2
        ]
    }, auth_headers).json

    assert tuna['description'] == 'always a tuna'

    response = patch_ingredient(client, tuna['_id'], {
        'description': 'is a really great tuna',
        'availabilityMonths': [
            12
        ]
    }, auth_headers)

    assert response.status_code == 200 and response.json[
        'description'] == 'is a really great tuna' and 12 in response.json['availabilityMonths']

    response = patch_ingredient(client, tuna['_id'], {
        'description': 'is a really great tuna',
        'availabilityMonths': [
            12, 13
        ]
    }, auth_headers)

    assert response.status_code == 400

def test_offline_id(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name' : 'Fish'
    }, auth_headers, False)

    assert response.status_code == 400

    response = create_ingredient(client, {
        'name' : 'Fish'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] is not None \
        and response.json['offline_id'] is not None

    idx = response.json['_id']
    offline_id = response.json['offline_id']

    response = put_ingredient(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'

    response = patch_ingredient(client, idx, {
        'name' : 'Fish',
        'offline_id': str(uuid4())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_ID'
    
    response = get_ingredient(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['offline_id'] == offline_id

def test_create_update_date(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Rice',
        'creation_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_ingredient(client, {
        'name': 'Rice',
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_ingredient(client, {
        'name': 'Rice',
        'update_date': str(datetime.now()),
        'creation_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'
    
    response = create_ingredient(client, {
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
    
    response = put_ingredient(client, idx, {
        'name': 'Tomato',
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_ingredient(client, idx, {
        'name': 'Tomato',
        'creation_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_ingredient(client, idx, {
        'name': 'Tomato',
        'creation_date': str(datetime.now()),
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = put_ingredient(client, idx, {
        'name': 'Tomato',
        'creation_date': str(datetime.now()),
        'update_date': str(datetime.now())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_ingredient(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['creation_date'] == creation_date \
        and response.json['update_date'] > update_date
    
    update_date = response.json['update_date']

    response = put_ingredient(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['name'] == 'Tomato' \
        and response.json['creation_date'] == creation_date \
        and response.json['update_date'] > update_date
