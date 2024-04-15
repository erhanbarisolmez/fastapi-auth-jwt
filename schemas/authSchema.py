from pydantic import BaseModel, EmailStr
from datetime import datetime

class CreateUserRequest(BaseModel):
    firstName: str
    lastName:str
    email: str
    phone: str
    registeredDate: datetime
    password: str
    role: str  = "user"
    exp: str

class Token(BaseModel):
    access_token:str
    token_type:str
    
