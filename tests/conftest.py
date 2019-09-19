import pytest

from flask.testing import FlaskClient
from weekly_menu import create_app

from weekly_menu.webapp.api.models import Ingredient, Menu, Recipe, User, ShoppingList

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
def client():
    app = create_app('pytest-config')
    testing_client = app.test_client()
 
    return testing_client