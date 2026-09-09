"""
models/base.py — Shared SQLAlchemy mixins for audit tracking and soft deletes.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, BigInteger, ForeignKey, func


class FullAuditMixin:
    """
    Mixin for full audit trail:
    - created_at: when the record was created
    - updated_at: when the record was last modified
    - deleted_at: timestamp for soft delete (NULL means active)
    - created_by: user who created the record (FK to users.id)
    - updated_by: user who last updated the record (FK to users.id)
    - deleted_by: user who soft-deleted the record (FK to users.id)
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    deleted_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def soft_delete(self, user_id: Optional[int] = None) -> None:
        """Mark record as soft-deleted."""
        self.deleted_at = func.now()
        self.deleted_by = user_id


class TimestampAuditMixin:
    """
    Mixin for operational task tracking:
    - created_at: when the task/record was created
    - updated_at: when the task/record was last updated
    - created_by: user who created the task (FK to users.id)
    - updated_by: user who last modified the task (FK to users.id)
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
