from fastapi import WebSocket, FastAPI
from starlette.websockets import WebSocketDisconnect
import json
import asyncio  # asyncio modülünü ekleyin
from scapy.all import ARP, EtherDA, srp

socket = FastAPI()
devices = []
@socket.websocket("/camera")
async def connect_socket(websocket: WebSocket):

    await websocket.accept()
    print("WebSocket connection") 
    try:
        while True:
            data = await websocket.receive_text()
            print("SOCKET: ", data)
            if data not in ["scanDevices", "close"]:
                device_info = json.loads(data)
                if device_info not in devices:
                    devices.append(device_info)
                    await websocket.send_text(json.dumps(device_info))
            elif data == "scanDevices":
                for device in devices:
                    await websocket.send_text(json.dumps(device))
            elif data == "close":
                await websocket.send_text("Closing connection...")
                await websocket.close()  # Close the connection gracefully
                break
            await asyncio.sleep(0)
            print("devices", devices)

    except WebSocketDisconnect:
        pass


# def scan_network(ip_range: str):
#     print(f"scanning network: {ip_range}")
#     arp = ARP(pdst= ip_range)
#     ether = EtherDA()