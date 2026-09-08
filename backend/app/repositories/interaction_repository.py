"""
repositories/interaction_repository.py — Raw SQLAlchemy queries for the Interaction model.

All DB access for Interaction records lives here.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.interaction import Interaction


def list_all(db: Session, skip: int = 0, limit: int = 50) -> List[Interaction]:
    """List all interactions newest-first. Supports pagination."""
    return (
        db.query(Interaction)
        .order_by(Interaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_by_hcp(
    db: Session, hcp_id: int, skip: int = 0, limit: int = 50
) -> List[Interaction]:
    """List all interactions for a given HCP, newest-first. Supports pagination."""
    return (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp_id)
        .order_by(Interaction.interaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_id(db: Session, interaction_id: int) -> Interaction | None:
    """Fetch an interaction by primary key."""
    return db.query(Interaction).filter(Interaction.id == interaction_id).first()


def create(db: Session, data: dict) -> Interaction:
    """Insert a new interaction record and return the refreshed ORM object."""
    interaction = Interaction(**data)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def patch(db: Session, interaction: Interaction, update_data: dict) -> Interaction:
    """Apply a partial update to an existing interaction record."""
    for field, value in update_data.items():
        setattr(interaction, field, value)
    db.commit()
    db.refresh(interaction)
    return interaction
