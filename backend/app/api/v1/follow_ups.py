"""
api/v1/follow_ups.py — HTTP handlers for follow-up endpoints.

Thin layer: validates request, delegates to follow_up_service, returns ApiResponse.
"""
from typing import List, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.follow_up import FollowUpCreate, FollowUpOut
from app.services import follow_up_service

router = APIRouter()

# ── Allowed status values ──────────────────────────────────────────────────────
FollowUpStatus = Literal["pending", "completed", "cancelled"]


class StatusUpdate(BaseModel):
    """Request body for updating a follow-up's status."""
    status: FollowUpStatus


@router.post("/", response_model=ApiResponse[FollowUpOut], status_code=201)
def create_follow_up(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a follow-up for an existing interaction."""
    data = follow_up_service.create_follow_up(db, payload, user_id=current_user.id)
    return ApiResponse(statusCode=201, message="Follow-up scheduled successfully", data=data)


@router.get("/{interaction_id}", response_model=ApiResponse[List[FollowUpOut]])
def get_follow_ups(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all follow-ups linked to a specific interaction."""
    data = follow_up_service.list_by_interaction(db, interaction_id)
    return ApiResponse(statusCode=200, message="Follow-ups fetched successfully", data=data)


@router.patch("/{follow_up_id}/status", response_model=ApiResponse[FollowUpOut])
def update_status(
    follow_up_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the status of a follow-up.
    Accepts a JSON body: {"status": "pending" | "completed" | "cancelled"}.
    """
    data = follow_up_service.update_status(
        db, follow_up_id, payload.status, user_id=current_user.id
    )
    return ApiResponse(statusCode=200, message="Follow-up status updated successfully", data=data)
