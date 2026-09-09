"""
repositories/hcp_repository.py — Raw SQLAlchemy queries for the HCP model.

All DB access for HCP records lives here.
"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.hcp import HCP


def list_hcps(db: Session, q: str = "", skip: int = 0, limit: int = 50) -> List[HCP]:
    """
    List active HCPs with optional name filter (case-insensitive substring).
    Supports pagination via skip/limit. Excludes soft-deleted HCPs.
    """
    query = db.query(HCP).filter(HCP.deleted_at.is_(None))
    if q:
        query = query.filter(HCP.name.ilike(f"%{q}%"))
    return query.offset(skip).limit(limit).all()


def get_by_id(db: Session, hcp_id: int) -> HCP | None:
    """Fetch an active HCP by primary key."""
    return db.query(HCP).filter(HCP.id == hcp_id, HCP.deleted_at.is_(None)).first()


def create(db: Session, data: dict, user_id: Optional[int] = None) -> HCP:
    """Insert a new HCP record and return the refreshed ORM object."""
    item_data = dict(data)
    if user_id is not None:
        item_data.setdefault("created_by", user_id)
        item_data.setdefault("updated_by", user_id)
    hcp = HCP(**item_data)
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


def soft_delete(db: Session, hcp_id: int, user_id: Optional[int] = None) -> bool:
    """Soft delete an active HCP. Returns True if deleted, False if not found."""
    hcp = db.query(HCP).filter(HCP.id == hcp_id, HCP.deleted_at.is_(None)).first()
    if not hcp:
        return False
    hcp.deleted_at = datetime.now(timezone.utc)
    hcp.deleted_by = user_id
    db.commit()
    return True


def fuzzy_search(db: Session, name: str) -> List[HCP]:
    """
    Case-insensitive substring search on active HCP name.
    Used by agent tools to match free-text doctor names.
    """
    return (
        db.query(HCP)
        .filter(HCP.deleted_at.is_(None), HCP.name.ilike(f"%{name}%"))
        .all()
    )
