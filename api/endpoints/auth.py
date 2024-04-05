from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from starlette import status
from models.users import Users
from passlib.context import CryptContext
from jose import JWTError, jwt
from schemas.authSchema import CreateUserRequest, Token
from api.deps import db_dependency, oauth2_bearer, OAuth2PasswordRequestFormCustom

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
    role = create_user_request.role
    if role is None:
        role = 'user'
    create_user_model=Users(
        first_name = create_user_request.firstName,
        last_name = create_user_request.lastName,
        email = create_user_request.email,
        phone = create_user_request.phone,
        registered_date = create_user_request.registeredDate,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = role
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestFormCustom, Depends()],
                                 db: db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
    role = get_user_role(user)
    token = create_access_token(user.email, user.id, role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer', 'role':role}

def authenticate_user(email:str, password:str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
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

def get_user_role(user: Users):
    return user.role

        

async def get_token_authorization(authorization: str = Header(...)):
    if not authorization.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.split()[1]
    return token
        
