from sqlalchemy.orm import Session
from database import get_db, crud, schemas
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus

from auth import authenticate_user, create_token, verify_token


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/users/me', response_model=schemas.User)
def read_current_user(user = Depends(authenticate_user)):
    return user


@app.get('/users/{user_id}', response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.')

    return db_user


@app.get('/users/', response_model=list[schemas.User], dependencies=[Depends(authenticate_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='E-mail já registrado.')

    user_from_db = crud.create_user(db=db, user=user)
    return user_from_db


@app.post('/users/{user_id}/items', response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db, item, user_id)


@app.get('/items/', response_model=list[schemas.Item], dependencies=[Depends(verify_token)])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip, limit)
    return items


@app.post('/token')
def get_token(data=Depends(create_token)):
    return data
