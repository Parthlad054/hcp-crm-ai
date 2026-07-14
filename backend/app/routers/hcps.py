from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hcp import HCP
from app.schemas.hcp import HCPCreate, HCPOut

router = APIRouter()


@router.get("/", response_model=List[HCPOut])
def list_hcps(q: str = "", db: Session = Depends(get_db)):
    """List all HCPs; optionally filter by name for autocomplete."""
    query = db.query(HCP)
    if q:
        query = query.filter(HCP.name.ilike(f"%{q}%"))
    return query.all()


@router.post("/", response_model=HCPOut, status_code=201)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db)):
    """Create a new HCP record (used for seeding / testing)."""
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.get("/{hcp_id}", response_model=HCPOut)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp
