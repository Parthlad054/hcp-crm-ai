from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionPatch, InteractionOut

router = APIRouter()


@router.post("/", response_model=InteractionOut, status_code=201)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """
    Create a new interaction via the structured form (bypasses NLU).
    The agent uses this same logic internally for the log_interaction tool.
    """
    interaction = Interaction(**payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.get("/{hcp_id}", response_model=List[InteractionOut])
def get_interactions_for_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Return all interactions for a given HCP, newest first."""
    return (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp_id)
        .order_by(Interaction.interaction_date.desc())
        .all()
    )


@router.patch("/{interaction_id}", response_model=InteractionOut)
def patch_interaction(
    interaction_id: int, payload: InteractionPatch, db: Session = Depends(get_db)
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
    return interaction


@router.get("/", response_model=List[InteractionOut])
def list_all_interactions(db: Session = Depends(get_db)):
    """List all interactions (dev / debug use)."""
    return db.query(Interaction).order_by(Interaction.created_at.desc()).all()
