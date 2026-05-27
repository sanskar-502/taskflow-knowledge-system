"""
Pydantic schemas for authentication endpoints.
Handles validation for login, registration, and token responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Email address used for login")
    password: str = Field(..., min_length=6, max_length=128, description="Account password")
    role_id: Optional[int] = Field(default=2, description="Role ID, defaults to regular User")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Needed because TokenResponse references UserOut which is defined after it
TokenResponse.model_rebuild()
