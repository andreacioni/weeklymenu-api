from mongomock import ObjectId
import pytest

from time import sleep
from datetime import datetime
from uuid import uuid4

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


def put_menu(client, menu_id, json, auth_headers):
    return client.put('/api/v1/menus/{}'.format(menu_id), json=json, headers=auth_headers)


def get_menu(client, menu_id, auth_headers):
    return client.get('/api/v1/menus/{}'.format(menu_id), headers=auth_headers)


def get_all_menus(client, auth_headers, page=1, per_page=10, order_by='', desc=False):
    return client.get('/api/v1/menus?page={}&per_page={}&order_by={}&desc={}'.format(page, per_page, order_by, desc), headers=auth_headers)


def get_all_menus_by_day(client, auth_headers, day):
    return client.get('/api/v1/menus?day={}'.format(day), headers=auth_headers)


def test_not_authorized(client: FlaskClient):
    response = get_all_menus(client, {})

    assert response.status_code == 401


def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'date': '2019-09-01',
        '_id': '5e4ae04561fe8235a5a18824'
    }, auth_headers)

    assert response.status_code == 201

    response = patch_menu(client, '5e4ae04561fe8235a5a18824', {
        'date': '2019-09-01',
        '_id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == '5e4ae04561fe8235a5a18824'

    response = put_menu(client, '5e4ae04561fe8235a5a18824', {
        'date': '2019-09-01',
        '_id': '1fe8235a5a5e4ae045618824'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == '5e4ae04561fe8235a5a18824'


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
                'ingredient': ham['_id'],
                'name': 'ham',
            }, {
                'ingredient': tuna['_id'],
                'name': 'tuna',
            }
        ]
    }, auth_headers).json

    ham_and_cheese = create_recipe(client, {
        'name': 'Ham And Cheese',
        'ingredients': [
            {
                'ingredient': ham['_id'],
                'name': 'ham',
            }, {
                'ingredient': cheese['_id'],
                'name': 'cheese',
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


def test_duplicate_entry_menu(client: FlaskClient, auth_headers):
    idx = ObjectId()
    response = create_menu(client, {
        "_id": idx,
        "name": "Menu 1",
        'date': '2012-01-12',
    }, auth_headers)

    assert response.status_code == 201 and ObjectId(
        response.json['_id']) == idx and response.json['date'] == '2012-01-12'

    response = create_menu(client, {
        "_id": idx,
        'name': 'Menu 2',
        'date': '2014-11-10',
    }, auth_headers)

    assert response.status_code == 409 and response.json['error'] == 'DUPLICATE_ENTRY'


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
                'ingredient': ham['_id'],
                'name': 'ham'
            }, {
                'ingredient': tuna['_id'],
                'name': 'tuna'
            }
        ]
    }, auth_headers).json

    ham_and_cheese = create_recipe(client, {
        'name': 'Ham And Cheese',
        'ingredients': [
            {
                'ingredient': ham['_id'],
                'name': 'ham'
            }, {
                'ingredient': cheese['_id'],
                'name': 'cheese'
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
        'name': 'Fish',
        'date': '2012-09-1212'
    }, auth_headers)

    assert response.status_code == 201  # truncated to 12

    response = create_menu(client, {
        'name': 'Fish',
        'date': '2012-31-31'
    }, auth_headers)

    assert response.status_code == 400

    response = create_menu(client, {
        'name': 'Fish',
        'date': '2012-12-31'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['date'] == '2012-12-31'


@pytest.mark.skip(reason="it gives random errors, needs more checks")
def test_offline_id(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        '_id': 'Mf5cd7d4f8cb6cd5acaec6f',  # invalid ObjectId
        'date': '2020-12-09'
    }, auth_headers)

    assert response.status_code == 400

    response = create_menu(client, {
        '_id': '5f5cd7d4f8cb6cd5acaec6f5',
        'date': '2020-12-09'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['_id'] == '5f5cd7d4f8cb6cd5acaec6f5'

    idx = response.json['_id']

    response = put_menu(client, idx, {
        '_id': '5f5cd7d4f8cb6cd5acaec6f8',  # Different ObjectId
        'date': '2020-12-09'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx

    response = patch_menu(client, idx, {
        '_id': '5f5cd7d4f8cb6cd5acaec6f8',  # Different ObjectId
        'date': '2020-12-09'
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx

    response = get_menu(client, idx, auth_headers)

    assert response.status_code == 200 \
        and response.json['_id'] == idx


def test_create_update_timestamp(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'date': '2019-02-14',
        'insert_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_menu(client, {
        'date': '2019-02-14',
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_menu(client, {
        'date': '2019-02-14',
        'update_timestamp': int(datetime.now().timestamp()),
        'insert_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = create_menu(client, {
        'date': '2019-02-14'
    }, auth_headers)

    assert response.status_code == 201 \
        and response.json['insert_timestamp'] is not None \
        and isinstance(response.json['insert_timestamp'], int) \
        and response.json['update_timestamp'] is not None \
        and isinstance(response.json['update_timestamp'], int)

    idx = response.json['_id']
    insert_timestamp = response.json['insert_timestamp']
    update_timestamp = response.json['update_timestamp']

    response = put_menu(client, idx, {
        'date': '2019-02-14',
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_menu(client, idx, {
        'date': '2019-02-14',
        'insert_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_menu(client, idx, {
        'date': '2019-02-14',
        'insert_timestamp': int(datetime.now().timestamp()),
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = put_menu(client, idx, {
        'date': '2019-02-14',
        'insert_timestamp': int(datetime.now().timestamp()),
        'update_timestamp': int(datetime.now().timestamp())
    }, auth_headers)

    assert response.status_code == 403 \
        and response.json['error'] == 'CANNOT_SET_CREATION_UPDATE_TIME'

    response = patch_menu(client, idx, {
        'date': '2019-02-14',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp

    update_timestamp = response.json['update_timestamp']

    response = put_menu(client, idx, {
        'date': '2020-02-14',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['date'] == '2020-02-14' \
        and response.json['insert_timestamp'] == insert_timestamp \
        and response.json['update_timestamp'] > update_timestamp


def test_get_last_updated(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'date': '2019-09-06',
    }, auth_headers)

    assert response.status_code == 201

    idx_1 = response.json['_id']
    insert_timestamp_1 = response.json['insert_timestamp']
    update_timestamp_1 = response.json['update_timestamp']

    sleep(1)  # avoid conflicting timestamps

    response = create_menu(client, {
        'date': '2019-10-06',
    }, auth_headers)

    assert response.status_code == 201

    idx_2 = response.json['_id']
    insert_timestamp_2 = response.json['insert_timestamp']
    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_menus(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2

    response = patch_menu(client, idx_1, {
        'name': 'Rice',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1

    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_menus(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1

    response = put_menu(client, idx_1, {
        'date': '2019-10-06',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_1 \
        and response.json['update_timestamp'] > update_timestamp_1

    update_timestamp_1 = response.json['update_timestamp']

    response = get_all_menus(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_1 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_1

    response = patch_menu(client, idx_2, {
        'date': '2019-10-06',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2

    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_menus(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2

    response = put_menu(client, idx_2, {
        'date': '2019-10-06',
    }, auth_headers)

    assert response.status_code == 200 \
        and response.json['insert_timestamp'] == insert_timestamp_2 \
        and response.json['update_timestamp'] > update_timestamp_2

    update_timestamp_2 = response.json['update_timestamp']

    response = get_all_menus(
        client, auth_headers, order_by='update_timestamp', desc=True, page=1, per_page=1)

    assert response.status_code == 200 \
        and len(response.json['results']) == 1 \
        and response.json['results'][0]['_id'] == idx_2 \
        and response.json['results'][0]['update_timestamp'] == update_timestamp_2


def test_allow_unexpected_value(client: FlaskClient, auth_headers):
    response = create_menu(client, {
        'date': '2020-12-12',
        'unexpected': 'field',
    }, auth_headers)

    assert response.status_code == 201 \
        and 'date' in response.json \
        and 'unexpected' not in response.json

    response = get_all_menus_by_day(client, auth_headers, '2020-12-12')

    assert response.status_code == 200 \
        and 'date' in response.json['results'][0] \
        and 'unexpected' not in response.json['results'][0]
