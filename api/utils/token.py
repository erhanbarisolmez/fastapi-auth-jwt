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
    access_token_expires = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print(f"create_access_token  - {access_token_expires}")
    payload = {
      "sub": email,
      "id": user_id,
      "role": role,
      "exp": access_token_expires
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(email: str, user_id: int, role: str, db: db_dependency):
    refresh_token_expires = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    print(f"create_refresh_token  - {refresh_token_expires}")
    payload = {
      "sub": email,
      "id": user_id,
      "role": role,
      "exp" : refresh_token_expires
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def refresh_access_token(email: str, token_expiry: datetime, db: db_dependency):
    
    user = db.query(Users).filter(Users.email == email).first()
    
    
    if user:
        refresh_token_payload = jwt.decode(user.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        refresh_token_expiry = datetime.fromtimestamp(refresh_token_payload.get("exp"))
        current_time = datetime.now()
        
        access_token_payload = jwt.decode(user.access_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_expiry = datetime.fromtimestamp(access_token_payload.get("exp"))
        
        # print(f"refresh_access_token: current_time: ${current_time}")
        # print(f"refresh_access_token: access_token_expiry: ${token_expiry}")
        # print(f"refresh_access_token: refresh_token_expiry: ${refresh_token_expiry}")
        print("--------------------------------------------------------------------")
        refresh_token_is_valid = current_time < refresh_token_expiry
        print(f"refresh_token_is_valid: ${refresh_token_is_valid}")
        print("--------------------------------------------------------------------")


        if  refresh_token_is_valid:
            
            new_email = refresh_token_payload.get('sub')
            new_user_id = refresh_token_payload.get('id')
            new_role = refresh_token_payload.get('role')
            new_access_token= create_access_token(new_email, new_user_id, new_role, db)  
            new_access_token_payload = jwt.decode(new_access_token, SECRET_KEY, algorithms= [ALGORITHM])
            new_access_token_expiry = datetime.fromtimestamp(new_access_token_payload.get('exp'))
           
            new_access_token_isvalid = new_access_token_expiry > current_time
            print(f"new_access_token_is_valid : ${new_access_token_isvalid }")
            print("--------------------------------------------------------------------")

            if new_access_token_isvalid:
                
            # Update the users table with the
            # new access token and remove old tokens
            
              
                save_token_to_db(user.id, new_access_token, user.refresh_token, new_access_token_expiry, db)

                print("******************************************************")
                print(f"new_access_token > current_time  -   user.access_token: ${new_access_token_expiry}")
                print("-----------------------------------------------------------")
                print(f"new_access_token > current_time  -   user.token_expiry: ${new_access_token_expiry}")
                print("******************************************************")

            
                return {"access_token": new_access_token, "refresh_token": user.refresh_token}
            else:
                invalidate_old_tokens(user, db)
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
        else: 
            invalidate_old_tokens(user,db)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired or invalid")
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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