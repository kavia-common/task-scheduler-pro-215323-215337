import os
from dataclasses import dataclass
from urllib.parse import quote_plus


def _get_env(name: str, default: str | None = None) -> str | None:
    """Internal helper to read environment variables without hardcoding secrets."""
    return os.getenv(name, default)


def _build_postgres_url_from_components() -> str | None:
    """Build a SQLAlchemy-compatible Postgres URL from POSTGRES_* components.

    This supports deployments where the platform provides split connection env vars
    instead of a full POSTGRES_URL.

    Expected env vars (names are provided by the database container on the platform):
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - POSTGRES_PORT
    Optional:
    - POSTGRES_HOST (defaults to "localhost")
    """
    user = _get_env("POSTGRES_USER")
    password = _get_env("POSTGRES_PASSWORD")
    db = _get_env("POSTGRES_DB")
    port = _get_env("POSTGRES_PORT")
    host = _get_env("POSTGRES_HOST", "localhost") or "localhost"

    if not (user and password and db and port):
        return None

    # URL encode credentials to safely handle special characters.
    user_q = quote_plus(user)
    pass_q = quote_plus(password)

    # psycopg3 driver:
    return f"postgresql+psycopg://{user_q}:{pass_q}@{host}:{port}/{db}"


def _resolve_cors_allow_origins() -> list[str]:
    """Resolve CORS allow-origins from environment.

    Supported env vars:
    - CORS_ALLOW_ORIGINS: comma-separated list or "*"
    - FRONTEND_URL: single origin URL (e.g. platform preview URL). If provided,
      it will be merged into allow list unless CORS_ALLOW_ORIGINS="*".
    """
    cors_raw = (_get_env("CORS_ALLOW_ORIGINS", "*") or "*").strip()
    if cors_raw == "*":
        return ["*"]

    allow = [o.strip() for o in cors_raw.split(",") if o.strip()]

    # Convenience for platform preview: set FRONTEND_URL to https://...:3000
    fe = (_get_env("FRONTEND_URL", "") or "").strip()
    if fe and fe not in allow:
        allow.append(fe)

    return allow


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
    - JWT_SECRET_KEY: secret used to sign JWT tokens.

    Database configuration (one of):
    - POSTGRES_URL: SQLAlchemy/psycopg compatible URL. Example:
      postgresql+psycopg://user:pass@host:port/db
    - Or platform-provided components: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
      (and optionally POSTGRES_HOST).

    Optional:
    - JWT_ALGORITHM (default: HS256)
    - ACCESS_TOKEN_EXPIRE_MINUTES (default: 10080 = 7 days)
    - CORS_ALLOW_ORIGINS: comma-separated list or "*" (default: "*")
    - FRONTEND_URL: single frontend origin to allow (merged into allow list)
    """
    postgres_url = _get_env("POSTGRES_URL") or _build_postgres_url_from_components()
    if not postgres_url:
        # Note: Orchestrator should set this in .env.
        raise RuntimeError(
            "Missing database config: set POSTGRES_URL or POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB/POSTGRES_PORT"
        )

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

    cors_allow_origins = _resolve_cors_allow_origins()

    return Settings(
        postgres_url=postgres_url,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        access_token_exp_minutes=exp_minutes,
        cors_allow_origins=cors_allow_origins,
    )
