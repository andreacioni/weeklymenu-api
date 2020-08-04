import pytest
import jwt
import os

from flask.testing import FlaskClient
from weekly_menu import create_app

from weekly_menu.webapp.api.models import Ingredient, Menu, Recipe, User, ShoppingList
from weekly_menu.webapp.api.v1.auth import encode_password

TEST_USERNAME = 'test'
TEST_PASSWORD = 'pippo@franco.it'
TEST_EMAIL = 'pippo@franco123'

TEST_USERNAME_2 = 'test2'
TEST_PASSWORD_2 = 'pippo2@franco.it'
TEST_EMAIL_2 = 'pippo2@franco123'

@pytest.fixture(autouse=True)
def clear_db():
  yield
  #Clear all collections
  #User.drop_collection()
  Recipe.drop_collection()
  Menu.drop_collection()
  Ingredient.drop_collection()
  ShoppingList.drop_collection()

@pytest.fixture(scope='session')
def app():
  config_name = os.environ.get('CONFIG_NAME', 'pytest')
  return create_app(config_name)

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def auth_headers(client: FlaskClient):
  return register_and_login(client, TEST_USERNAME, TEST_PASSWORD, TEST_EMAIL)

@pytest.fixture(scope='session')
def auth_headers_2(client: FlaskClient):
  return register_and_login(client, TEST_USERNAME_2, TEST_PASSWORD_2, TEST_EMAIL_2)


def register_and_login(client, user, password, email):
  response = client.post('/api/v1/auth/register', json={
  'username': user, 
  'password': password,
  'email': email
  })

  response = client.post('/api/v1/auth/token', json={
    'username': user, 
    'password': password
    })

  headers = {
      'Authorization': 'Bearer {}'.format(response.json['access_token']),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
  }

  return headers