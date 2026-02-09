from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.session import get_db
from src.api.deps.auth import get_current_user
from src.api.models.task import Task
from src.api.models.user import User
from src.api.schemas.notifications import UpcomingTaskOut, UpcomingTasksResponse
from src.api.schemas.tasks import TaskOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


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
    "/upcoming",
    response_model=UpcomingTasksResponse,
    summary="Upcoming tasks",
    description="Returns tasks with due_at within the next N minutes (excluding completed).",
    operation_id="notifications_upcoming",
)
def upcoming_tasks(
    minutes: int = Query(60, ge=1, le=43200, description="Lookahead window in minutes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UpcomingTasksResponse:
    """List upcoming tasks due soon for the authenticated user."""
    now = datetime.now(UTC)
    window_end = now + timedelta(minutes=minutes)

    rows = db.scalars(
        select(Task)
        .where(
            Task.user_id == current_user.id,
            Task.completed.is_(False),
            Task.due_at.is_not(None),
            Task.due_at >= now,
            Task.due_at <= window_end,
        )
        .order_by(Task.due_at.asc())
    ).all()

    items: list[UpcomingTaskOut] = []
    for t in rows:
        # due_at is not None due to query filter
        due_at = t.due_at  # type: ignore[assignment]
        delta = due_at - now
        due_in_minutes = max(0, int(delta.total_seconds() // 60))
        items.append(
            UpcomingTaskOut(
                task=_task_to_out(t),
                due_in_minutes=due_in_minutes,
                due_at=due_at,
            )
        )

    return UpcomingTasksResponse(items=items)
