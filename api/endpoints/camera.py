

from typing import List
from fastapi import APIRouter
from camera.main import devices


router = APIRouter(
  prefix='/camera',
  tags=['camera']
)



@router.get("/devices", response_model=List[dict])
async def get_devices():
  return devices

@router.get("/open/{device_id}")
async def open_camera(device_id: str):
  
  return {"message": f"Kamera {device_id} başarıyla açıldı"}
