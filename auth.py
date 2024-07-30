import jwt

from datetime import datetime, timedelta, UTC
from http import HTTPStatus
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database import crud
from pydantic import BaseModel

from database import get_db

security = HTTPBasic()

INVALID_TOKEN_FORMAT = 'Invalid Token Format!'
TOKEN_EXPIRED = 'Token Expired!'

def validate_user(db, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return

    if not user.hashed_password == f'{password}notreallyhashed':
        return

    return user


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = validate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password', headers={'WWW-Authenticate': 'Basice'})

    return user


token = HTTPBearer()

SECRET_KEY = 'minha chave secreta'

class EmailAuthentication(BaseModel):
    email: str
    password: str


def verify_token(token: HTTPAuthorizationCredentials = Depends(token), db=Depends(get_db)):
    try:
        data = jwt.decode(token.credentials, SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.DecodeError:
        raise HTTPException(HTTPStatus.BAD_REQUEST, INVALID_TOKEN_FORMAT)
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(HTTPStatus.BAD_REQUEST, TOKEN_EXPIRED)

    email = data.get('email')
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid Credentials')

    return data


def create_token(credentials: EmailAuthentication, db=Depends(get_db)):
    user = validate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password')

    expiration_date = datetime.now(UTC) + timedelta(minutes=15)
    token = jwt.encode({'email': credentials.email, 'exp': expiration_date}, SECRET_KEY, algorithm='HS256')
    return token
