from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class InteractionBase(BaseModel):
    hcp_id: int
    rep_id: Optional[str] = None
    interaction_date: date
    channel: Optional[str] = None          # in-person / call / email
    topics_discussed: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None        # positive / neutral / negative
    samples_given: Optional[Dict[str, Any]] = None
    follow_up_required: Optional[bool] = False
    follow_up_date: Optional[date] = None
    raw_input: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None           # form / chat


class InteractionCreate(InteractionBase):
    pass


class InteractionPatch(BaseModel):
    """All fields optional — only provided fields are updated."""
    rep_id: Optional[str] = None
    interaction_date: Optional[date] = None
    channel: Optional[str] = None
    topics_discussed: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    samples_given: Optional[Dict[str, Any]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[date] = None
    raw_input: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None


class InteractionOut(InteractionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
