from fastapi import Depends, APIRouter, status,HTTPException
from typing import Annotated
from .auth import get_current_user, create_access_token, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,REFRESH_TOKEN_EXPIRE_MINUTES,create_refresh_token, save_token_to_db
from  db.database import get_db
from sqlalchemy.orm import Session
from api.deps import db_dependency, OAuth2PasswordRequestFormCustom, oauth2_bearer
from datetime  import timedelta,datetime, timezone
from jose import JWTError, jwt
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
  if not token: 
    refresh_token_payload = jwt.decode(user.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    email = refresh_token_payload.get('sub')
    user_id = refresh_token_payload.get('id')
    role = refresh_token_payload.get('role')
    new_access_token = create_access_token(email, user_id, role, db)
    user.access_token = new_access_token
    save_token_to_db(user.id, new_access_token, user.refresh_token, db)
    token = new_access_token

    user['access_token'] = create_access_token(user['email'], user["id"], user["access_token"])
    return {"id": user['id'], 'Token': new_access_token, 'email': user['email']}
  
  return {"id": user['id'], 'Token': user['access_token'], 'email': user['email']}
