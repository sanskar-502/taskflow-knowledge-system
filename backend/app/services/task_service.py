"""
Task management service.
Handles CRUD operations and dynamic filtering for tasks.
"""

import math
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from fastapi import HTTPException, status

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListResponse


def create_task(data: TaskCreate, creator_id: int, db: Session) -> TaskOut:
    """Create a new task. Only admins should call this (enforced at the route level)."""

    # If assigning to someone, make sure that user exists
    if data.assigned_to:
        assignee = db.query(User).filter(User.id == data.assigned_to).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {data.assigned_to} not found",
            )

    task = Task(
        title=data.title,
        description=data.description,
        assigned_to=data.assigned_to,
        created_by=creator_id,
        due_date=data.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return _task_to_response(task)


def get_tasks(
    db: Session,
    status_filter: Optional[str] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
) -> TaskListResponse:
    """
    List tasks with dynamic filtering, sorting, and pagination.

    This is the mandatory filtering API. Supports query parameters like:
      /tasks?status=Completed&assigned_to=1&page=2&limit=5&sort_by=due_date&order=asc
    """
    query = db.query(Task)

    # Apply filters only if they're provided
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if assigned_to is not None:
        query = query.filter(Task.assigned_to == assigned_to)
    if created_by is not None:
        query = query.filter(Task.created_by == created_by)

    # Get total count before pagination
    total = query.count()

    # Sorting
    sort_column = getattr(Task, sort_by, Task.created_at)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Pagination
    offset = (page - 1) * limit
    tasks = query.offset(offset).limit(limit).all()
    total_pages = math.ceil(total / limit) if limit > 0 else 1

    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


def get_task_by_id(task_id: int, db: Session) -> TaskOut:
    """Fetch a single task by its ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return _task_to_response(task)


def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User,
    db: Session,
) -> TaskOut:
    """
    Update a task. Users can update the status of tasks assigned to them.
    Admins can update any field on any task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Regular users can only update tasks assigned to them
    is_admin = current_user.role.role_name == "Admin"
    if not is_admin and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update tasks assigned to you",
        )

    # Apply updates for fields that were actually provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return _task_to_response(task)


def delete_task(task_id: int, db: Session) -> dict:
    """Delete a task. Only admins should call this."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted successfully"}


def _task_to_response(task: Task) -> TaskOut:
    """Convert a Task ORM object to a response schema."""
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        assigned_to=task.assigned_to,
        assignee_name=task.assignee.name if task.assignee else None,
        created_by=task.created_by,
        creator_name=task.creator.name if task.creator else None,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
