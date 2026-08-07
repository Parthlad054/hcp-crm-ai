from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.routers import interactions, chat, hcps, follow_ups, auth
from app.limiter import limiter
from app.config import settings
from app.database import get_db

app = FastAPI(
    title="AI-First CRM — HCP Module",
    description="LangGraph-powered CRM backend for field reps logging HCP interactions.",
    version="0.1.0",
)

# ── Rate limiter ───────────────────────────────────────────────────────────────
# Must be registered before routers so @limiter.limit decorators are recognised.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(hcps.router, prefix="/hcps", tags=["hcps"])
app.include_router(follow_ups.router, prefix="/follow-ups", tags=["follow-ups"])


# ── Health check ───────────────────────────────────────────────────────────────
# Returns DB connectivity status so load balancers can route traffic away from
# degraded instances (e.g. DB connection pool exhausted or DB restart).
@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    """
    Liveness + readiness probe.
    Returns 200 {"status": "ok"} when the DB is reachable,
    or 200 {"status": "degraded"} with the error when it is not.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as exc:  # pragma: no cover
        return {"status": "degraded", "db": str(exc)}
