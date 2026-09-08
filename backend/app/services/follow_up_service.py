"""
services/follow_up_service.py — Business logic for follow-up management.

Extracted from app/routers/follow_ups.py.
"""
import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import follow_up_repository
from app.schemas.follow_up import FollowUpCreate, FollowUpOut

logger = logging.getLogger(__name__)


def create_follow_up(db: Session, payload: FollowUpCreate) -> FollowUpOut:
    """Schedule a follow-up for an existing interaction."""
    follow_up = follow_up_repository.create(db, payload.model_dump())
    return FollowUpOut.model_validate(follow_up)


def list_by_interaction(db: Session, interaction_id: int) -> List[FollowUpOut]:
    """Return all follow-ups linked to a specific interaction."""
    rows = follow_up_repository.list_by_interaction(db, interaction_id)
    return [FollowUpOut.model_validate(r) for r in rows]


def update_status(db: Session, follow_up_id: int, new_status: str) -> FollowUpOut:
    """
    Update the status of a follow-up.
    Raises 404 if the follow-up does not exist.
    """
    fu = follow_up_repository.get_by_id(db, follow_up_id)
    if not fu:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    fu = follow_up_repository.update_status(db, fu, new_status)
    return FollowUpOut.model_validate(fu)
