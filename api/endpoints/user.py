from fastapi import Depends, APIRouter, status,HTTPException
from typing import Annotated
from .auth import get_current_user, create_access_token, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,REFRESH_TOKEN_EXPIRE_MINUTES,create_refresh_token, save_token_to_db
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
  

  
  return {"id": user.id, 'Token': user.access_token, 'email': user.email}
