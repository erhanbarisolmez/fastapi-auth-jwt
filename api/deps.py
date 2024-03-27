from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from db.database import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
db_dependency = Annotated[Session, Depends(get_db)]