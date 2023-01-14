from pydoc import cli
from mongomock import ObjectId
import pytest

from time import sleep
from uuid import uuid4
from datetime import datetime, time

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient


def create_ingredient(client, json, auth_headers):
    return client.post('/api/v1/ingredients', json=json, headers=auth_headers)


def replace_ingredient(client, ing_id, json, auth_headers):
    return client.put('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)


def patch_ingredient(client, ing_id, json, auth_headers):
    return client.patch('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)


def put_ingredient(client, ing_id, json, auth_headers):
    return client.put('/api/v1/ingredients/{}'.format(ing_id), json=json, headers=auth_headers)


def delete_ingredient(client, ing_id, auth_headers):
    return client.delete('/api/v1/ingredients/{}'.format(ing_id), headers=auth_headers)


def get_all_ingredients(client, auth_headers, page=1, per_page=10, order_by='', desc=False):
    return client.get('/api/v1/ingredients?page={}&per_page={}&order_by={}&desc={}'.format(page, per_page, order_by, desc), headers=auth_headers)


def get_ingredient(client, ing_id, auth_headers):
    return client.get('/api/v1/ingredients/{}'.format(ing_id), headers=auth_headers)


def test_not_authorized(client: FlaskClient):
    response = get_all_ingredients(client, {})

    assert response.status_code == 401


def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Garlic',
        '_id': '5e4ae04561fe8235a5a18824'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] == '5e4ae04561fe8235a5a18824'

    response = patch_ingredient(client, '5e4ae04561fe8235a5a18824', {
        'name': 'Garlic',
        '_id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == '5e4ae04561fe8235a5a18824'

    response = put_ingredient(client, '5e4ae04561fe8235a5a18824', {
        'name': 'Garlic',
        '_id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == '5e4ae04561fe8235a5a18824'


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


def test_duplicate_entry_ingredient(client: FlaskClient, auth_headers):
    idx = ObjectId()
    response = create_ingredient(client, {
        "_id": idx,
        'name': 'Ingredient 1',
    }, auth_headers)

    assert response.status_code == 201 and ObjectId(
        response.json['_id']) == idx and response.json['name'] == 'Ingredient 1'

    response = create_ingredient(client, {
        "_id": idx,
        'name': 'Ingredient 2',
    }, auth_headers)

    assert response.status_code == 409 and response.json['error'] == 'DUPLICATE_ENTRY'


def test_replace_ingredient(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Tuna',
        'description': 'this is a tuna'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['name'] == 'Tuna'  \
        and response.json['description'] == 'this is a tuna' \
        and response.json['_id'] is not None

    original_id = response.json['_id']

    response = replace_ingredient(client, original_id, {
        'name': 'Tuna',
        'description': 'always a tuna',
        'note': 'note about tuna'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['description'] == 'always a tuna' \
        and response.json['note'] == 'note about tuna' \
        and original_id == response.json['_id']


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


@pytest.mark.skip(reason="it gives random errors, needs more checks")
def test_offline_id(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        '_id': 'Mf5cd7d4f8cb6cd5acaec6f',  # invalid ObjectId
        'name': 'Fish'
    }, auth_headers)

    assert response.status_code == 400

    response = create_ingredient(client, {
        '_id': '5f5cd7d4f8cb6cd5acaec6f5',
        'name': 'Fish'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] == '5f5cd7d4f8cb6cd5acaec6f5'

    idx = response.json['_id']

    response = put_ingredient(client, idx, {
        '_id': '5f5cd7d4f8cb6cd5acaec6f8',  # Different ObjectId
        'name': 'Fish'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx

    response = patch_ingredient(client, idx, {
        '_id': '5f5cd7d4f8cb6cd5acaec6f8',  # Different ObjectId
        'name': 'Fish'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx

    response = get_ingredient(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx


def test_create_update_timestamp(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Rice',
        'insert_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_ingredient(client, {
        'name': 'Rice',
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_ingredient(client, {
        'name': 'Rice',
        'update_timestamp': int(datetime.now().timestamp()),
        'insert_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_ingredient(client, {
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

    response = put_ingredient(client, idx, {
        'name': 'Tomato',
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_ingredient(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_ingredient(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': int(datetime.now().timestamp()),
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = put_ingredient(client, idx, {
        'name': 'Tomato',
        'insert_timestamp': int(datetime.now().timestamp()),
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_ingredient(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp

    update_timestamp = response.json['update_timestamp']

    response = put_ingredient(client, idx, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['name'] == 'Tomato' \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp


def test_get_last_updated(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 201

    idx_1 = response.json['_id']
    insert_timestamp_1 = response.json['insert_timestamp']
    update_timestamp_1 = response.json['update_timestamp']

    sleep(1)  # avoid conflicting timestamps

    response = create_ingredient(client, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 201

    idx_2 = response.json['_id']
    insert_timestamp_2 = response.json['insert_timestamp']
    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_ingredients(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2

    response = patch_ingredient(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1

    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_ingredients(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1

    response = put_ingredient(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1

    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_ingredients(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1

    response = patch_ingredient(client, idx_2, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2

    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_ingredients(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2

    response = put_ingredient(client, idx_2, {
        'name': 'Tomato',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2

    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_ingredients(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2


def test_allow_unexpected_value(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {
        'name': 'Rice',
        'unexpected': 'field',
    }, auth_headers)

    assert response.status_code == 201 \
        and 'name' in response.json \
        and 'unexpected' not in response.json

    response = get_ingredient(client, response.json['_id'], auth_headers)

    assert response.status_code == 200 \
        and 'name' in response.json \
        and 'unexpected' not in response.json
