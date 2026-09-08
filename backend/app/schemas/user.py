"""
schemas/user.py — Pydantic schemas for the User domain.

UserOut was previously defined in schemas/auth.py. Moving it here
so the user schema is not entangled with auth request/response schemas.
"""
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    """Public-safe representation of a user — never exposes hashed_password."""
    id: int
    name: str
    email: EmailStr
    contact_number: str
    is_active: bool

    model_config = {"from_attributes": True}
