"""
repositories/follow_up_repository.py — Raw SQLAlchemy queries for the FollowUp model.

All DB access for FollowUp records lives here.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.follow_up import FollowUp


def list_by_interaction(db: Session, interaction_id: int) -> List[FollowUp]:
    """Return all follow-ups linked to a specific interaction."""
    return (
        db.query(FollowUp)
        .filter(FollowUp.interaction_id == interaction_id)
        .all()
    )


def get_by_id(db: Session, follow_up_id: int) -> FollowUp | None:
    """Fetch a follow-up by primary key."""
    return db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()


def create(db: Session, data: dict, user_id: Optional[int] = None) -> FollowUp:
    """Insert a new follow-up record and return the refreshed ORM object."""
    item_data = dict(data)
    if user_id is not None:
        item_data.setdefault("created_by", user_id)
        item_data.setdefault("updated_by", user_id)
    follow_up = FollowUp(**item_data)
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


def update_status(
    db: Session,
    follow_up: FollowUp,
    status: str,
    user_id: Optional[int] = None,
) -> FollowUp:
    """Update the status field of an existing follow-up record."""
    follow_up.status = status
    if user_id is not None:
        follow_up.updated_by = user_id
    db.commit()
    db.refresh(follow_up)
    return follow_up
