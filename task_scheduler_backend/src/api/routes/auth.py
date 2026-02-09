from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.session import get_db
from src.api.deps.auth import get_current_user
from src.api.models.user import User
from src.api.schemas.auth import LoginRequest, MeResponse, SignupRequest, TokenResponse
from src.api.security.jwt import create_access_token
from src.api.security.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a user account and returns an access token (JWT).",
    operation_id="auth_signup",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new user and return a JWT access token."""
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, name=payload.name, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Validates credentials and returns an access token (JWT).",
    operation_id="auth_login",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login with email/password and return a JWT access token."""
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get current user",
    description="Returns the current user profile from the access token.",
    operation_id="auth_me",
)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    """Return current user's profile."""
    return MeResponse(id=str(current_user.id), email=current_user.email, name=current_user.name)
