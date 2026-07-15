"""Shared helpers for LangGraph tool return envelopes."""

from __future__ import annotations

import json
from typing import Any


def tool_envelope(reply: str, form_data: dict[str, Any] | None = None) -> str:
    """Serialize the standard tool response: {reply, form_data}."""
    return json.dumps({"reply": reply, "form_data": form_data})


def parse_tool_envelope(content: str) -> tuple[str, dict[str, Any] | None]:
    """Parse a tool message into (reply, form_data). Falls back to raw content."""
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "reply" in parsed:
            return parsed["reply"], parsed.get("form_data")
    except (json.JSONDecodeError, TypeError):
        pass
    return content, None


def extracted_to_form_data(extracted, *, channel: str = "in-person", summary: str | None = None) -> dict[str, Any]:
    """Map InteractionExtraction (or similar) into the API form_data shape."""
    follow_up_date = getattr(extracted, "follow_up_date", None)
    interaction_date = getattr(extracted, "interaction_date", None)
    data: dict[str, Any] = {
        "hcp_name": getattr(extracted, "hcp_name", None),
        "date": str(interaction_date) if interaction_date else None,
        "channel": channel,
        "products_discussed": list(getattr(extracted, "products_discussed", None) or []),
        "topics_discussed": list(getattr(extracted, "topics_discussed", None) or []),
        "sentiment": getattr(extracted, "sentiment", None),
        "samples_given": dict(getattr(extracted, "samples_given", None) or {}),
        "follow_up_required": bool(getattr(extracted, "follow_up_required", False)),
        "follow_up_date": str(follow_up_date) if follow_up_date else None,
    }
    if summary is not None:
        data["summary"] = summary
    return data


def baseline_form_state(form_state: dict[str, Any] | None) -> dict[str, Any]:
    """Use current_form_state as-is for edit baseline (only normalize date alias)."""
    if not form_state:
        return {}
    baseline = dict(form_state)
    if baseline.get("date") is None and baseline.get("interaction_date") is not None:
        baseline["date"] = baseline["interaction_date"]
    return baseline


def filter_spurious_patch(baseline: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """
    Drop patch keys that would accidentally wipe existing values
    (e.g. LLM returning empty lists for fields not mentioned in the correction).
    """
    filtered: dict[str, Any] = {}
    for key, value in patch.items():
        if value is None:
            continue
        current = baseline.get(key)
        if value == [] and current not in (None, [], ""):
            continue
        if value == {} and current not in (None, {}, ""):
            continue
        filtered[key] = value
    return filtered


def merge_form_patch(current: dict[str, Any] | None, patch: dict[str, Any]) -> dict[str, Any]:
    """Shallow merge: {**current_form_state, **llm_patch} — untouched keys stay identical."""
    base = dict(current or {})
    safe_patch = filter_spurious_patch(base, patch)
    return {**base, **safe_patch}


def format_field_label(field: str) -> str:
    labels = {
        "hcp_name": "HCP name",
        "date": "date",
        "channel": "channel",
        "topics_discussed": "topics discussed",
        "products_discussed": "products discussed",
        "sentiment": "sentiment",
        "samples_given": "samples given",
        "follow_up_required": "follow-up required",
        "follow_up_date": "follow-up date",
        "summary": "summary",
    }
    return labels.get(field, field.replace("_", " "))


def format_edit_reply(baseline: dict[str, Any], patch: dict[str, Any]) -> str:
    """Build a confirmation listing only fields that actually changed."""
    changes = []
    for key, new_value in patch.items():
        old_value = baseline.get(key)
        if old_value != new_value:
            changes.append(f"{format_field_label(key)} to {new_value}")

    if not changes:
        return "No fields needed updating based on your correction."

    if len(changes) == 1:
        return f"Updated {changes[0]} — everything else stayed the same."

    joined = ", ".join(changes[:-1]) + f", and {changes[-1]}"
    return f"Updated {joined} — everything else stayed the same."
