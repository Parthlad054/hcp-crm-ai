from datetime import date
from typing import Optional

from pydantic import BaseModel


class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital_affiliation: Optional[str] = None
    last_interaction_date: Optional[date] = None
    notes: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPOut(HCPBase):
    id: int

    class Config:
        from_attributes = True
