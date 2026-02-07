"""
Tests for PainReliever and GainCreator effectiveness field validators.

Validates that LLM synonym variance is normalized to canonical values
by the @field_validator decorators in src/state/models.py.

PainReliever canonical values: eliminates, reduces, none
GainCreator canonical values:  exceeds, meets, misses
"""

import pytest
from pydantic import ValidationError

from src.state.models import PainReliever, GainCreator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pain_reliever(**overrides) -> PainReliever:
    """Build a PainReliever with sensible defaults, applying overrides."""
    defaults = {
        "id": "pr_001",
        "description": "Reduces manual data entry",
        "addresses_pain_id": "pain_001",
        "effectiveness": "reduces",
    }
    defaults.update(overrides)
    return PainReliever(**defaults)


def _gain_creator(**overrides) -> GainCreator:
    """Build a GainCreator with sensible defaults, applying overrides."""
    defaults = {
        "id": "gc_001",
        "description": "Exceeds reporting expectations",
        "addresses_gain_id": "gain_001",
        "effectiveness": "meets",
    }
    defaults.update(overrides)
    return GainCreator(**defaults)


# ===========================================================================
# PainReliever effectiveness tests
# ===========================================================================

@pytest.mark.parametrize("canonical", ["eliminates", "reduces", "none"])
def test_pain_reliever_accepts_canonical_values(canonical):
    """PainReliever must accept all three canonical effectiveness values."""
    pr = _pain_reliever(effectiveness=canonical)
    assert pr.effectiveness == canonical


@pytest.mark.parametrize(
    "synonym, expected",
    [
        ("mitigates", "reduces"),
        ("alleviates", "reduces"),
        ("partially_reduces", "reduces"),
        ("partially_eliminates", "reduces"),
        ("significantly_reduces", "reduces"),
        ("removes", "eliminates"),
        ("fully_eliminates", "eliminates"),
    ],
)
def test_pain_reliever_normalizes_synonyms(synonym, expected):
    """PainReliever field_validator must map LLM synonyms to canonical values."""
    pr = _pain_reliever(effectiveness=synonym)
    assert pr.effectiveness == expected


def test_pain_reliever_rejects_invalid_value():
    """PainReliever must reject values outside the canonical set and synonym map."""
    with pytest.raises(ValidationError) as exc_info:
        _pain_reliever(effectiveness="unknown_value")

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("effectiveness",) for e in errors)


def test_pain_reliever_strips_whitespace():
    """PainReliever normalizer should strip leading/trailing whitespace."""
    pr = _pain_reliever(effectiveness="  reduces  ")
    assert pr.effectiveness == "reduces"


def test_pain_reliever_case_insensitive():
    """PainReliever normalizer should lowercase before matching."""
    pr = _pain_reliever(effectiveness="Eliminates")
    assert pr.effectiveness == "eliminates"


# ===========================================================================
# GainCreator effectiveness tests
# ===========================================================================

@pytest.mark.parametrize("canonical", ["exceeds", "meets", "misses"])
def test_gain_creator_accepts_canonical_values(canonical):
    """GainCreator must accept all three canonical effectiveness values."""
    gc = _gain_creator(effectiveness=canonical)
    assert gc.effectiveness == canonical


@pytest.mark.parametrize(
    "synonym, expected",
    [
        ("partially_meets", "meets"),
        ("significantly_meets", "meets"),
        ("surpasses", "exceeds"),
        ("far_exceeds", "exceeds"),
        ("falls_short", "misses"),
    ],
)
def test_gain_creator_normalizes_synonyms(synonym, expected):
    """GainCreator field_validator must map LLM synonyms to canonical values."""
    gc = _gain_creator(effectiveness=synonym)
    assert gc.effectiveness == expected


def test_gain_creator_rejects_invalid_value():
    """GainCreator must reject values outside the canonical set and synonym map."""
    with pytest.raises(ValidationError) as exc_info:
        _gain_creator(effectiveness="unknown_value")

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("effectiveness",) for e in errors)


def test_gain_creator_strips_whitespace():
    """GainCreator normalizer should strip leading/trailing whitespace."""
    gc = _gain_creator(effectiveness="  meets  ")
    assert gc.effectiveness == "meets"


def test_gain_creator_case_insensitive():
    """GainCreator normalizer should lowercase before matching."""
    gc = _gain_creator(effectiveness="Exceeds")
    assert gc.effectiveness == "exceeds"
