from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.schemas.common import DMYDate, FullAuditOut


class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital_affiliation: Optional[str] = None
    last_interaction_date: Optional[DMYDate] = None
    notes: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPOut(HCPBase, FullAuditOut):
    id: int

    model_config = ConfigDict(from_attributes=True)
