from pydantic import BaseModel
from datetime import datetime

class CreateParkRequest(BaseModel):
  parkName: str
  lat: str
  lng: str
  capacity: int
  emptyCapacity: int
  workHours: str
  parkType: str
  freeTime: int
  district: str
  isOpen: str
  city: str
  enable: str
  registeredDate: datetime