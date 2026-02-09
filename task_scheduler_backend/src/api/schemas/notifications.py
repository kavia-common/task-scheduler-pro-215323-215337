from datetime import datetime

from pydantic import BaseModel, Field

from src.api.schemas.tasks import TaskOut


class UpcomingTaskOut(BaseModel):
    """Upcoming task including reminder metadata."""

    task: TaskOut = Field(..., description="Task info")
    due_in_minutes: int = Field(..., ge=0, description="Minutes remaining until due_at")
    due_at: datetime = Field(..., description="Due date/time in ISO format")


class UpcomingTasksResponse(BaseModel):
    """Response for upcoming tasks endpoint."""

    items: list[UpcomingTaskOut] = Field(..., description="Upcoming tasks")
