"""
repositories/hcp_repository.py — Raw SQLAlchemy queries for the HCP model.

All DB access for HCP records lives here.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.hcp import HCP


def list_hcps(db: Session, q: str = "", skip: int = 0, limit: int = 50) -> List[HCP]:
    """
    List HCPs with optional name filter (case-insensitive substring).
    Supports pagination via skip/limit.
    """
    query = db.query(HCP)
    if q:
        query = query.filter(HCP.name.ilike(f"%{q}%"))
    return query.offset(skip).limit(limit).all()


def get_by_id(db: Session, hcp_id: int) -> HCP | None:
    """Fetch an HCP by primary key."""
    return db.query(HCP).filter(HCP.id == hcp_id).first()


def create(db: Session, data: dict) -> HCP:
    """Insert a new HCP record and return the refreshed ORM object."""
    hcp = HCP(**data)
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


def fuzzy_search(db: Session, name: str) -> List[HCP]:
    """
    Case-insensitive substring search on HCP name.
    Used by agent tools to match free-text doctor names.
    Returns all matches — callers should handle 0 / 1 / 2+ cases.
    """
    return db.query(HCP).filter(HCP.name.ilike(f"%{name}%")).all()
