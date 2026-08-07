"""
security.py — JWT token helpers, password hashing, and the
get_current_user FastAPI dependency.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# ── Password hashing ──────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    # bcrypt has a 72-byte password limit. We truncate to 72 bytes to avoid ValueError.
    plain_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    # Truncate plain password to 72 bytes to match hashing truncation and avoid ValueError.
    plain_bytes = plain.encode("utf-8")[:72]
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


# ── Token creation ────────────────────────────────────────────────────────────

def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_reset_token(user_id: int) -> str:
    """Short-lived token embedded in the password-reset link."""
    return _create_token(
        {"sub": str(user_id), "type": "reset"},
        timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
    )


# ── Token decoding ────────────────────────────────────────────────────────────

def decode_token(token: str, expected_type: str) -> int:
    """
    Decode a JWT and return the user_id.
    Raises HTTPException 401 if the token is invalid, expired, or wrong type.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if user_id is None or token_type != expected_type:
            raise credentials_exception
        return int(user_id)
    except JWTError:
        raise credentials_exception


# ── FastAPI dependency ────────────────────────────────────────────────────────

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts and validates the Bearer token from Authorization header.
    Returns the authenticated User ORM object or raises 401.
    """
    user_id = decode_token(credentials.credentials, expected_type="access")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
