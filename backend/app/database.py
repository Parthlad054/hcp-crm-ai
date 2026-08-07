from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # ── Connection pool (scalability & replication resilience) ────────────────
    pool_size=settings.DB_POOL_SIZE,          # persistent connections kept alive
    max_overflow=settings.DB_MAX_OVERFLOW,    # extra connections allowed under spike
    pool_timeout=settings.DB_POOL_TIMEOUT,    # wait time before ConnectionTimeout
    pool_recycle=settings.DB_POOL_RECYCLE,    # recycle to avoid server-side timeouts
    pool_pre_ping=True,                       # validate conn before use (failover safe)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency — use in FastAPI route handlers with Depends(get_db)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
