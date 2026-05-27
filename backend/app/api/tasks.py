"""
Task management routes.
Admin can create, assign, and delete tasks.
Users can view their tasks and update status.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListResponse
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(require_role("Admin")),
    db: Session = Depends(get_db),
):
    """Create a new task and optionally assign it to a user. Admin only."""
    return task_service.create_task(data, current_user.id, db)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: Optional[str] = Query(default=None, description="Filter by status: Pending, In Progress, Completed"),
    assigned_to: Optional[int] = Query(default=None, description="Filter by assigned user ID"),
    created_by: Optional[int] = Query(default=None, description="Filter by creator user ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Results per page"),
    sort_by: str = Query(default="created_at", description="Field to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List tasks with optional filtering, sorting, and pagination.
    Both admins and users can access this endpoint.

    Example:
        GET /tasks?status=Completed&assigned_to=3&page=1&limit=5
    """
    return task_service.get_tasks(
        db=db,
        status_filter=status,
        assigned_to=assigned_to,
        created_by=created_by,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single task by ID."""
    return task_service.get_task_by_id(task_id, db)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a task. Users can update the status of their own assigned tasks.
    Admins can update any field on any task.
    """
    return task_service.update_task(task_id, data, current_user, db)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(require_role("Admin")),
    db: Session = Depends(get_db),
):
    """Delete a task. Admin only."""
    return task_service.delete_task(task_id, db)
