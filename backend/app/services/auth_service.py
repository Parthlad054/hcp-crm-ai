"""
services/auth_service.py — Business logic for authentication flows.

Extracted from app/routers/auth.py. Handles registration, login,
token refresh, forgot-password OTP, and password reset.
Routers call these functions and just wrap results in ApiResponse.
"""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.integrations.email_client import send_reset_email
from app.repositories import user_repository
from app.schemas.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserOut

logger = logging.getLogger(__name__)


def register_user(db: Session, payload: UserRegister) -> TokenResponse:
    """
    Create a new user account.
    Raises 409 if the email is already registered.
    Returns a JWT token pair + user profile on success.
    """
    existing = user_repository.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = user_repository.create(
        db,
        name=payload.name,
        email=payload.email,
        contact_number=payload.contact_number,
        hashed_password=hash_password(payload.password),
    )
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )


def login_user(db: Session, payload: UserLogin) -> TokenResponse:
    """
    Authenticate with email + password.
    Raises 401 for invalid credentials (vague to prevent enumeration).
    Raises 403 if account is deactivated.
    Returns a JWT token pair + user profile on success.
    """
    user = user_repository.get_by_email(db, payload.email)
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


def refresh_tokens(db: Session, refresh_token: str) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    Raises 401 if the token is invalid, expired, or the user is inactive.
    """
    user_id = decode_token(refresh_token, expected_type="refresh")
    user = user_repository.get_active_by_id(db, user_id)
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


def initiate_password_reset(
    db: Session,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
) -> None:
    """
    Generate a 6-digit OTP and fire a password-reset email in the background.
    Silently no-ops for unknown emails (prevents enumeration — caller returns 202 either way).
    """
    user = user_repository.get_by_email(db, payload.email)
    if not user:
        return  # Prevent user enumeration

    otp = f"{secrets.randbelow(1_000_000):06d}"
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    user.password_reset_token = otp_hash
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
    )
    user_repository.save(db, user)

    # Fire-and-forget — email is sent in background so endpoint responds immediately
    background_tasks.add_task(send_reset_email, user.email, user.name, otp)
    logger.info("Password reset OTP generated for user %s", user.id)


def reset_password(db: Session, payload: ResetPasswordRequest) -> None:
    """
    Validate the 6-digit OTP and set a new hashed password.
    The OTP is single-use and cleared immediately after a successful reset.
    Raises 400 for invalid, expired, or already-used OTPs.
    """
    _INVALID = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired OTP",
    )

    user = user_repository.get_by_email(db, payload.email)
    if not user or not user.is_active or not user.password_reset_token:
        raise _INVALID

    # Verify expiration first (before doing the hash comparison)
    now = datetime.now(timezone.utc)
    expires_at = user.password_reset_expires
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at is None or now > expires_at:
        user.password_reset_token = None
        user.password_reset_expires = None
        user_repository.save(db, user)
        raise _INVALID

    # Constant-time comparison via hashing (prevents timing attacks)
    submitted_hash = hashlib.sha256(payload.otp.encode()).hexdigest()
    if not secrets.compare_digest(submitted_hash, user.password_reset_token):
        raise _INVALID

    # Apply new password and immediately invalidate the single-use OTP
    user.hashed_password = hash_password(payload.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user_repository.save(db, user)
    logger.info("Password reset successfully for user %s", user.id)
