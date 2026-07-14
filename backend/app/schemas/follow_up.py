from datetime import date
from typing import Optional

from pydantic import BaseModel


class FollowUpBase(BaseModel):
    interaction_id: int
    due_date: Optional[date] = None
    status: Optional[str] = "pending"
    note: Optional[str] = None


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpOut(FollowUpBase):
    id: int

    class Config:
        from_attributes = True
