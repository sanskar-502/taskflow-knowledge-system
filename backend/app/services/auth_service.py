"""
Authentication service.
Handles user registration and login, delegating password hashing
and token creation to the security module.
"""

from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.config import get_settings

settings = get_settings()


def register_user(data: UserRegister, db: Session) -> UserOut:
    """
    Create a new user account.
    Checks for duplicate email before inserting.
    """
    # Check if email is already taken
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Verify the role exists
    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role_id=data.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=role.role_name,
        created_at=user.created_at,
    )


def authenticate_user(data: UserLogin, db: Session) -> TokenResponse:
    """
    Validate credentials and return a JWT token.
    We deliberately use a vague error message to avoid revealing
    whether the email or password was wrong.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Build the JWT payload
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.role_name},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    user_out = UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.role_name,
        created_at=user.created_at,
    )

    return TokenResponse(access_token=token, user=user_out)
