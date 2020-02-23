import pytest
import jwt

from flask.testing import FlaskClient
from weekly_menu import create_app

from weekly_menu.webapp.api.models import Ingredient, Menu, Recipe, User, ShoppingList
from weekly_menu.webapp.api.v1.auth import encode_password

TEST_USERNAME = 'test'
TEST_PASSWORD = 'pippo@franco.it'
TEST_EMAIL = 'pippo@franco123'

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
  return create_app('pytest-config')

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def auth_headers(client: FlaskClient):
  response = client.post('/api/v1/auth/register', json={
    'username':TEST_USERNAME, 
    'password':TEST_PASSWORD,
    'email':TEST_EMAIL
    })
  
  response = client.post('/api/v1/auth/token', json={
    'username':TEST_USERNAME, 
    'password':TEST_PASSWORD
    })

  headers = {
      'Authorization': 'Bearer {}'.format(response.json['access_token']),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
  }

  return headers