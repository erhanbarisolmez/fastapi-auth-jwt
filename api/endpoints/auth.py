from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from db.database import get_db
from models.users import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from schemas.authSchema import CreateUserRequest, Token
from api.deps import db_dependency, oauth2_bearer

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model=Users(
        first_name = create_user_request.firstName,
        last_name = create_user_request.lastName,
        email = create_user_request.email,
        phone = create_user_request.phone,
        registered_date = create_user_request.registeredDate,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.email, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(email:str, password:str, db):  
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id}
    expires = datetime.utcnow() +expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Coult not validate user.')
        return {'email': email, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Coult not validate user.')
        
        
        
