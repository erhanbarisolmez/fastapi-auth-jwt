from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CreateParkRequest(BaseModel):
  parkName: str
  lat: float
  lng: float
  capacity: int
  emptyCapacity: int
  workHours: str
  parkType: str
  freeTime: int
  district: str
  isOpen: bool
  city: str
  enable: bool
  registeredDate: Optional[datetime]
  