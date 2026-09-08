"""
main.py — FastAPI application factory.

Lean entry point: wires up middleware, error handlers, rate limiting,
and mounts the versioned API router. No business logic lives here.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.logging import setup_logging
from app.core.rate_limit import limiter

# ── Logging ────────────────────────────────────────────────────────────────────
setup_logging()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI-First CRM — HCP Module",
    description="LangGraph-powered CRM backend for field reps logging HCP interactions.",
    version="1.0.0",
)

# ── Rate limiter ───────────────────────────────────────────────────────────────
# Must be registered before routers so @limiter.limit decorators are recognised.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Error handlers ─────────────────────────────────────────────────────────────
register_error_handlers(app)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Origins are read from ALLOWED_ORIGINS in .env — comma-separated list.
# Default: localhost dev servers only. Override per environment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Router ─────────────────────────────────────────────────────────────────
# All routes are versioned under /api/v1/
app.include_router(api_router, prefix="/api/v1")
