"""
services/interaction_service.py — Business logic for interaction management.

Extracted from app/routers/interactions.py.
"""
import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import interaction_repository
from app.schemas.interaction import InteractionCreate, InteractionOut, InteractionPatch

logger = logging.getLogger(__name__)


def create_interaction(
    db: Session, payload: InteractionCreate, current_user: User
) -> InteractionOut:
    """
    Create a new interaction via the structured form (bypasses NLU).
    Automatically fills rep_id from the authenticated user if not provided.
    """
    data = payload.model_dump()
    if not data.get("rep_id"):
        data["rep_id"] = current_user.email
    interaction = interaction_repository.create(db, data)
    return InteractionOut.model_validate(interaction)


def list_all_interactions(
    db: Session, skip: int = 0, limit: int = 50
) -> List[InteractionOut]:
    """List all interactions (admin/debug use). Supports pagination."""
    rows = interaction_repository.list_all(db, skip=skip, limit=limit)
    return [InteractionOut.model_validate(r) for r in rows]


def list_by_hcp(
    db: Session, hcp_id: int, skip: int = 0, limit: int = 50
) -> List[InteractionOut]:
    """Return all interactions for a given HCP, newest first. Supports pagination."""
    rows = interaction_repository.list_by_hcp(db, hcp_id=hcp_id, skip=skip, limit=limit)
    return [InteractionOut.model_validate(r) for r in rows]


def patch_interaction(
    db: Session, interaction_id: int, payload: InteractionPatch
) -> InteractionOut:
    """
    Apply a partial update to an interaction — only supplied fields are written.
    Raises 404 if the interaction does not exist.
    """
    interaction = interaction_repository.get_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    update_data = payload.model_dump(exclude_unset=True)
    interaction = interaction_repository.patch(db, interaction, update_data)
    return InteractionOut.model_validate(interaction)
