from fastapi import FastAPI
from db.database import engine, Base
from models import park
from api.main import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api_router)

