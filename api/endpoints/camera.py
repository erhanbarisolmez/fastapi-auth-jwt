from typing import List
from fastapi import APIRouter
from camera.main import devices
import cv2


router = APIRouter(
  prefix='/camera',
  tags=['camera']
)



@router.get("/devices", response_model=List[dict])
async def get_devices():
  return devices

@router.get("/open/{device_id}")
async def open_camera(device_id: str):
  """Open the camera for the specified device."""
  cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    return {"error": "cannot open camera"}
  while True:
    ret, frame = cap.read()
    if not ret:
      break
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    
  cap.release()
  cv2.destroyAllWindows()
  return {"status": "Camera closed"}
