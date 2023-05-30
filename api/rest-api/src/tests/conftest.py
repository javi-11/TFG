import pytest
import sys

sys.path.append("C:\\Users\\javit\\Desktop\\TFG\\api\\rest-api\\src")

from api.app import create_app, clear_app


@pytest.fixture()
def app():
    app = create_app(True)
    
    yield app


@pytest.fixture
def client(app,request):

    return app.test_client()
 
def pytest_sessionfinish(session, exitstatus):
    clear_app()
