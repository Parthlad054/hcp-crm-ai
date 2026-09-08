"""
repositories/user_repository.py — Raw SQLAlchemy queries for the User model.

All DB access for User records lives here. Services call these functions
and never touch db.query(User) directly.
"""
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email address (case-sensitive)."""
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, user_id: int) -> User | None:
    """Fetch a user by primary key."""
    return db.query(User).filter(User.id == user_id).first()


def get_active_by_id(db: Session, user_id: int) -> User | None:
    """Fetch an active user by primary key — returns None if deactivated."""
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def create(
    db: Session,
    *,
    name: str,
    email: str,
    contact_number: str,
    hashed_password: str,
) -> User:
    """Insert a new user record and return the refreshed ORM object."""
    user = User(
        name=name,
        email=email,
        contact_number=contact_number,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save(db: Session, user: User) -> User:
    """Commit pending changes to an existing user and return the refreshed object."""
    db.commit()
    db.refresh(user)
    return user
