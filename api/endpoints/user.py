from fastapi import Depends, APIRouter, status,HTTPException
from typing import Annotated
from .auth import get_current_user, create_access_token
from  db.database import get_db
from sqlalchemy.orm import Session
from api.deps import db_dependency, OAuth2PasswordRequestFormCustom, oauth2_bearer
from datetime  import timedelta,datetime, timezone
router = APIRouter(
    prefix='/user',
    tags=['user']
)

user_dependency  = Annotated[str, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK)
async def read_users_me(user: user_dependency, db: db_dependency, token: Annotated[str, Depends(oauth2_bearer)],
):
  if user and token is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')
  
  return {"id": user['id'], 'Token': user['access_token'], 'email': user['email']}
