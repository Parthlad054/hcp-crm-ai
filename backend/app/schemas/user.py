"""
schemas/user.py — Pydantic schemas for the User domain.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    """Public-safe representation of a user — never exposes hashed_password."""
    id: int
    name: str
    email: EmailStr
    contact_number: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
