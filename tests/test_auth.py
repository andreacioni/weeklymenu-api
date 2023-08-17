import pytest

from conftest import TEST_EMAIL, TEST_PASSWORD
from test_shopping_list import get_all_shopping_list

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from weekly_menu.webapp.api.models import User


def register_user(client: FlaskClient, name: str, password: str, email: str):
    return client.post('/api/v1/auth/register', json={
        'name': name,
        'password': password,
        'email': email
    })


def test_bad_request_registration(client: FlaskClient):
    response = client.post('/api/v1/auth/register', json={})

    assert response.status_code == 400

    response = client.post('/api/v1/auth/register', json={'name': 'a'})

    assert response.status_code == 400


def test_user_creation(client: FlaskClient):
    response = client.post('/api/v1/auth/register', json={
        'name': "test2",
        'password': "password12",
        'email': "pippo@pluto.com"
    })

    user_id = response.json['_id']

    assert response.status_code == 200

    response = client.post('/api/v1/auth/token', json={
        'email': "test2@pluto.com",
        'password': 'wrong-password'
    })

    assert response.status_code == 401

    response = client.post('/api/v1/auth/token', json={
        'email': "pippo@pluto.com",
        'password': "password12"
    })

    assert response.status_code == 200 and response.json['access_token'] is not None

    User.objects(id=user_id).get().delete()


def test_shopping_list_creation_on_registration(client: FlaskClient):
    response = client.post('/api/v1/auth/register', json={
        'name': "test_usr",
        'password': "password",
        'email': "pippo@pluto.com"
    })

    assert response.status_code == 200

    response = client.post('/api/v1/auth/token', json={
        'email': "pippo@pluto.com",
        'password': "password"
    })

    assert response.status_code == 200 and response.json['access_token'] is not None

    response = get_all_shopping_list(
        client, {'Authorization': 'Bearer {}'.format(response.json['access_token'])})

    assert response.status_code == 200 and response.json['pages'] == 1 and len(
        response.json['results']) == 1


def test_password_reset(client: FlaskClient):
    response = register_user(client, name="John Smith",
                             password="password", email="jsmith@pluto.com")

    assert response.status_code == 200

    response = client.post('/api/v1/auth/reset_password', json={
        'email': "jsmith@pluto.com"
    })

    assert response.status_code == 204

    response = client.post('/api/v1/auth/reset_password', json={
        'email': "luke@pluto.com"
    })

    assert response.status_code == 404


def test_expires_in(client: FlaskClient, auth_headers):
    response = client.post('/api/v1/auth/token', json={
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    })

    assert response.status_code == 200 and response.json[
        'expires_in'] == 60 and response.json['user_id'] != None


def test_logout(client: FlaskClient):
    response = client.post('/api/v1/auth/logout', json={})

    assert response.status_code == 204
