from http import HTTPStatus
from unittest import mock, TestCase
from fastapi.testclient import TestClient

from main import app, get_db


def override_get_db(): ...

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class UserTestCase(TestCase):

    @mock.patch('database.crud.get_users')
    def test_read_users(self, crud_get_users):
        users = [{
            'id': 1,
            'email': 'teste@teste.com',
            'is_active': False,
            'items': []
        }]

        crud_get_users.return_value = users
        response = client.get('/users/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        assert response.status_code == HTTPStatus.OK  # Outra opção de como usar o 'assert' para a mesma verificação.
        self.assertEqual(response.json(), users)
        assert response.json() == users  # Outra opção de como usar o 'assert' para a mesma verificação.


    @mock.patch('database.crud.get_user_by_email')
    @mock.patch('database.crud.create_user')
    def test_create_user(self, create_user, get_user_by_email):
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


    def test_invalid_user_creation(self):
        response = client.post('/users/', json={})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


    @mock.patch('database.crud.get_user_by_email')
    def test_invalid_user_creation_repeated_email(self, get_user_by_email):
        get_user_by_email.return_value = True
        response = client.post('/users/', json={
            'email': 'well@fiap.com.br',
            'password': 'abcdde'
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @mock.patch('database.crud.get_items')
    def test_read_items(self, crud_get_items):
        items = [{
            'id': 1,
            'user_id': 1,
            'title': 'Geladeira',
            'description': 'teste'
        }]
        crud_get_items.return_value = items
        response = client.get('/items/')

        assert response.status_code == HTTPStatus.OK
        assert response.json() == items
