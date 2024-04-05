from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime,func, Float, Boolean

class Park(Base):
    __tablename__ ='park'

    id = Column(Integer, primary_key=True, index=True)
    park_name = Column(String,index=True)
    lat = Column(Float,index=True)
    lng = Column(Float,index=True)
    capacity = Column(Integer,index=True)
    empty_capacity = Column(Integer,index=True)
    work_hours = Column(String,index=True) 
    park_type = Column(String,index=True)
    free_time = Column(Integer,index=True)
    district = Column(String,index=True)
    is_open = Column(Boolean,index=True)
    city = Column(String,index=True)
    enable = Column(Boolean,index=True)
    registered_date = Column(DateTime,index=True, default=func.now())
 
