from datetime import UTC, datetime
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.api.db.session import get_db
from src.api.deps.auth import get_current_user
from src.api.models.task import Task
from src.api.models.user import User
from src.api.schemas.tasks import (
    TaskCreate,
    TaskOut,
    TaskPatchCompleted,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

_ALLOWED_PRIORITIES = {"low", "medium", "high"}


def _task_to_out(t: Task) -> TaskOut:
    return TaskOut(
        id=str(t.id),
        title=t.title,
        description=t.description,
        due_at=t.due_at,
        priority=t.priority,  # type: ignore[arg-type]
        completed=t.completed,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get(
    "",
    response_model=list[TaskOut],
    summary="List tasks",
    description="List tasks for the current user.",
    operation_id="tasks_list",
)
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskOut]:
    """Return tasks belonging to the authenticated user (newest first)."""
    rows = db.scalars(select(Task).where(Task.user_id == current_user.id).order_by(Task.created_at.desc())).all()
    return [_task_to_out(t) for t in rows]


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task for the current user.",
    operation_id="tasks_create",
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    """Create a task."""
    if payload.priority not in _ALLOWED_PRIORITIES:
        raise HTTPException(status_code=422, detail="Invalid priority")

    task = Task(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        priority=payload.priority,
        completed=False,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.put(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update task",
    description="Replace/update fields of an existing task (PUT).",
    operation_id="tasks_update",
)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    """Update a task for current user."""
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

    task = db.scalar(select(Task).where(Task.id == tid, Task.user_id == current_user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data: dict[str, Any] = payload.model_dump(exclude_unset=True)
    if "priority" in data and data["priority"] is not None and data["priority"] not in _ALLOWED_PRIORITIES:
        raise HTTPException(status_code=422, detail="Invalid priority")

    for k, v in data.items():
        setattr(task, k, v)

    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.patch(
    "/{task_id}",
    response_model=TaskOut,
    summary="Patch task completion",
    description="Toggle completion for an existing task (PATCH {completed}).",
    operation_id="tasks_patch",
)
def patch_task(
    task_id: str,
    payload: TaskPatchCompleted,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    """Patch completion state."""
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

    task = db.scalar(select(Task).where(Task.id == tid, Task.user_id == current_user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = payload.completed
    task.updated_at = datetime.now(UTC)

    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task by id.",
    operation_id="tasks_delete",
)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a task. Returns 204 on success."""
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

    task = db.scalar(select(Task).where(Task.id == tid, Task.user_id == current_user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.execute(delete(Task).where(Task.id == tid, Task.user_id == current_user.id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
