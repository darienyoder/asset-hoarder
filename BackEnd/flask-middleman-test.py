import pytest
import importlib
import uuid;
from flask import session;
flask_middleman = importlib.import_module('flask-middleman')
app = flask_middleman.app

@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
    })
    with app.test_client() as client:
        yield client

@pytest.fixture
def junk_user():
    random_guid = str(uuid.uuid4()).replace('-', '')
    return {'username': 'adminaccounttestuser' + random_guid, 'password': 'Password123!'}

def test_get_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_get_assets(client):
    response = client.get('/assets')
    assert response.status_code == 200
    assert 'imageAssets' in response.json
    assert 'audioAssets' in response.json
    assert 'videoAssets' in response.json

def test_get_random_assets(client):
    response = client.get('/random_assets')
    assert response.status_code == 200
    assert 'assets' in response.json

# test /create_account /login /logout /user_toggle_save_asset /user_saved_assets
def test_account_routes(client, junk_user):
    user_info = junk_user

    with client.session_transaction() as sess:
        assert 'userId' not in sess

    response = client.get('/logout')
    assert response.status_code == 400
    assert response.json == 'user not logged in'

    response = client.post('/delete_account', data = user_info)
    assert response.status_code == 400
    assert response.json == 'user not logged in'

    response = client.post('/user_toggle_save_asset/1')
    assert response.status_code == 400
    assert response.json == 'user not logged in'

    response = client.get('/user_saved_assets')
    assert response.status_code == 400
    assert response.json == 'user not logged in'

    response = client.post('/login', data = {'username': '', 'password': ''})
    assert response.status_code == 400
    assert response.json == 'enter username and password'

    response = client.post('/login', data = user_info)
    assert response.status_code == 400
    assert response.json == 'wrong username or password'

    response = client.post('/create_account', data = {'username': '', 'password': ''})
    assert response.status_code == 400
    assert response.json == 'enter username and password'

    response = client.post('/create_account', data = user_info)
    assert response.status_code == 200
    assert response.json == 'succesfully created account'

    response = client.post('/create_account', data = user_info)
    assert response.status_code == 400
    assert response.json == 'username already exists'

    response = client.post('/login', data = user_info)
    assert response.status_code == 200
    assert response.json == 'successful login'
    with client.session_transaction() as sess:
        assert 'userId' in sess

    # currently logged in

    response = client.post('/login', data = user_info)
    assert response.status_code == 400
    assert response.json == 'already logged in'

    response = client.get('/user_saved_assets')
    assert response.status_code == 200
    assert 'imageAssets' in response.json
    assert 'audioAssets' in response.json
    assert 'videoAssets' in response.json

    response = client.post('/user_toggle_save_asset/0')
    assert response.status_code == 400
    assert response.json == 'no asset found'

    response = client.post('/user_toggle_save_asset/1')
    assert response.status_code == 200
    assert response.json == 'asset saved to user'

    response = client.post('/user_toggle_save_asset/1')
    assert response.status_code == 200
    assert response.json == 'asset unsaved from user'

    response = client.get('/logout')
    assert response.status_code == 200
    assert response.json == 'successfully logged out'
    with client.session_transaction() as sess:
        assert 'userId' not in sess

    response = client.post('/login', data = user_info)
    assert response.status_code == 200
    assert response.json == 'successful login'

    response = client.post('/delete_account', data = user_info)
    assert response.status_code == 200
    assert response.json == 'successfully deleted account and logged out'
    with client.session_transaction() as sess:
        assert 'userId' not in sess


