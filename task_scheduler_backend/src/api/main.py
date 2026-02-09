from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import get_settings
from src.api.db.init_db import init_db
from src.api.routes.auth import router as auth_router
from src.api.routes.notifications import router as notifications_router
from src.api.routes.tasks import router as tasks_router

settings = get_settings()

openapi_tags = [
    {"name": "health", "description": "Service health checks"},
    {"name": "auth", "description": "User registration, login, and profile"},
    {"name": "tasks", "description": "Task CRUD endpoints"},
    {"name": "notifications", "description": "Upcoming-task notification endpoints"},
]

app = FastAPI(
    title="Task Scheduler Pro API",
    description=(
        "Backend API for Task Scheduler Pro.\n\n"
        "Auth: Use Bearer JWT in `Authorization` header.\n"
        "Frontend expects: POST /auth/signup, POST /auth/login, GET /auth/me, and /tasks CRUD.\n"
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS: allow the React frontend to call this API.
# Use CORS_ALLOW_ORIGINS env var to restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Initialize database schema on app startup."""
    init_db()


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Simple health check endpoint used for platform readiness checks.",
    operation_id="health_check",
)
def health_check():
    """Return a health status payload."""
    return {"message": "Healthy"}


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(notifications_router)
