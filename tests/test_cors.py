import pytest

from conftest import TEST_EMAIL, TEST_PASSWORD
from test_shopping_list import get_all_shopping_list

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from weekly_menu.webapp.api.models import User

allow_origin = 'http://localhost:8080/'


def test_cors_on_(client: FlaskClient):
    response = client.options('/api/v1', json={})
    assert response.status_code == 404


def test_cors_auth(client: FlaskClient):
    response = client.options('/api/v1/auth/token', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin
    response = client.options('/api/v1/auth/register', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin
    response = client.options('/api/v1/auth/reset_password', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin


def test_cors_recipes(client: FlaskClient):
    response = client.options('/api/v1/recipes', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin


def test_cors_ingredients(client: FlaskClient):
    response = client.options('/api/v1/ingredients', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin


def test_cors_shopping_list(client: FlaskClient):
    response = client.options('/api/v1/shopping-lists', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin


def test_cors_menu(client: FlaskClient):
    response = client.options('/api/v1/menus', json={})
    assert response.status_code == 200 and response.headers[
        'Access-Control-Allow-Origin'] == allow_origin
