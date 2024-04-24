from fastapi import HTTPException, status


def token_HTTPException(token):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired.",
        )


def park_HTTPException(park):
    if not park:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Park not found"
        )


def user_HTTPException(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
