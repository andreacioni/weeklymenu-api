from mongomock import ObjectId
import pytest

from time import sleep
from datetime import datetime
from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

def get_user_profile(client, auth_headers):
  return client.get('/api/v1/users/me', headers=auth_headers)

def get_user_preferences_list(client, auth_headers):
  return client.get('/api/v1/users/me/preferences', headers=auth_headers)

def get_user_preferences(client, pref_id, auth_headers):
  return client.get('/api/v1/users/me/preferences/{}'.format(pref_id), headers=auth_headers)

def post_user_preferences(client, json, auth_headers):
    return client.post('/api/v1/users/me/preferences', json=json, headers=auth_headers)

def put_user_preferences(client, pref_id, json, auth_headers):
    return client.put('/api/v1/users/me/preferences/{}'.format(pref_id), json=json, headers=auth_headers)

def patch_user_preferences(client, pref_id, json, auth_headers):
    return client.patch('/api/v1/users/me/preferences/{}'.format(pref_id), json=json, headers=auth_headers)

def delete_user_preferences(client, pref_id, auth_headers):
    return client.delete('/api/v1/users/me/preferences/{}'.format(pref_id), headers=auth_headers)

def test_get_user_preference(client: FlaskClient, auth_headers):
    response = get_user_preferences_list(client, auth_headers)

    assert response.status_code == 200

def test_create_user_preference(client: FlaskClient, auth_headers):
    response = post_user_preferences(client, {}, auth_headers)

    assert response.status_code == 201

    #delete before exit to avoid unexpected failure on other tests
    response = delete_user_preferences(client, response.json['_id'], auth_headers)

    assert response.status_code == 204

def test_replace_user_preference(client: FlaskClient, auth_headers):
    response = post_user_preferences(client, {}, auth_headers).json
    current_prefs = get_user_preferences(client, response['_id'], auth_headers).json

    assert ('shopping_days' not in current_prefs.keys()) and \
            ('supermarket_sections' not in current_prefs.keys())
    
    response = put_user_preferences(client, current_prefs['_id'], {
        'shopping_days': [1, 4],
        'supermarket_sections': [{
            'name': 'section1'
        }],
    }, auth_headers)

    assert response.status_code == 200 and \
        len(response.json['shopping_days']) == 2 and \
            len(response.json['supermarket_sections']) == 1 \

    response = get_user_preferences(client, current_prefs['_id'], auth_headers)

    assert response.status_code == 200 and \
        response.json['shopping_days'] == [1, 4] and \
            response.json['supermarket_sections'][0]['name'] == 'section1'

def test_update_user_preference(client: FlaskClient, auth_headers):
    response = post_user_preferences(client, {}, auth_headers).json
    current_prefs = get_user_preferences(client, response['_id'], auth_headers).json

    assert ('shopping_days' not in current_prefs.keys()) and \
            ('supermarket_sections' not in current_prefs.keys())
    
    response = patch_user_preferences(client, current_prefs['_id'], {
        'shopping_days': [1, 4],
        'supermarket_sections': [{
            'name': 'section1'
        }],
    }, auth_headers)

    assert response.status_code == 200 and \
        len(response.json['shopping_days']) == 2 and \
            len(response.json['supermarket_sections']) == 1

    response = get_user_preferences(client, current_prefs['_id'], auth_headers)

    assert response.status_code == 200 and \
        response.json['shopping_days'] == [1, 4] and \
            response.json['supermarket_sections'][0]['name'] == 'section1'

    patch_user_preferences(client, current_prefs['_id'], {
        'shopping_days': [3, 6]
    }, auth_headers)

    response = get_user_preferences(client, current_prefs['_id'], auth_headers)

    assert response.status_code == 200 and \
        response.json['shopping_days'] == [3, 6] and \
            response.json['supermarket_sections'][0]['name'] == 'section1'

def test_get_user_profile(client: FlaskClient, auth_headers):
    response = get_user_profile(client, auth_headers)

    assert response.status_code == 200