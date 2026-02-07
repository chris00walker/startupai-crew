"""
Tests for the SEGMENT_PIVOT| envelope parsing in the iterate branch.

The production logic lives in src/modal_app/app.py inside the ``iterate``
decision handler of ``hitl_approve``.  Because that handler is tightly
coupled to Modal + Supabase, we replicate the *parsing logic only* here
to keep the tests dependency-free.

Tested contract:
    feedback = "SEGMENT_PIVOT|{\"target_segment\":\"...\",\"rationale\":\"...\"}"
    -> parsed into pivot context dict with keys:
       pivot_type, pivot_reason, pivot_from_phase, target_segment_hypothesis
"""

import json

import pytest


# ---------------------------------------------------------------------------
# Replicated parsing logic (mirrors app.py iterate branch exactly)
# ---------------------------------------------------------------------------

def parse_segment_pivot_envelope(
    feedback_str: str,
    current_phase: int = 2,
    current_segment: str | None = None,
) -> dict | None:
    """
    Parse a SEGMENT_PIVOT| envelope from HITL iterate feedback.

    Returns the pivot context dict if the envelope is valid and contains a
    non-empty target_segment.  Returns None otherwise.

    This replicates the exact logic in app.py lines 578-606.
    """
    if not feedback_str.startswith("SEGMENT_PIVOT|"):
        return None

    try:
        pivot_json = json.loads(feedback_str[len("SEGMENT_PIVOT|"):])
    except (json.JSONDecodeError, TypeError):
        return None

    target_segment = pivot_json.get("target_segment", "").strip()
    rationale = pivot_json.get("rationale", "").strip()

    if not target_segment:
        return None

    result = {
        "pivot_type": "segment_pivot",
        "pivot_reason": rationale or "Segment pivot requested by user",
        "pivot_from_phase": current_phase,
        "target_segment_hypothesis": {
            "segment_name": target_segment,
            "segment_description": rationale or target_segment,
            "why_better_fit": rationale or "User-specified pivot",
        },
    }

    if current_segment:
        result["failed_segment"] = current_segment

    return result


# ===========================================================================
# Tests
# ===========================================================================

def test_valid_segment_pivot_envelope():
    """A well-formed SEGMENT_PIVOT| envelope is parsed correctly."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"Enterprise IT","rationale":"budget authority"}'
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx is not None
    assert ctx["pivot_type"] == "segment_pivot"
    assert ctx["pivot_reason"] == "budget authority"
    assert ctx["pivot_from_phase"] == 2
    assert ctx["target_segment_hypothesis"]["segment_name"] == "Enterprise IT"
    assert ctx["target_segment_hypothesis"]["segment_description"] == "budget authority"
    assert ctx["target_segment_hypothesis"]["why_better_fit"] == "budget authority"


def test_pivot_from_phase_is_configurable():
    """pivot_from_phase should reflect the current_phase argument."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"SMBs","rationale":"smaller deals"}'
    ctx = parse_segment_pivot_envelope(feedback, current_phase=3)

    assert ctx["pivot_from_phase"] == 3


def test_failed_segment_tracked_when_present():
    """When current_segment is provided, it is stored as failed_segment."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"Healthcare","rationale":"regulated market"}'
    ctx = parse_segment_pivot_envelope(
        feedback,
        current_segment="Fintech Startups",
    )

    assert ctx["failed_segment"] == "Fintech Startups"


def test_failed_segment_absent_when_no_current():
    """When current_segment is None, failed_segment key should not appear."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"Healthcare","rationale":"better fit"}'
    ctx = parse_segment_pivot_envelope(feedback, current_segment=None)

    assert "failed_segment" not in ctx


def test_malformed_json_returns_none():
    """Invalid JSON after the SEGMENT_PIVOT| prefix should be handled gracefully."""
    feedback = "SEGMENT_PIVOT|{not valid json"
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx is None


def test_empty_target_segment_returns_none():
    """An empty target_segment should be treated as invalid."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"","rationale":"no segment"}'
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx is None


def test_whitespace_only_target_segment_returns_none():
    """A whitespace-only target_segment should be treated as invalid."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"   ","rationale":"spaces only"}'
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx is None


def test_missing_target_segment_key_returns_none():
    """Missing target_segment key entirely should return None."""
    feedback = 'SEGMENT_PIVOT|{"rationale":"no target key"}'
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx is None


def test_missing_rationale_uses_defaults():
    """When rationale is absent, sensible defaults fill in."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"Government"}'
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx is not None
    assert ctx["pivot_reason"] == "Segment pivot requested by user"
    assert ctx["target_segment_hypothesis"]["segment_description"] == "Government"
    assert ctx["target_segment_hypothesis"]["why_better_fit"] == "User-specified pivot"


def test_non_pivot_feedback_returns_none():
    """Plain text feedback (no SEGMENT_PIVOT| prefix) should return None."""
    ctx = parse_segment_pivot_envelope("Please add more experiments")

    assert ctx is None


def test_empty_feedback_returns_none():
    """Empty string feedback should return None."""
    ctx = parse_segment_pivot_envelope("")

    assert ctx is None


def test_target_segment_whitespace_is_stripped():
    """Leading and trailing whitespace in target_segment should be stripped."""
    feedback = 'SEGMENT_PIVOT|{"target_segment":"  EdTech  ","rationale":"teachers need it"}'
    ctx = parse_segment_pivot_envelope(feedback)

    assert ctx["target_segment_hypothesis"]["segment_name"] == "EdTech"
