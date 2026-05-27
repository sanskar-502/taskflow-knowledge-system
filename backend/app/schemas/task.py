"""
Pydantic schemas for task management endpoints.
Covers creation, updates, filtering parameters, and list responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[int] = Field(default=None, description="User ID to assign the task to")
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    assigned_to: Optional[int]
    assignee_name: Optional[str] = None
    created_by: int
    creator_name: Optional[str] = None
    due_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskOut]
    total: int
    page: int
    limit: int
    total_pages: int
