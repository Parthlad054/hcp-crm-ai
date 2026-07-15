"""ContextVar so tools can read current_form_state without LLM-visible args."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

_current_form_state: ContextVar[dict[str, Any] | None] = ContextVar(
    "current_form_state", default=None
)


def set_current_form_state(form_state: dict[str, Any] | None):
    return _current_form_state.set(form_state)


def reset_current_form_state(token) -> None:
    _current_form_state.reset(token)


def get_current_form_state() -> dict[str, Any] | None:
    return _current_form_state.get()
