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

def post_user_preferences(client, pref_id,  json, auth_headers):
    return client.post('/api/v1/users/me/preferences/{}'.format(pref_id), json=json, headers=auth_headers)

def put_user_preferences(client, pref_id, json, auth_headers):
    return client.put('/api/v1/users/me/preferences/{}'.format(pref_id), json=json, headers=auth_headers)

def patch_user_preferences(client, pref_id, json, auth_headers):
    return client.patch('/api/v1/users/me/preferences/{}'.format(pref_id), json=json, headers=auth_headers)

def test_get_user_preference(client: FlaskClient, auth_headers):
    response = get_user_preferences(client, auth_headers)

    assert response.status_code == 200

def test_create_user_preference(client: FlaskClient, auth_headers):
    response = post_user_preferences(client, {}, auth_headers)

    assert response.status_code == 201

def test_replace_user_preference(client: FlaskClient, auth_headers):
    # get default profile prefs
    current_prefs = get_user_preferences_list(client, auth_headers).json['results']

    assert len(current_prefs) == 1 and \
        len(current_prefs[0]['shopping_days']) == 0 and \
            len(current_prefs[0]['supermarket_sections']) == 0
    
    response = put_user_preferences(client, current_prefs[0]['_id'], {
        'shopping_days': [1, 4],
        'supermarket_sections': [{
            'name': 'section1'
        }],
    }, auth_headers)

    assert response.status_code == 200 and \
        len(response.json['shopping_days']) == 2 and \
            len(response.json['supermarket_sections']) == 1 \

    response = get_user_preferences(client, current_prefs[0]['_id'], auth_headers)

    assert response.status_code == 200 and \
        response.json['shopping_days'] == [1, 4] and \
            response.json['supermarket_sections'][0]['name'] == 'section1'




def test_update_user_preference(client: FlaskClient, auth_headers):
    response = patch_user_preferences(client, auth_headers)

    assert response.status_code == 200

def test_get_user_profile(client: FlaskClient, auth_headers):
    response = get_user_profile(client, auth_headers)

    assert response.status_code == 200