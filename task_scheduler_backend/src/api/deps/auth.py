import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from src.api.db.session import get_db
from src.api.models.user import User
from src.api.security.jwt import decode_token

_bearer = HTTPBearer(auto_error=False)


# PUBLIC_INTERFACE
def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that returns the authenticated user based on Bearer JWT."""
    if not creds or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = creds.credentials
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = uuid.UUID(str(sub))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
