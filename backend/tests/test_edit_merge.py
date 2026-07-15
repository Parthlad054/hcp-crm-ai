"""Tests for selective edit merge logic (no LLM)."""

from app.agent.tool_response import filter_spurious_patch, merge_form_patch


def test_selective_edit_preserves_untouched_fields():
    baseline = {
        "hcp_name": "Dr. Meera Iyer",
        "date": "2026-07-15",
        "channel": "in-person",
        "products_discussed": ["Neurocalm"],
        "topics_discussed": ["side effects", "dosage"],
        "sentiment": "neutral",
        "samples_given": {"Neurocalm": 2},
        "follow_up_required": True,
        "follow_up_date": "2026-07-20",
    }

    patch = {"hcp_name": "Dr. John", "sentiment": "negative"}
    merged = merge_form_patch(baseline, patch)

    assert merged["hcp_name"] == "Dr. John"
    assert merged["sentiment"] == "negative"
    assert merged["products_discussed"] == ["Neurocalm"]
    assert merged["topics_discussed"] == ["side effects", "dosage"]
    assert merged["date"] == "2026-07-15"
    assert merged["channel"] == "in-person"
    assert merged["samples_given"] == {"Neurocalm": 2}
    assert merged["follow_up_required"] is True
    assert merged["follow_up_date"] == "2026-07-20"


def test_spurious_empty_list_patch_is_ignored():
    baseline = {
        "hcp_name": "Dr. Smith",
        "topics_discussed": ["efficacy", "safety"],
        "products_discussed": ["Cardixin"],
    }
    patch = {"hcp_name": "Dr. John", "topics_discussed": [], "products_discussed": []}
    filtered = filter_spurious_patch(baseline, patch)
    merged = merge_form_patch(baseline, filtered)

    assert merged["hcp_name"] == "Dr. John"
    assert merged["topics_discussed"] == ["efficacy", "safety"]
    assert merged["products_discussed"] == ["Cardixin"]


def test_single_field_name_change_only():
    baseline = {
        "hcp_name": "Dr. Rao",
        "date": "2026-07-15",
        "channel": "call",
        "products_discussed": ["Cardixin"],
        "topics_discussed": ["efficacy"],
        "sentiment": "positive",
    }
    patch = {"hcp_name": "Dr. John"}
    merged = merge_form_patch(baseline, patch)

    assert merged["hcp_name"] == "Dr. John"
    assert merged["date"] == "2026-07-15"
    assert merged["channel"] == "call"
    assert merged["products_discussed"] == ["Cardixin"]
    assert merged["topics_discussed"] == ["efficacy"]
    assert merged["sentiment"] == "positive"
