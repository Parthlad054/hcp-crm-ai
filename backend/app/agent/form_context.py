"""ContextVar so tools can read current_form_state and current_rep_id without LLM-visible args."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

_current_form_state: ContextVar[dict[str, Any] | None] = ContextVar(
    "current_form_state", default=None
)
_current_rep_id: ContextVar[str | None] = ContextVar("current_rep_id", default=None)


def set_current_form_state(form_state: dict[str, Any] | None):
    return _current_form_state.set(form_state)


def reset_current_form_state(token) -> None:
    _current_form_state.reset(token)


def get_current_form_state() -> dict[str, Any] | None:
    return _current_form_state.get()


def set_current_rep_id(rep_id: str | None):
    return _current_rep_id.set(rep_id)


def reset_current_rep_id(token) -> None:
    _current_rep_id.reset(token)


def get_current_rep_id() -> str | None:
    return _current_rep_id.get()

