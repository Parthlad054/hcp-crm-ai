"""
services/hcp_service.py — Business logic for HCP management.

Extracted from app/routers/hcps.py. Owns the TTL cache for HCP searches.
"""
import threading
from typing import List, Optional

from cachetools import TTLCache
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import hcp_repository
from app.schemas.hcp import HCPCreate, HCPOut

# ── HCP search cache ───────────────────────────────────────────────────────────
# Results are cached for 60 seconds to reduce DB load on autocomplete queries.
_hcp_cache: TTLCache = TTLCache(maxsize=512, ttl=60)
_cache_lock = threading.Lock()


def _cache_key(q: str, skip: int, limit: int) -> str:
    return f"{q.lower().strip()}:{skip}:{limit}"


def invalidate_hcp_cache() -> None:
    """Clear the entire cache when HCP data changes (e.g. after create/delete)."""
    with _cache_lock:
        _hcp_cache.clear()


def list_hcps(db: Session, q: str = "", skip: int = 0, limit: int = 50) -> List[HCPOut]:
    """
    List all active HCPs; optionally filter by name for autocomplete.
    Results are cached for 60 seconds per (q, skip, limit) combination.
    """
    key = _cache_key(q, skip, limit)
    with _cache_lock:
        if key in _hcp_cache:
            return _hcp_cache[key]

    rows = hcp_repository.list_hcps(db, q=q, skip=skip, limit=limit)
    result = [HCPOut.model_validate(r) for r in rows]

    with _cache_lock:
        _hcp_cache[key] = result

    return result


def get_hcp(db: Session, hcp_id: int) -> HCPOut:
    """Fetch a single active HCP by ID. Raises 404 if not found or soft-deleted."""
    hcp = hcp_repository.get_by_id(db, hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return HCPOut.model_validate(hcp)


def create_hcp(db: Session, payload: HCPCreate, user_id: Optional[int] = None) -> HCPOut:
    """Create a new HCP record and invalidate the search cache."""
    hcp = hcp_repository.create(db, payload.model_dump(), user_id=user_id)
    invalidate_hcp_cache()
    return HCPOut.model_validate(hcp)


def delete_hcp(db: Session, hcp_id: int, user_id: Optional[int] = None) -> None:
    """Soft-delete an HCP by ID. Raises 404 if not found."""
    success = hcp_repository.soft_delete(db, hcp_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="HCP not found")
    invalidate_hcp_cache()
