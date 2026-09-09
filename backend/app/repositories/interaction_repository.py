"""
repositories/interaction_repository.py — Raw SQLAlchemy queries for the Interaction model.

All DB access for Interaction records lives here.
"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.interaction import Interaction


def list_all(db: Session, skip: int = 0, limit: int = 50) -> List[Interaction]:
    """List all active interactions newest-first. Supports pagination."""
    return (
        db.query(Interaction)
        .filter(Interaction.deleted_at.is_(None))
        .order_by(Interaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_by_hcp(
    db: Session, hcp_id: int, skip: int = 0, limit: int = 50
) -> List[Interaction]:
    """List all active interactions for a given HCP, newest-first. Supports pagination."""
    return (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp_id, Interaction.deleted_at.is_(None))
        .order_by(Interaction.interaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_id(db: Session, interaction_id: int) -> Interaction | None:
    """Fetch an active interaction by primary key."""
    return (
        db.query(Interaction)
        .filter(Interaction.id == interaction_id, Interaction.deleted_at.is_(None))
        .first()
    )


def create(db: Session, data: dict, user_id: Optional[int] = None) -> Interaction:
    """Insert a new interaction record and return the refreshed ORM object."""
    item_data = dict(data)
    if user_id is not None:
        item_data.setdefault("created_by", user_id)
        item_data.setdefault("updated_by", user_id)
    interaction = Interaction(**item_data)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def patch(
    db: Session,
    interaction: Interaction,
    update_data: dict,
    user_id: Optional[int] = None,
) -> Interaction:
    """Apply a partial update to an existing interaction record."""
    for field, value in update_data.items():
        setattr(interaction, field, value)
    if user_id is not None:
        interaction.updated_by = user_id
    db.commit()
    db.refresh(interaction)
    return interaction


def soft_delete(db: Session, interaction_id: int, user_id: Optional[int] = None) -> bool:
    """Soft-delete an interaction. Returns True if deleted, False if not found."""
    interaction = (
        db.query(Interaction)
        .filter(Interaction.id == interaction_id, Interaction.deleted_at.is_(None))
        .first()
    )
    if not interaction:
        return False
    interaction.deleted_at = datetime.now(timezone.utc)
    interaction.deleted_by = user_id
    db.commit()
    return True
