from fastapi import WebSocket, FastAPI
from starlette.websockets import WebSocketDisconnect

socket = FastAPI()
devices = []

@socket.websocket("/camera")
async def connect_socket(websocket: WebSocket):
    
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data =="scanDevices":
                for device in devices:
                    await websocket.send_text(device)
            elif data == "close":
                await websocket.close()
                break
           
                
    except WebSocketDisconnect:
        pass
    
    
    