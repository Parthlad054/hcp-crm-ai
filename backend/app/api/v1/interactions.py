"""
api/v1/interactions.py — HTTP handlers for interaction endpoints.

Thin layer: validates request, delegates to interaction_service, returns ApiResponse.
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.interaction import InteractionCreate, InteractionOut, InteractionPatch
from app.services import interaction_service

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
    data = interaction_service.create_interaction(db, payload, current_user)
    return ApiResponse(statusCode=201, message="Interaction logged successfully", data=data)


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
    data = interaction_service.list_all_interactions(db, skip=skip, limit=limit)
    return ApiResponse(statusCode=200, message="Interactions fetched successfully", data=data)


@router.get("/{hcp_id}", response_model=ApiResponse[List[InteractionOut]])
def get_interactions_for_hcp(
    hcp_id: int,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all interactions for a given HCP, newest first. Supports pagination."""
    data = interaction_service.list_by_hcp(db, hcp_id=hcp_id, skip=skip, limit=limit)
    return ApiResponse(statusCode=200, message="HCP interactions fetched successfully", data=data)


@router.patch("/{interaction_id}", response_model=ApiResponse[InteractionOut])
def patch_interaction(
    interaction_id: int,
    payload: InteractionPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partial update — only supplied fields are written."""
    data = interaction_service.patch_interaction(db, interaction_id, payload)
    return ApiResponse(statusCode=200, message="Interaction updated successfully", data=data)
