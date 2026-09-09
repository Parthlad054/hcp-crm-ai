"""
services/interaction_service.py — Business logic for interaction management.

Extracted from app/routers/interactions.py.
"""
import logging
from typing import List, Optional

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
    Automatically fills rep_id and audit created_by/updated_by.
    """
    data = payload.model_dump()
    if not data.get("rep_id"):
        data["rep_id"] = current_user.email
    interaction = interaction_repository.create(db, data, user_id=current_user.id)
    return InteractionOut.model_validate(interaction)


def list_all_interactions(
    db: Session, skip: int = 0, limit: int = 50
) -> List[InteractionOut]:
    """List all active interactions (admin/debug use). Supports pagination."""
    rows = interaction_repository.list_all(db, skip=skip, limit=limit)
    return [InteractionOut.model_validate(r) for r in rows]


def list_by_hcp(
    db: Session, hcp_id: int, skip: int = 0, limit: int = 50
) -> List[InteractionOut]:
    """Return all active interactions for a given HCP, newest first. Supports pagination."""
    rows = interaction_repository.list_by_hcp(db, hcp_id=hcp_id, skip=skip, limit=limit)
    return [InteractionOut.model_validate(r) for r in rows]


def patch_interaction(
    db: Session,
    interaction_id: int,
    payload: InteractionPatch,
    current_user: Optional[User] = None,
) -> InteractionOut:
    """
    Apply a partial update to an interaction — only supplied fields are written.
    Raises 404 if the interaction does not exist or is soft-deleted.
    """
    interaction = interaction_repository.get_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    update_data = payload.model_dump(exclude_unset=True)
    user_id = current_user.id if current_user else None
    interaction = interaction_repository.patch(db, interaction, update_data, user_id=user_id)
    return InteractionOut.model_validate(interaction)


def delete_interaction(
    db: Session, interaction_id: int, current_user: User
) -> None:
    """Soft delete an interaction. Raises 404 if not found or already deleted."""
    success = interaction_repository.soft_delete(db, interaction_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found")
