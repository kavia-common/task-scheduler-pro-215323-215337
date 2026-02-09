from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min length 8)")
    name: str = Field(..., min_length=1, description="Display name")


class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="Bearer token to use in Authorization header")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")


class MeResponse(BaseModel):
    """Current user profile response."""

    id: str = Field(..., description="User id")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User display name")
