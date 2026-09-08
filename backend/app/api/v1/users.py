"""
api/v1/users.py — HTTP handlers for user profile management.

Stub router for future user self-service endpoints:
update profile, change password, deactivate account, etc.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import UserOut
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=ApiResponse[UserOut])
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return ApiResponse(
        statusCode=200,
        message="User profile fetched successfully",
        data=UserOut.model_validate(current_user),
    )
