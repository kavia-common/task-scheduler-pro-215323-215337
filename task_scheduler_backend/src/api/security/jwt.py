from datetime import UTC, datetime, timedelta

from jose import jwt

from src.api.core.config import get_settings

settings = get_settings()


# PUBLIC_INTERFACE
def create_access_token(subject: str) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Typically the user id (string).

    Returns:
        Encoded JWT token string.
    """
    now = datetime.now(UTC)
    exp = now + timedelta(minutes=settings.access_token_exp_minutes)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# PUBLIC_INTERFACE
def decode_token(token: str) -> dict:
    """Decode and validate JWT token.

    Raises jose.JWTError if invalid/expired.
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
