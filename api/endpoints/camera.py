from typing import List
from fastapi import APIRouter
from fastapi import FastAPI, Request

import cv2
import subprocess
import re
import json
import socket
import threading
from pathlib import Path

from pydantic import BaseModel

router = APIRouter(
  prefix='/camera',
  tags=['camera']
)

class Device(BaseModel):
    ip: str
    label: str

devices = []


# Thread 
# def scan_ip_range(start_ip, end_ip, port, devices):
#   for ip in range(start_ip, end_ip):
#     ip_address = f"192.168.4.{ip}"
#     try:
#       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.settimeout(1)
#         s.connect((ip_address, port))
#         devices.append({"ip": ip_address, "port": port, "label": f"Device {ip}"})
#     except (socket.timeout, ConnectionRefusedError):
#       pass
    
def ping_ip_range(start_ip, end_ip, devices):
  for ip in range(start_ip, end_ip):
    ip_address = f"192.168.4.{ip}"
    try:
      output = subprocess.check_output(["ping", "-c", "1", "-W", "1", ip_address], stderr=subprocess.DEVNULL)
      if "1 received" in output.decode("utf-8"):
        devices.append({"ip": ip_address, "label": f"Devices {ip}"})
    except subprocess.CalledProcessError:
      pass


@router.get("/devices", response_model=List[Device])
async def get_devices():
  return devices

@router.get("/scan")
async def scan_devices():
  """Scan the network for devices."""
  devices.clear()
  # for ip in range(60, 100):
  #   ip_address = f"192.168.4.{ip}"
  #   try:
  #     subprocess.check_output(["ping", "-c", "1", ip_address], stderr=subprocess.DEVNULL)
  #     devices.append({"ip": ip_address, "deviceId": str(ip), "label": f"Device {ip}"})
  #   except subprocess.CalledProcessError:
  #     pass
  # return devices
  

  threads = []
  num_threads = 10  # Paralel işlem sayısı
  # start_ip = 50
  # end_ip = 90
  port = 3000
  ip_range = range(1,255)

  # # paralel işlemleri başlat
  # for i in range(num_threads):
  #   thread = threading.Thread(target=scan_ip_range, args=(start_ip, end_ip, port, devices))
  #   threads.append(thread)
  #   thread.start()
  
  for i in range(num_threads):
    start_ip = ip_range.start + (ip_range.stop - ip_range.start) //num_threads * i
    end_ip = ip_range.start +(ip_range.stop - ip_range.start) // num_threads * (i+1)
    thread = threading.Thread(target=ping_ip_range, args=(start_ip, end_ip, devices))
    threads.append(thread)
    thread.start()
    
  # tüm thread'ları bitir
  for thread in threads:
    thread.join()
    
  return devices

@router.post("/abone")
async def scan_device( label: str, request: Request):
    """Handle the scan request from each device."""
    client_host = request.client.host
    ip = client_host
    device = Device(ip=ip, label=label)
    devices.append(device)
    return {"message": "Device scanned successfully"}
  

@router.get("/open/{ip_address}")
async def open_camera(ip_address: str):
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
    if ip_address:
        save_directory = Path("camera/images/")
        image_path = save_directory / f"camera_{ip_address}.jpg"
        cv2.imwrite(str(image_path), frame)
        return {"status": "Image captured", "image_path": str(image_path)}
  cap.release()
  cv2.destroyAllWindows()
  return {"status": "Camera closed"}


