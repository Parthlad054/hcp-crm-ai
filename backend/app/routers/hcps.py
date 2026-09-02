import threading
from typing import List

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.hcp import HCP
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.hcp import HCPCreate, HCPOut

router = APIRouter()

# ── HCP search cache ───────────────────────────────────────────────────────────
_hcp_cache: TTLCache = TTLCache(maxsize=512, ttl=60)
_cache_lock = threading.Lock()


def _cache_key(q: str, skip: int, limit: int) -> str:
    return f"{q.lower().strip()}:{skip}:{limit}"


def _invalidate_hcp_cache() -> None:
    """Clear the whole cache when HCP data changes (new HCP created)."""
    with _cache_lock:
        _hcp_cache.clear()


@router.get("/", response_model=ApiResponse[List[HCPOut]])
def list_hcps(
    q: str = "",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all HCPs; optionally filter by name for autocomplete. Results are cached for 60s."""
    key = _cache_key(q, skip, limit)
    with _cache_lock:
        if key in _hcp_cache:
            return ApiResponse(
                statusCode=200,
                message="HCPs fetched successfully",
                data=_hcp_cache[key],
            )

    query = db.query(HCP)
    if q:
        query = query.filter(HCP.name.ilike(f"%{q}%"))
    rows = query.offset(skip).limit(limit).all()

    result = [HCPOut.model_validate(r) for r in rows]
    with _cache_lock:
        _hcp_cache[key] = result

    return ApiResponse(
        statusCode=200,
        message="HCPs fetched successfully",
        data=result,
    )


@router.post("/", response_model=ApiResponse[HCPOut], status_code=201)
def create_hcp(
    payload: HCPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HCP record. Invalidates the search cache."""
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    _invalidate_hcp_cache()  # ensure next search reflects the new record
    return ApiResponse(
        statusCode=201,
        message="HCP created successfully",
        data=HCPOut.model_validate(hcp),
    )


@router.get("/{hcp_id}", response_model=ApiResponse[HCPOut])
def get_hcp(
    hcp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return ApiResponse(
        statusCode=200,
        message="HCP fetched successfully",
        data=HCPOut.model_validate(hcp),
    )

