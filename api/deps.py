from fastapi import Depends, Form
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import Annotated
from db.database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


class OAuth2PasswordRequestFormCustom(OAuth2PasswordRequestForm):
    username: EmailStr = Form(...)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
db_dependency = Annotated[Session, Depends(get_db)]