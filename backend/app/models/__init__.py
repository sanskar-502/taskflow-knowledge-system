"""
Makes all models importable from app.models directly.
Also ensures all models are registered with SQLAlchemy's Base
before we run create_all or migrations.
"""

from app.models.role import Role
from app.models.user import User
from app.models.task import Task
from app.models.document import Document
from app.models.activity_log import ActivityLog

__all__ = ["Role", "User", "Task", "Document", "ActivityLog"]
