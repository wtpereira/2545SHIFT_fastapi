import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class User(BaseModel):
    email: str
    name: str = ''


@app.get('/')
def hello_world(name: str):
    return {'Hello': name}


@app.post('/users', status_code=201)
def create_user(user: User):
    if '@' not in user.email:
        raise HTTPException(400, 'Informe um e-mail válido.')

    return {
        "id": random.randint(0, 100),
        "name": user.name,
        "email": user.email
    }



@app.patch('/users/{user_id}')
def partial_update_user(user_id: int, user: User):
    if '@' not in user.email:
        raise HTTPException(400, 'Informe um e-mail válido (PATCH).')

    return {
        "id": user_id,
        "name": user.name,
        "email": user.email
    }


@app.put('/users/{user_id}/{item_id}')
def update_user(user_id:int, item_id:int, user: User):
    if '@' not in user.email:
        raise HTTPException(400, 'Informe um e-mail válido (PUT).')

    return {
        "id": user_id,
        "name": user.name,
        "email": user.email
    }


users = {
    1: {'name': 'Well', 'email': 'well@fiap.com.br'},
    2: {'name': 'Teste', 'email': 'teste@teste.com.br'}
}


@app.delete('/users/{user_id}')
def delete_user(user_id: int):
    try:
        del users[user_id]
        return users
    except KeyError:
        raise HTTPException(400, 'Usuário não exite!')
