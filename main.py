from fastapi import FastAPI, Request, HTTPException, status
from db.database import engine, Base
from models import park
from api.main import api_router
from fastapi.middleware.cors import CORSMiddleware
from api.middleware import refresh_token_middleware

Base.metadata.create_all(bind=engine)

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

@app.middleware("http")
async def apply_refresh_token_middleware(request: Request, call_next):
    authorization_header  = request.headers.get("Authorization")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")
    response = await refresh_token_middleware(request, call_next, token=authorization_header)
    print(response.headers)
    return response

app.include_router(api_router)

