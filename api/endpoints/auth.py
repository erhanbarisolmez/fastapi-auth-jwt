from datetime import timedelta, datetime, timezone
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
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest,
                      create_token:Token ):
    role = create_user_request.role
    exp = create_token.access_token
    if role is None:
        role = 'user'
    create_user_model=Users(
        first_name = create_user_request.firstName,
        last_name = create_user_request.lastName,
        email = create_user_request.email,
        phone = create_user_request.phone,
        registered_date = create_user_request.registeredDate,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = role,
        exp = exp
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestFormCustom, Depends()],
    db: db_dependency
    ):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
    role = get_user_role(user)
    token = create_access_token(user.email, user.id, role, timedelta(minutes=1))
    if token:
        user.exp = token
        db.add(user)
        db.commit()
    return {'access_token': token, 'token_type': 'bearer', 'role':role}

@router.get("/email-control")
def get_user(db: db_dependency, email: str):
    user = db.query(Users).filter(Users.email == email).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail='User not found')


def authenticate_user(email:str, password:str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate user.',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise credentials_exception

        # Check if access token has expired
        if datetime.now() >= datetime.fromtimestamp(payload['exp']):
            try:
                # Attempt to refresh token using refresh token from payload
                refresh_token = payload.get("refresh_token")  # Extract refresh token from access token
                if refresh_token is not None:
                    return await refresh_token_helper(refresh_token, user_id, email, db)
                else:
                    # No refresh token included, raise unauthorized error
                    raise credentials_exception
            except JWTError:
                raise credentials_exception  # Handle JWT errors during refresh token verification

        # Access token is valid, return user information
        user = db.query(Users).filter(Users.email == email, Users.id == user_id).first()
        role = get_user_role(user)
        return {'email': email, 'id': user_id, 'role': role}

    except JWTError:
        raise credentials_exception


def create_refresh_token(user_id: int, expires_delta: timedelta):
    encode = {'sub': user_id, 'refresh': True}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'refresh_exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def refresh_token_helper(refresh_token: str, user_id: int, email: str, db):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        # Verify if refresh token belongs to the same user making the request
        if payload.get("id") != user_id:
            raise JWTError("Invalid refresh token")

        # Check refresh token expiration
        refresh_token_expire = datetime.fromtimestamp(payload["refresh_exp"],timezone.utc)
        if datetime.now(timezone.utc) >= refresh_token_expire:
             new_token = create_refresh_token(email, user_id, user.role, timedelta(minutes=1))
             user = db.query(Users).filter(Users.id == user_id).first()
             user.exp = new_token
             db.merge(user)
             db.commit()

        raise JWTError("Refresh token expired")
    except:
        pass
        


def get_user_role(user: Users):
    return user.role

async def get_token_authorization(authorization: str = Header(...)):
    if not authorization.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.split()[1]
    return token
        
        
        


