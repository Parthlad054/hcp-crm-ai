"""
api/v1/hcps.py — HTTP handlers for HCP endpoints.

Thin layer: validates request, delegates to hcp_service, returns ApiResponse.
All business logic (including search cache) lives in services/hcp_service.py.
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.hcp import HCPCreate, HCPOut
from app.services import hcp_service

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[HCPOut]])
def list_hcps(
    q: str = "",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all HCPs; optionally filter by name for autocomplete. Results are cached for 60s."""
    data = hcp_service.list_hcps(db, q=q, skip=skip, limit=limit)
    return ApiResponse(statusCode=200, message="HCPs fetched successfully", data=data)


@router.post("/", response_model=ApiResponse[HCPOut], status_code=201)
def create_hcp(
    payload: HCPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HCP record. Invalidates the search cache."""
    data = hcp_service.create_hcp(db, payload)
    return ApiResponse(statusCode=201, message="HCP created successfully", data=data)


@router.get("/{hcp_id}", response_model=ApiResponse[HCPOut])
def get_hcp(
    hcp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single HCP by ID."""
    data = hcp_service.get_hcp(db, hcp_id)
    return ApiResponse(statusCode=200, message="HCP fetched successfully", data=data)
