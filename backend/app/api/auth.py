"""
Authentication routes.
Handles user registration and login.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    By default, new accounts are created with the 'User' role.
    """
    return auth_service.register_user(data, db)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    The token should be included in subsequent requests as:
        Authorization: Bearer <token>
    """
    return auth_service.authenticate_user(data, db)
