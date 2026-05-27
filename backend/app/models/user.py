"""
User model. Stores registered users with hashed passwords.
Each user is associated with exactly one role.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("Role", back_populates="users")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    documents = relationship("Document", back_populates="uploader")
    activity_logs = relationship("ActivityLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
