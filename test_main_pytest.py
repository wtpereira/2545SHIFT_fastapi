from http import HTTPStatus
from fastapi.testclient import TestClient
from unittest import mock
from main import app, get_db


def override_get_db(): ...

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@mock.patch('database.crud.get_users')
def test_read_users(get_users):
    users = [{
        'id': 1,
        'email': 'teste@teste.com',
        'is_active': False,
        'items': []
    }]
    get_users.return_value = users
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK


@mock.patch('database.crud.get_user_by_email')
@mock.patch('database.crud.create_user')
def test_create_user(create_user, get_user_by_email):
    user_data = {
        'id': 1,
        'email': 'teste@teste.com',
        'is_active': False,
        'items': []
    }

    create_user.return_value = user_data
    get_user_by_email.return_value = None

    response = client.post('/users/', json={
        'email': 'well@fiap.com.br',
        'password': 'abcdde'
    })
    print(response)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_data


def test_invalid_user_creation():
    response = client.post('/users/', json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@mock.patch('database.crud.get_user_by_email')
def test_invalid_user_creation_repeated_email(get_user_by_email):
    get_user_by_email.return_value = True
    response = client.post('/users/', json={
        'email': 'well@fiap.com.br',
        'password': 'abcdde'
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
