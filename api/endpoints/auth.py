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
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES + 2 

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest,
                      create_token: Token ):
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
        role = role,
        access_token = create_token.access_token,
        refresh_token = create_token.refresh_token
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
    access_token = create_access_token(user.email, user.id, role, db)
    refresh_token = create_refresh_token(user.email, user.id, role, db)
    
    if access_token and refresh_token:
        save_token_to_db(user.id, access_token, refresh_token, db)
    else:
        raise HTTPException(status_code=401, detail='Token creation failed')
    
    return {'access_token': access_token, 'token_type': 'bearer', 'role': role, 'refresh_token': refresh_token}

@router.get("/email-control")
def get_user(db: db_dependency, email: str):
    user = db.query(Users).filter(Users.email == email).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail='User not found')
    
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
        token_expiry: str = payload.get('exp')
        
        if email:
            print('Email:', email)
        else:
            print('Email bulunamadı!')
        if user_id: 
            print('ID', user_id)
        else:
            print('id yok')
        if token_expiry: 
            print('Token', token_expiry)
        else:
            print('Token yok')
        
        user = db.query(Users).filter(Users.email == email, Users.id == user_id).first()
        if not user:
            raise credentials_exception

        if email is None or user_id is None:
            raise credentials_exception
        
        # # Refresh Token 
        # payload_refresh = jwt.decode(user.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        # email: str = payload_refresh.get('sub')
        # user_id: int = payload_refresh.get('id')
        # token_expiry: str = payload_refresh.get('exp')
        
        # if email:
        #     print('Refresh Email:', email)
        # else:
        #     print('Email bulunamadı!')
        # if user_id: 
        #     print('Refresh ID', user_id)
        # else:
        #     print('id yok')
        # if token_expiry: 
        #     print('Refresh Token', token_expiry)
        # else:
        #     print('Token yok')
            
        # # Access Token 
        # payload_access = jwt.decode(user.access_token, SECRET_KEY, algorithms=[ALGORITHM])
        # email: str = payload_access.get('sub')
        # user_id: int = payload_access.get('id')
        # token_expiry: str = payload_access.get('exp')
        
        # if email:
        #     print('Access Email:', email)
        # else:
        #     print('Email bulunamadı!')
        # if user_id: 
        #     print('Access ID', user_id)
        # else:
        #     print('id yok')
        # if token_expiry: 
        #     print('Access Token', token_expiry)
        # else:
        #     print('Token yok')
        
        role = get_user_role(user)
        
        current_time = datetime.now(timezone.utc)
        if current_time >= datetime.fromtimestamp(token_expiry, tz=timezone.utc):
            refresh_token_payload = jwt.decode(user.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            refresh_token_expiry = refresh_token_payload.get('exp')
            if current_time < datetime.fromtimestamp(refresh_token_expiry, tz=timezone.utc):
                new_access_token = create_access_token(email, user_id, role, db)
                if new_access_token:
                    save_token_to_db(user.id, new_access_token,user.refresh_token,db)
                    db.merge(user)
                    db.commit()
                return {'email': email, 'id': user_id, 'role': role, 'access_token': new_access_token}
        else:
            return {'email': email, 'id': user_id, 'role': role, 'access_token': user.access_token}

    except JWTError:
        raise credentials_exception

def get_user_role(user: Users):
    return user.role


def authenticate_user(email:str, password:str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email: str, user_id: int, role: str, db: db_dependency):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode({'sub': email, 'id': user_id, 'role': role, 'exp': expire.timestamp()}, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(email: str, user_id: int, role: str, db: db_dependency):
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode({'sub': email, 'id': user_id, 'role': role, 'exp': expire.timestamp()}, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_access_token_expiry(email: str, token_expiry: datetime, db: db_dependency):
    user = db.query(Users).filter(Users.email == email).first()
    current_time = datetime.now(timezone.utc)
    if current_time >= token_expiry:
        refresh_token_payload = jwt.decode(user.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = refresh_token_payload.get('sub')
        user_id = refresh_token_payload.get('id')
        role = refresh_token_payload.get('role')
        new_access_token= create_access_token(email, user_id, role, db)
        save_token_to_db(user_id, new_access_token, user.refresh_token,db)
        
        return new_access_token
    else:
        return None

def save_token_to_db(user_id: int, access_token: str, refresh_token: str, db:db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
        db.merge(user)
        db.commit()
    else: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User not found')
        



async def get_token_authorization(authorization: str = Header(...)):
    if not authorization.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.split()[1]
    return token
