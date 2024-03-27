from db.database import Base
from sqlalchemy import Column, Integer, String

class Park(Base):
    __tablename__ ='park'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    addres = Column( String, unique=True)

