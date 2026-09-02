from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.interaction import Interaction
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.interaction import InteractionCreate, InteractionPatch, InteractionOut

router = APIRouter()


@router.post("/", response_model=ApiResponse[InteractionOut], status_code=201)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new interaction via the structured form (bypasses NLU).
    Requires active user authentication.
    """
    data = payload.model_dump()
    if not data.get("rep_id"):
        data["rep_id"] = current_user.email
    interaction = Interaction(**data)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return ApiResponse(
        statusCode=201,
        message="Interaction logged successfully",
        data=InteractionOut.model_validate(interaction),
    )


# ── GET / must be registered BEFORE GET /{hcp_id} ────────────────────────────
# FastAPI matches routes in registration order. If the wildcard /{hcp_id} were
# first, a future path like GET /export or GET /recent would be silently
# captured by it instead of matching its own handler.

@router.get("/", response_model=ApiResponse[List[InteractionOut]])
def list_all_interactions(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all interactions (dev / debug use). Supports pagination via skip & limit."""
    rows = (
        db.query(Interaction)
        .order_by(Interaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return ApiResponse(
        statusCode=200,
        message="Interactions fetched successfully",
        data=[InteractionOut.model_validate(r) for r in rows],
    )


@router.get("/{hcp_id}", response_model=ApiResponse[List[InteractionOut]])
def get_interactions_for_hcp(
    hcp_id: int,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all interactions for a given HCP, newest first. Supports pagination."""
    rows = (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp_id)
        .order_by(Interaction.interaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return ApiResponse(
        statusCode=200,
        message="HCP interactions fetched successfully",
        data=[InteractionOut.model_validate(r) for r in rows],
    )


@router.patch("/{interaction_id}", response_model=ApiResponse[InteractionOut])
def patch_interaction(
    interaction_id: int,
    payload: InteractionPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partial update — only supplied fields are written."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return ApiResponse(
        statusCode=200,
        message="Interaction updated successfully",
        data=InteractionOut.model_validate(interaction),
    )
