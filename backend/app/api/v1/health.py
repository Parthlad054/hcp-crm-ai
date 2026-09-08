"""
api/v1/health.py — Liveness + readiness health check endpoint.

Extracted from main.py. Returns DB connectivity status so load balancers
can route traffic away from degraded instances.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/", response_model=ApiResponse[dict])
def health(db: Session = Depends(get_db)):
    """
    Liveness + readiness probe.
    Returns 200 {\"status\": \"ok\"} when the DB is reachable,
    or 503 {\"status\": \"degraded\"} with the error when it is not.
    """
    try:
        db.execute(text("SELECT 1"))
        return ApiResponse(
            statusCode=200,
            message="Health check passed",
            data={"status": "ok", "db": "connected"},
        )
    except Exception as exc:  # pragma: no cover
        return ApiResponse(
            statusCode=503,
            message="Health check degraded",
            data={"status": "degraded", "db": str(exc)},
        )
