from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.follow_up import FollowUp
from app.schemas.follow_up import FollowUpCreate, FollowUpOut

router = APIRouter()


@router.post("/", response_model=FollowUpOut, status_code=201)
def create_follow_up(payload: FollowUpCreate, db: Session = Depends(get_db)):
    """Schedule a follow-up for an existing interaction."""
    follow_up = FollowUp(**payload.model_dump())
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


@router.get("/{interaction_id}", response_model=List[FollowUpOut])
def get_follow_ups(interaction_id: int, db: Session = Depends(get_db)):
    """Return all follow-ups linked to a specific interaction."""
    return (
        db.query(FollowUp)
        .filter(FollowUp.interaction_id == interaction_id)
        .all()
    )


@router.patch("/{follow_up_id}/status")
def update_status(follow_up_id: int, status: str, db: Session = Depends(get_db)):
    """Update the status of a follow-up (pending → completed / cancelled)."""
    fu = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()
    if not fu:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    fu.status = status
    db.commit()
    db.refresh(fu)
    return fu
