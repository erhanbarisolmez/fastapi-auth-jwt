import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, Base
from api.main import api_router
import multiprocessing
from camera.main import socket
# Database initialization
Base.metadata.create_all(bind=engine)

# First FastAPI app for general API routes
app = FastAPI()

# CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

def run_app():
    uvicorn.run(app, host="0.0.0.0", port=8000 )

def socket_camera():
    uvicorn.run(socket, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_app)
    p2 = multiprocessing.Process(target=socket_camera)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
