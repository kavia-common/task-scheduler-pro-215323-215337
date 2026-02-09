from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["low", "medium", "high"]


class TaskBase(BaseModel):
    """Shared task fields."""

    title: str = Field(..., min_length=1, description="Task title")
    description: str | None = Field(None, description="Optional task details")
    due_at: datetime | None = Field(None, description="Due date/time in ISO format")
    priority: Priority = Field("medium", description="Task priority")


class TaskCreate(TaskBase):
    """Create task payload."""


class TaskUpdate(BaseModel):
    """Update task payload for PUT (all optional, but at least one should be present)."""

    title: str | None = Field(None, min_length=1, description="Task title")
    description: str | None = Field(None, description="Optional task details")
    due_at: datetime | None = Field(None, description="Due date/time in ISO format")
    priority: Priority | None = Field(None, description="Task priority")
    completed: bool | None = Field(None, description="Completion status")


class TaskPatchCompleted(BaseModel):
    """PATCH payload used by the frontend to toggle completion."""

    completed: bool = Field(..., description="Completion status")


class TaskOut(BaseModel):
    """Task response shape used by the frontend."""

    id: str = Field(..., description="Task id")
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Optional task details")
    due_at: datetime | None = Field(None, description="Due date/time in ISO format")
    priority: Priority = Field(..., description="Task priority")
    completed: bool = Field(..., description="Completion status")

    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class TaskListResponse(BaseModel):
    """Optional list wrapper. Frontend accepts either wrapper or raw array."""

    items: list[TaskOut] = Field(..., description="List of tasks")
