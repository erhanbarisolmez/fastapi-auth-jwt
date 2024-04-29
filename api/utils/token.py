from .conf import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

from api.deps import db_dependency
from datetime import timezone, timedelta, datetime
from fastapi import HTTPException, status
from  models.users import Users
from jose import jwt


def invalidate_old_tokens(user: Users, db: db_dependency):
    user.access_token = None
    user.refresh_token = None
    db.merge(user)
    db.commit()
    db.refresh(user)


def create_access_token(email: str, user_id: int, role: str, db: db_dependency):
    access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
      "sub": email,
      "id": user_id,
      "role": role,
      "exp": access_token_expires
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    save_token_to_db(user_id, encoded_jwt, None, access_token_expires,  db)
    return encoded_jwt

def create_refresh_token(email: str, user_id: int, role: str, db: db_dependency):
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {
      "sub": email,
      "id": user_id,
      "role": role,
      "exp" : refresh_token_expires
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    save_token_to_db(user_id,None, encoded_jwt, refresh_token_expires, db)

    return encoded_jwt


def refresh_access_token(email: str, token_expiry: datetime, db: db_dependency):
    
    user = db.query(Users).filter(Users.email == email).first()
    
    refresh_token_payload = jwt.decode(user.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    refresh_token_expiry = refresh_token_payload.get("exp")
    current_time = datetime.now(timezone.utc)
    
    
    if current_time < datetime.fromtimestamp(refresh_token_expiry, tz=timezone.utc):
        new_email = refresh_token_payload.get('sub')
        new_user_id = refresh_token_payload.get('id')
        new_role = refresh_token_payload.get('role')
        new_access_token= create_access_token(new_email, new_user_id, new_role, db)
        
        # Update the users table with the
        # new access token and remove old tokens
        
        user.access_token = new_access_token
        user.token_expiry = token_expiry
        save_token_to_db(user.id, new_access_token, user.refresh_token, token_expiry, db)
        
        user.token_expiry = token_expiry
        
        db.merge(user)
        db.commit()
        db.refresh(user)
        return {"access_token": new_access_token}
    else:
        return None

def save_token_to_db(user_id: int, access_token: str, refresh_token: str,token_expiry: datetime, db:db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_expiry = token_expiry
        db.merge(user)
        db.commit()
        db.refresh(user)
    else: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User not found')