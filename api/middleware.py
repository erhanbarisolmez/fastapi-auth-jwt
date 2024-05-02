from .utils.conf import ALGORITHM,SECRET_KEY, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES
from .utils.token import create_access_token, create_refresh_token

from fastapi import Request, Depends
from fastapi.responses import Response
from jose import jwt, JWTError
from datetime import datetime,timedelta, timezone
from fastapi.routing import APIRoute
from typing import Annotated

from .exception import token_HTTPException
from .endpoints.auth import get_token_authorization
from .deps import oauth2_bearer
async def refresh_token_middleware(request: Request, call_next, token:  Annotated[str, Depends(oauth2_bearer)]):
  print("Middleware çalıştı")

  token_HTTPException(token)
  token_value = await get_token_authorization()
  response = await call_next(request)
  
  response.headers["X-Access-Token"] = token_value["access_token"]
  response.headers["X-Refresh-Token"] = token_value["refresh_token"]
      
  return response