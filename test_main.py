import jwt

from http import HTTPStatus
from unittest import mock, TestCase
from fastapi.testclient import TestClient

from auth import INVALID_TOKEN_FORMAT, TOKEN_EXPIRED
from main import app, get_db, authenticate_user, verify_token
from database.models import User


def override_get_db(): ...

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class UserTestCase(TestCase):

    def override_authenticate_user(self):
        pass

    @mock.patch('database.crud.get_users')
    def test_read_users(self, crud_get_users):
        users = [{
            'id': 1,
            'email': 'teste@teste.com',
            'is_active': False,
            'items': []
        }]

        app.dependency_overrides[authenticate_user] = self.override_authenticate_user

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


ALGORITHM = 'HS256'
SECRET_KEY = 'minha chave secreta'


class ItemTestCase(TestCase):
    def setUp(self):
        self.items = [{"title": "string", "description": "string", "id": 1, "user_id": 0}]
        self.user = User(email="fakeemail", hashed_password="password")
        self.token = jwt.encode({"email": self.user.email}, SECRET_KEY, algorithm=ALGORITHM)

    def override_verify_token(self):
        pass

    @mock.patch("database.crud.get_items")
    def test_get_items(self, get_items):
        app.dependency_overrides[verify_token] = self.override_verify_token
        get_items.return_value = self.items

        response = client.get("/items/", headers={'Authorization': f'Bearer {self.token}'})
        assert response.status_code == HTTPStatus.OK
        assert response.json() == self.items


class AuthTestCase(TestCase):
    def setUp(self):
        self.user = User(email="teste@teste.com", hashed_password="senha")
        self.token = jwt.encode({"email": self.user.email}, SECRET_KEY, algorithm=ALGORITHM)

    @mock.patch('database.crud.get_user_by_email')
    @mock.patch("auth.validate_user")
    def test_create_token(self, validate_user, get_user_by_email):
        validate_user.return_value = self.user
        get_user_by_email.return_value = True

        response = client.post("/token/", json={"email": self.user.email, "password": self.user.hashed_password})
        token = response.json()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert response.status_code == HTTPStatus.OK
        assert payload.get("email") == self.user.email

    @mock.patch("database.crud.get_user_by_email")
    @mock.patch("database.crud.get_items")
    def test_valid_token(self, get_items, get_user_by_email):
        get_items.return_value = []
        get_user_by_email.return_value = self.user
        response = client.get("/items/", headers={"Authorization": f"Bearer {self.token}"})
        assert response.status_code == HTTPStatus.OK

    @mock.patch("database.crud.get_user_by_email")
    @mock.patch("database.crud.get_items")
    def test_invalid_token_format(self, get_items, get_user_by_email):
        get_items.return_value = []
        get_user_by_email.return_value = self.user
        response = client.get("/items/", headers={"Authorization": "Bearer xxxxxx"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"detail": INVALID_TOKEN_FORMAT}

    @mock.patch("database.crud.get_user_by_email")
    @mock.patch("database.crud.get_items")
    def test_invalid_token(self, get_items, get_user_by_email):
        get_items.return_value = []
        get_user_by_email.return_value = self.user
        token = jwt.encode({"email": self.user.email}, "outra chave secreta", algorithm=ALGORITHM)
        response = client.get("/items/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"detail": INVALID_TOKEN_FORMAT}

    @mock.patch("database.crud.get_user_by_email")
    @mock.patch("database.crud.get_items")
    def test_expired_token(self, get_items, get_user_by_email):
        from datetime import datetime, timedelta
        get_items.return_value = []
        get_user_by_email.return_value = self.user
        expiration_date = datetime.now() + timedelta(minutes=15)
        token = jwt.encode({"email": self.user.email, 'exp': expiration_date}, SECRET_KEY, algorithm=ALGORITHM)
        response = client.get("/items/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"detail": TOKEN_EXPIRED}