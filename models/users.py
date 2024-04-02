from db.database import Base
from sqlalchemy import Column, Integer, String,DateTime

class Users(Base):
    __tablename__ ='users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20), index=True)
    last_name = Column(String(20),index=True )
    email = Column(String(20), unique=True, index=True)
    phone = Column(String(10), unique=True, index=True)
    registered_date = Column(DateTime, index=True )
    hashed_password = Column(String)
    role = Column(String, nullable=True, default='user')  # user or

