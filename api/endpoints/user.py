from fastapi import Depends, APIRouter, status,HTTPException
from typing import Annotated

from api.exception import token_HTTPException, user_HTTPException
from models.users import Users
from .auth import get_current_user
from  db.database import get_db
from sqlalchemy.orm import Session
from api.deps import db_dependency, OAuth2PasswordRequestFormCustom, oauth2_bearer
from datetime  import timedelta,datetime, timezone
from jose import JWTError, jwt
from schemas.authSchema import CreateUserRequest
router = APIRouter(
    prefix='/user',
    tags=['user']
)

user_dependency  = Annotated[str, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK)
async def read_users_me(user: user_dependency, db: db_dependency, token: Annotated[str, Depends(oauth2_bearer)],
):
  if not user:
    raise HTTPException(status_code=401, detail='Authentication Failed')  
  
  return user

# @router.get("/active_user", status_code=status.HTTP_200_OK)
# async def active_users(user: user_dependency, db:db_dependency, token:Annotated[str, Depends(oauth2_bearer)]):
#     user_HTTPException(user)
#     token_HTTPException(token)
    
#     current_time = datetime.now()
#     active_users = db.query(Users).filter(
#         Users.is_active == True,
#         Users.token_expiry < current_time
#     ).all()
#     return active_users