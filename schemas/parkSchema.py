from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CreateParkRequest(BaseModel):
  parkName: str | None = None
  lat: float | None = None
  lng: float | None = None
  capacity: int | None = None
  emptyCapacity: int | None = None
  workHours: str | None = None
  parkType: str | None = None
  freeTime: int | None = None
  district: str | None = None
  isOpen: bool | None = None
  city: str | None = None
  enable: bool | None = None
  registeredDate: Optional[datetime] = datetime.now()
  
  
class ParkUpdateSchema(BaseModel):
  parkName: Optional[str | None] = None
  lat: Optional[float | None] = None
  lng: Optional[float | None] = None
  capacity: Optional[int | None] = None
  emptyCapacity: Optional[int | None] = None
  workHours: Optional[str | None] = None
  parkType: Optional[str | None] = None
  freeTime: Optional[int | None] = None
  district: Optional[str | None] = None
  isOpen: Optional[bool | None] = None
  city: Optional[str | None] = None
  enable: Optional[bool | None] = None
  

  