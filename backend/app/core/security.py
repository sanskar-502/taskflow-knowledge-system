"""
Security utilities for JWT token management and password hashing.
This module handles the cryptographic operations -- nothing else should
be doing raw hashing or token encoding.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt

from app.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with a random salt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT token.

    The payload always includes:
    - sub: the user ID (as a string, per JWT convention)
    - role: the user's role name
    - exp: expiration timestamp
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    Raises jwt.ExpiredSignatureError if the token has expired.
    Raises jwt.InvalidTokenError for any other validation failure.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
