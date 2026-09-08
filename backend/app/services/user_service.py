"""
services/user_service.py — Business logic for user profile management.

Stub for future features: update profile, change email, deactivate account, etc.
"""
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import user_repository
from app.schemas.user import UserOut

logger = logging.getLogger(__name__)


def get_user_profile(db: Session, user_id: int) -> UserOut:
    """Fetch and return the profile for a given user ID."""
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserOut.model_validate(user)
