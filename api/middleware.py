from .utils.conf import ALGORITHM,SECRET_KEY, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES
from .utils.token import create_access_token, create_refresh_token

from fastapi import Request
from fastapi.responses import Response
from jose import jwt, JWTError
from datetime import datetime,timedelta, timezone
from fastapi.routing import APIRoute

async def refresh_token_middleware(request: Request, call_next):
  print("Middleware çalıştı")
  response = await call_next(request)
  if "Authorization" in response.headers:
    authorization = response.headers["Authorization"]
    if authorization.startswith("Bearer"):
      token = authorization.split()[1]
   
      try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is not None:
          exp_datetime = datetime.fromtimestamp(exp)
          now = datetime.now()
          if now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES) >= exp_datetime:
            if  now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  >= exp_datetime:
              new_token = create_access_token(data=payload)
            new_refresh_token = create_refresh_token(data=payload)
            
            response.headers["X-New-Token"] = new_token
            response.headers["X-Refresh-Token"] = new_refresh_token
            print(response["X-New-Token"])
      except JWTError:
        JWTError(print(f"Invalid token : {token}"))
  return response