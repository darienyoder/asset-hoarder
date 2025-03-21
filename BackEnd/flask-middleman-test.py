import pytest
import importlib
flask_middleman = importlib.import_module('flask-middleman')
app = flask_middleman.app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
