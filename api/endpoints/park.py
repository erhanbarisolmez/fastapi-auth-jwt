from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from api.deps import db_dependency, oauth2_bearer
from schemas.parkSchema import CreateParkRequest
from schemas.authSchema import CreateUserRequest
from models.park import Park
from .auth import login_for_access_token, get_current_user
from datetime import timedelta, datetime

router = APIRouter(prefix="/park", tags=["park"])


@router.post("/create_park", status_code=status.HTTP_201_CREATED)
async def create_park(
    db: db_dependency,
    create_park_schema: CreateParkRequest,
    token: Annotated[str, Depends(oauth2_bearer)],
):


    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired.",
        )

    

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
