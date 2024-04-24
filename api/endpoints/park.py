from typing import Annotated, List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from api.deps import db_dependency, oauth2_bearer
from schemas.parkSchema import CreateParkRequest, ParkUpdateSchema
from schemas.authSchema import CreateUserRequest
from models.park import Park
from datetime import timedelta, datetime
from api.exception import token_HTTPException, park_HTTPException, user_HTTPException
from .auth import get_current_user

router = APIRouter(prefix="/park", tags=["park"])

user_dependency  = Annotated[str, Depends(get_current_user)]

@router.post("/create_park", status_code=status.HTTP_201_CREATED)
async def create_park(
    db: db_dependency,
    user: user_dependency,
    create_park_schema: CreateParkRequest,
    token: Annotated[str, Depends(oauth2_bearer)],
):
    
    user_HTTPException(user)

    token_HTTPException(token)

    create_park_model = Park(
        park_name=create_park_schema.parkName,
        lat=create_park_schema.lat,
        lng=create_park_schema.lng,
        capacity=create_park_schema.capacity,
        empty_capacity=create_park_schema.emptyCapacity,
        work_hours=create_park_schema.workHours,
        park_type=create_park_schema.parkType,
        free_time=create_park_schema.freeTime,
        district=create_park_schema.district,
        is_open=create_park_schema.isOpen,
        city=create_park_schema.city,
        enable=create_park_schema.enable,
        registered_date=create_park_schema.registeredDate,
    )
    db.add(create_park_model)
    db.commit()
    return {"message": "Successfully created a new park."}



@router.get("/read_park/{park_id}", status_code=status.HTTP_200_OK)
async def read_park_id(
    park_id: int,
    token: Annotated[str, Depends(oauth2_bearer)],
    db:db_dependency):
    
    token_HTTPException(token)
    
    park = db.query(Park).filter(Park.id == park_id).first()
    park_HTTPException(park)
    
    return park


    

@router.get("/read_park_all", status_code=status.HTTP_200_OK)
async def read_park_all(
    db:db_dependency,
    token: Annotated[str, Depends(oauth2_bearer)],
):
    
    token_HTTPException(token)
    
    park_list = db.query(Park).all()
    
    return park_list

@router.put("/update_park/{park_id}", status_code=status.HTTP_200_OK,  response_model=ParkUpdateSchema)
async def update_park(
    park_id: int,
    park_data: Annotated[dict, Body(...), Depends(ParkUpdateSchema)],
    token: Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency
):
    token_HTTPException(token)
    
    updated_park =  db.query(Park).filter(Park.id == park_id).first()
    park_HTTPException(updated_park)
    
    
    updated_fields = {
        "park_name": park_data.parkName,
        "lat": park_data.lat,
        "lng": park_data.lng,
        "capacity": park_data.capacity,
        "empty_capacity": park_data.emptyCapacity,
        "work_hours": park_data.workHours,
        "park_type": park_data.parkType,
        "free_time": park_data.freeTime,
        "district": park_data.district,
        "is_open": park_data.isOpen,
        "city": park_data.city,
        "enable": park_data.enable
    }

    
    for field, value in updated_fields.items():
        if value is not None:
            setattr(updated_park, field, value)
    
    db.commit()
    db.refresh(updated_park)
    
    return updated_park

    

@router.delete("/delete/{park_id}", status_code=status.HTTP_200_OK)
async def delete_park(
    park_id: int,
    token:Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency):
    
    token_HTTPException(token)
    
    park = db.query(Park).filter(Park.id == park_id).first()
    park_HTTPException(park_id)
    
    db.delete(park)
    db.commit()
    
    return park