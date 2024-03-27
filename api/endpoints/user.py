from fastapi import Depends, APIRouter, status,HTTPException
from typing import Annotated
from .auth import get_current_user
from  db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/user',
    tags=['user']
)

user_dependency  = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]



@router.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication Failed')
  return {"User": user}
