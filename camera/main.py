from fastapi import WebSocket, FastAPI
from starlette.websockets import WebSocketDisconnect

socket = FastAPI()


@socket.websocket("/camera")
async def connect_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "openCamera":
                await websocket.send_text("openCamera")
                
    except WebSocketDisconnect:
        pass