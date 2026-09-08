"""
dependencies.py — Centralised FastAPI dependency injection functions.

All route handlers should import their Depends() functions from here,
not from individual modules. This provides a single point of change
for swapping implementations (e.g. test overrides, future auth schemes).
"""
from app.database import get_db as get_db  # noqa: F401
from app.core.security import get_current_user as get_current_user  # noqa: F401
