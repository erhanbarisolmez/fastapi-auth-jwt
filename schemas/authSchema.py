from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CreateUserRequest(BaseModel):
    firstName: str
    lastName:str
    email: str
    phone: str
    registeredDate: Optional[datetime] = datetime.now()
    password: str
    role: str  = "user"
    access_token: Optional[str | None]=None
    refresh_token: Optional[str | None]=None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    
