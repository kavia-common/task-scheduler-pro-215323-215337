from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return _pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a password against its stored hash."""
    return _pwd_context.verify(plain_password, password_hash)
