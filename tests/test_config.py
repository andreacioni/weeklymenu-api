import pytest

from conftest import TEST_EMAIL, TEST_PASSWORD
from test_shopping_list import get_all_shopping_list

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from weekly_menu.webapp.api.models import Config


def test_get_config_for_version_code(client: FlaskClient):
    response = client.get('/api/v1/config/0')
    assert response.status_code == 404

    Config(min_version_code=0, properties={
        'testProp': 12
    }).save()

    response = client.get('/api/v1/config/0')
    assert response.status_code == 200 and response.json['properties']['testProp'] == 12

    response = client.get('/api/v1/config/100')
    assert response.status_code == 200 and response.json['properties']['testProp'] == 12

    Config(min_version_code=10, properties={
        'testProp': 13
    }).save()

    response = client.get('/api/v1/config/9')
    assert response.status_code == 200 and response.json['properties']['testProp'] == 12

    response = client.get('/api/v1/config/10')
    assert response.status_code == 200 and response.json['properties']['testProp'] == 13

    response = client.get('/api/v1/config/11')
    assert response.status_code == 200 and response.json['properties']['testProp'] == 13
