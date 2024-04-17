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
  
  current_time = datetime.now(timezone.utc)
  token_expiry = datetime.fromtimestamp(user['exp'], tz=timezone.utc)
  if current_time >= token_expiry:
    new_access_token = create_access_token(user['email'], user['id'], user['role'], db)
    if new_access_token:
      user['access_token'] = new_access_token
    else:
      raise HTTPException(status_code=401, detail='Token refresh failed.')
    
  return {"User": user}
