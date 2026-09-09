from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict
from app.schemas.common import DMYDate, FullAuditOut


class InteractionBase(BaseModel):
    hcp_id: int
    rep_id: Optional[str] = None
    interaction_date: DMYDate
    channel: Optional[str] = None          # in-person / call / email
    topics_discussed: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None        # positive / neutral / negative
    samples_given: Optional[Dict[str, Any]] = None
    follow_up_required: Optional[bool] = False
    follow_up_date: Optional[DMYDate] = None
    raw_input: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None           # form / chat


class InteractionCreate(InteractionBase):
    pass


class InteractionPatch(BaseModel):
    """All fields optional — only provided fields are updated."""
    rep_id: Optional[str] = None
    interaction_date: Optional[DMYDate] = None
    channel: Optional[str] = None
    topics_discussed: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    samples_given: Optional[Dict[str, Any]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[DMYDate] = None
    raw_input: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None


class InteractionOut(InteractionBase, FullAuditOut):
    id: int

    model_config = ConfigDict(from_attributes=True)
