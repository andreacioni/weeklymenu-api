import pytest

from flask.testing import FlaskClient
from weekly_menu import create_app

@pytest.fixture(scope='session')
def client():
    app = create_app('pytest-config')
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
 
    yield testing_client
 
    ctx.pop()