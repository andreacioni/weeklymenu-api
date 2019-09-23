import pytest
import jwt

from flask.testing import FlaskClient
from weekly_menu import create_app

from weekly_menu.webapp.api.models import Ingredient, Menu, Recipe, User, ShoppingList
from weekly_menu.webapp.api.v1.auth import encode_password

TEST_USERNAME = 'test'
TEST_PASSWORD = 'a@b.it'
TEST_EMAIL = 'pippofranco'

@pytest.fixture(autouse=True)
def clear_db():
  yield
  #Clear all collections
  User.drop_collection()
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

@pytest.fixture
def auth_headers(app):
  user = User()
  user.username = TEST_USERNAME
  user.email = TEST_EMAIL
  user.password = encode_password(TEST_EMAIL)
  user.save()

  valid_token = jwt.encode({'username':'username'}, app.config['SECRET_KEY']).decode('utf-8')
  headers = {
      'Authorization': 'Bearer {}'.format(valid_token)
  }

  return headers