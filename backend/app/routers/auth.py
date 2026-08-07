"""
routers/auth.py — Registration, Login, Token Refresh,
Forgot Password (SMTP), Reset Password, and /me endpoints.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.limiter import limiter
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserOut,
)
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    get_current_user,
)
from app.auth.email import send_reset_email

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Returns access & refresh tokens plus user payload on success.
    Rate-limited: 3 registrations per IP per minute.
    """
    # Duplicate email check
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        contact_number=payload.contact_number,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.
    Returns access & refresh tokens plus user payload on success.
    Rate-limited: 10 attempts per IP per minute (brute-force protection).
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        # Deliberate vague error to prevent user enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )


# ── Refresh Token ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    Old refresh token is implicitly invalidated by issuing a new one.
    """
    user_id = decode_token(payload.refresh_token, expected_type="refresh")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )


# ── Forgot Password ───────────────────────────────────────────────────────────

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Sends a password-reset email to the registered address.
    Always returns 202 to avoid revealing whether the email exists.
    Rate-limited: 5 requests per IP per minute (prevents email spam/DoS).
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Return success anyway to prevent user enumeration
        return {"message": "If that email is registered, a reset link has been sent."}

    reset_token = create_reset_token(user.id)
    token_hash = hashlib.sha256(reset_token.encode()).hexdigest()

    user.password_reset_token = token_hash
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
    )
    db.commit()

    # Fire-and-forget email in background so the endpoint responds immediately
    background_tasks.add_task(send_reset_email, user.email, user.name, reset_token)

    logger.info("Password reset token generated for user %s", user.id)
    return {"message": "If that email is registered, a reset link has been sent."}


# ── Reset Password ────────────────────────────────────────────────────────────

@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Validates the reset JWT and single-use DB record, then sets a new hashed password.
    Rate-limited: 5 attempts per IP per minute.
    """
    user_id = decode_token(payload.token, expected_type="reset")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user or not user.password_reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Verify single-use token hash
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    if user.password_reset_token != token_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Verify expiration
    now = datetime.now(timezone.utc)
    if user.password_reset_expires and user.password_reset_expires.tzinfo is None:
        expires_at = user.password_reset_expires.replace(tzinfo=timezone.utc)
    else:
        expires_at = user.password_reset_expires

    if expires_at and now > expires_at:
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Apply new password and immediately invalidate the single-use token
    user.hashed_password = hash_password(payload.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()

    return {"message": "Password has been reset successfully"}


# ── Current User ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user

