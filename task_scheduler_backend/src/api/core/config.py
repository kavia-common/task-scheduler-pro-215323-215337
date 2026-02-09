import os
from dataclasses import dataclass


def _get_env(name: str, default: str | None = None) -> str | None:
    """Internal helper to read environment variables without hardcoding secrets."""
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    postgres_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_exp_minutes: int
    cors_allow_origins: list[str]


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load and validate settings from environment.

    Required environment variables:
    - POSTGRES_URL: SQLAlchemy/psycopg compatible URL. Example:
      postgresql+psycopg://user:pass@host:port/db
      (In this project the database container provides components: POSTGRES_URL, etc.)
    - JWT_SECRET_KEY: secret used to sign JWT tokens.

    Optional:
    - JWT_ALGORITHM (default: HS256)
    - ACCESS_TOKEN_EXPIRE_MINUTES (default: 10080 = 7 days)
    - CORS_ALLOW_ORIGINS: comma-separated list or "*" (default: "*")
    """
    postgres_url = _get_env("POSTGRES_URL")
    if not postgres_url:
        # Note: Orchestrator should set this in .env.
        raise RuntimeError("Missing required env var POSTGRES_URL")

    jwt_secret_key = _get_env("JWT_SECRET_KEY")
    if not jwt_secret_key:
        # Note: Orchestrator should set this in .env.
        raise RuntimeError("Missing required env var JWT_SECRET_KEY")

    jwt_algorithm = _get_env("JWT_ALGORITHM", "HS256") or "HS256"
    exp_min_raw = _get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "10080") or "10080"
    try:
        exp_minutes = int(exp_min_raw)
    except ValueError as e:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer") from e

    cors_raw = (_get_env("CORS_ALLOW_ORIGINS", "*") or "*").strip()
    if cors_raw == "*":
        cors_allow_origins = ["*"]
    else:
        cors_allow_origins = [o.strip() for o in cors_raw.split(",") if o.strip()]

    return Settings(
        postgres_url=postgres_url,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        access_token_exp_minutes=exp_minutes,
        cors_allow_origins=cors_allow_origins,
    )
