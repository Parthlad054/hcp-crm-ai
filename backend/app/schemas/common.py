from datetime import date, datetime
from typing import Annotated, Any, Generic, Optional, TypeVar
from pydantic import BaseModel, BeforeValidator, PlainSerializer

T = TypeVar("T")


def parse_date_dmy(v: Any) -> Optional[date]:
    """
    Parse date from DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD.
    Returns a datetime.date object.
    """
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                continue
    raise ValueError(f"Invalid date format: {v}. Expected date-month-year (DD-MM-YYYY).")


def serialize_date_dmy(v: Optional[date]) -> Optional[str]:
    """
    Serialize datetime.date to string in DD-MM-YYYY format.
    """
    if v is None:
        return None
    if isinstance(v, (date, datetime)):
        return v.strftime("%d-%m-%Y")
    return str(v)


# Pydantic type for Date in DD-MM-YYYY format
DMYDate = Annotated[
    date,
    BeforeValidator(parse_date_dmy),
    PlainSerializer(serialize_date_dmy, return_type=str, when_used="json-unless-none"),
]


class ApiResponse(BaseModel, Generic[T]):
    statusCode: int = 200
    message: str = "Success"
    data: Optional[T] = None


class FullAuditOut(BaseModel):
    """Common output schema for full audit and soft delete tracking."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None


class TimestampAuditOut(BaseModel):
    """Common output schema for timestamp and creator/updater tracking."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
