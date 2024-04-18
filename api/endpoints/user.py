from fastapi import Depends, APIRouter, status,HTTPException
from typing import Annotated
from .auth import get_current_user, create_access_token
from  db.database import get_db
from sqlalchemy.orm import Session
from api.deps import db_dependency
from datetime  import timedelta,datetime, timezone
router = APIRouter(
    prefix='/user',
    tags=['user']
)

user_dependency  = Annotated[dict, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK)
async def read_users_me(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')

  return {"User": user["access_token"]}
