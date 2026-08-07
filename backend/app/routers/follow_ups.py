from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.follow_up import FollowUp
from app.models.user import User
from app.schemas.follow_up import FollowUpCreate, FollowUpOut

router = APIRouter()

# ── Allowed status values ──────────────────────────────────────────────────────
FollowUpStatus = Literal["pending", "completed", "cancelled"]


class StatusUpdate(BaseModel):
    """Request body for updating a follow-up's status."""
    status: FollowUpStatus


@router.post("/", response_model=FollowUpOut, status_code=201)
def create_follow_up(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a follow-up for an existing interaction."""
    follow_up = FollowUp(**payload.model_dump())
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


@router.get("/{interaction_id}", response_model=List[FollowUpOut])
def get_follow_ups(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all follow-ups linked to a specific interaction."""
    return (
        db.query(FollowUp)
        .filter(FollowUp.interaction_id == interaction_id)
        .all()
    )


@router.patch("/{follow_up_id}/status", response_model=FollowUpOut)
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
    fu = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()
    if not fu:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    fu.status = payload.status
    db.commit()
    db.refresh(fu)
    return fu

