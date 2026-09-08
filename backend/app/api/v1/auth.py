"""
api/v1/auth.py — HTTP handlers for authentication endpoints.

Thin layer: validates request, delegates to auth_service, returns ApiResponse.
All business logic lives in services/auth_service.py.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.schemas.common import ApiResponse
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter()


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Returns access & refresh tokens plus user payload on success.
    Rate-limited: 3 registrations per IP per minute.
    """
    data = auth_service.register_user(db, payload)
    return ApiResponse(
        statusCode=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=data,
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=ApiResponse[TokenResponse])
@limiter.limit("10/minute")
async def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.
    Returns access & refresh tokens plus user payload on success.
    Rate-limited: 10 attempts per IP per minute (brute-force protection).
    """
    data = auth_service.login_user(db, payload)
    return ApiResponse(
        statusCode=status.HTTP_200_OK,
        message="Login successful",
        data=data,
    )


# ── Refresh Token ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    Old refresh token is implicitly invalidated by issuing a new one.
    """
    data = auth_service.refresh_tokens(db, payload.refresh_token)
    return ApiResponse(
        statusCode=status.HTTP_200_OK,
        message="Token refreshed successfully",
        data=data,
    )


# ── Forgot Password ───────────────────────────────────────────────────────────

@router.post("/forgot-password", response_model=ApiResponse[None], status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Sends a 6-digit OTP to the registered email address.
    Always returns 202 to avoid revealing whether the email exists.
    Rate-limited: 5 requests per IP per minute (prevents email spam/DoS).
    """
    auth_service.initiate_password_reset(db, payload, background_tasks)
    return ApiResponse(
        statusCode=status.HTTP_202_ACCEPTED,
        message="If that email is registered, a 6-digit OTP has been sent.",
        data=None,
    )


# ── Reset Password ────────────────────────────────────────────────────────────

@router.post("/reset-password", response_model=ApiResponse[None])
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Validates the 6-digit OTP and email, then sets a new hashed password.
    The OTP is single-use and cleared immediately after a successful reset.
    Rate-limited: 5 attempts per IP per minute.
    """
    auth_service.reset_password(db, payload)
    return ApiResponse(
        statusCode=status.HTTP_200_OK,
        message="Password has been reset successfully",
        data=None,
    )


# ── Current User ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=ApiResponse[UserOut])
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return ApiResponse(
        statusCode=status.HTTP_200_OK,
        message="User profile fetched successfully",
        data=UserOut.model_validate(current_user),
    )
