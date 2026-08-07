import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── User output ────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    contact_number: str
    is_active: bool

    model_config = {"from_attributes": True}


# ── Registration ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    contact_number: str
    password: str
    confirm_password: str

    def __repr__(self) -> str:
        return f"UserRegister(name='{self.name}', email='{self.email}', contact_number='{self.contact_number}', password='***', confirm_password='***')"

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

    @field_validator("contact_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Allow optional leading +, then 7–15 digits (covers Indian & international)
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise ValueError("Invalid contact number format")
        return cleaned

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


# ── Login ─────────────────────────────────────────────────────────────────────

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    def __repr__(self) -> str:
        return f"UserLogin(email='{self.email}', password='***')"


# ── Token ─────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Forgot / Reset Password ───────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    def __repr__(self) -> str:
        return f"ResetPasswordRequest(token='{self.token[:8]}...', new_password='***')"

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

