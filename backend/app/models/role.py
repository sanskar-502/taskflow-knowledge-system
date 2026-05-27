"""
Role model. Stores the available roles in the system (Admin, User).
Seeded once at startup and referenced by the users table.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(20), unique=True, nullable=False)

    # One role can have many users
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, role_name='{self.role_name}')>"
