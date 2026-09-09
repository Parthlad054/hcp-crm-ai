from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.schemas.common import DMYDate, TimestampAuditOut


class FollowUpBase(BaseModel):
    interaction_id: int
    due_date: Optional[DMYDate] = None
    status: Optional[str] = "pending"
    note: Optional[str] = None


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpOut(FollowUpBase, TimestampAuditOut):
    id: int

    model_config = ConfigDict(from_attributes=True)
