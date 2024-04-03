from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime

class Park(Base):
    __tablename__ ='park'

    id = Column(Integer, primary_key=True, index=True)
    park_name = Column(String,index=True)
    lat = Column(String,index=True)
    lng = Column(String,index=True)
    capacity = Column(Integer,index=True)
    empty_capacity = Column(Integer,index=True)
    work_hours = Column(String,index=True) 
    park_type = Column(String,index=True)
    free_time = Column(Integer,index=True)
    district = Column(String,index=True)
    is_open = Column(String,index=True)
    city = Column(String,index=True)
    enable = Column(String,index=True)
    registered_date = Column(DateTime,index=True)
 
