"""
Segment Alternatives Generator

When a segment pivot is recommended (NO_INTEREST signal), this module generates
alternative customer segments for the founder to choose from.

Uses direct OpenAI API call for efficiency (no full CrewAI machinery needed).
"""

import json
import logging
import os
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)


def generate_alternative_segments(
    founders_brief: dict[str, Any],
    failed_segment: dict[str, Any],
    desirability_evidence: dict[str, Any],
    num_alternatives: int = 3,
) -> list[dict[str, Any]]:
    """
    Generate alternative customer segments based on the failed validation.

    Args:
        founders_brief: The original founder's brief with business idea
        failed_segment: The customer profile that didn't resonate
        desirability_evidence: Evidence from Phase 2 showing what failed
        num_alternatives: Number of alternatives to generate (default 3)

    Returns:
        List of alternative segments with confidence scores, sorted by confidence
    """
    # Input validation - log what we receive for debugging
    logger.info(json.dumps({
        "event": "segment_alternatives_input",
        "founders_brief_keys": list(founders_brief.keys()) if founders_brief else [],
        "failed_segment_keys": list(failed_segment.keys()) if failed_segment else [],
        "desirability_evidence_keys": list(desirability_evidence.keys()) if desirability_evidence else [],
    }))

    # Check for missing/empty inputs
    if not founders_brief:
        logger.warning("generate_alternative_segments called with empty founders_brief")
        return [{
            "segment_name": "Custom Segment (Missing Data)",
            "segment_description": "No founder's brief data available for segment generation.",
            "why_better_fit": "Please specify a custom segment.",
            "confidence": 0.0,
            "_error": "missing_founders_brief",
        }]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set")
        return [{
            "segment_name": "Custom Segment (API Error)",
            "segment_description": "OpenAI API key not configured.",
            "why_better_fit": "Please specify a custom segment.",
            "confidence": 0.0,
            "_error": "missing_api_key",
        }]

    client = OpenAI(api_key=api_key)

    # Extract key info
    one_liner = founders_brief.get("the_idea", {}).get("one_liner", "")
    problem = founders_brief.get("the_idea", {}).get("problem_statement", "")
    failed_segment_name = failed_segment.get("segment_name", "Unknown") if failed_segment else "Unknown"
    failed_segment_desc = failed_segment.get("segment_description", "") if failed_segment else ""

    # Extract failure evidence (be defensive about missing/malformed data)
    problem_resonance = desirability_evidence.get("problem_resonance", 0) if desirability_evidence else 0
    zombie_ratio = desirability_evidence.get("zombie_ratio", 1) if desirability_evidence else 1

    prompt = f"""You are a startup strategy expert. A validation test has failed, and we need alternative customer segments to test.

## BUSINESS IDEA
{one_liner}

Problem Statement: {problem}

## FAILED SEGMENT
Name: {failed_segment_name}
Description: {failed_segment_desc}

## WHY IT FAILED
- Problem Resonance: {problem_resonance:.1%} (below 30% threshold - customers don't feel the pain)
- Zombie Ratio: {zombie_ratio:.1%} (customers acknowledge problem but don't take action)

## YOUR TASK
Propose {num_alternatives} alternative customer segments that might be a better fit for this product. For each segment:

1. Consider who ELSE might have this problem more acutely
2. Think about adjacent markets or different company sizes
3. Consider segments where the pain is more urgent/expensive
4. Look for segments with higher willingness to pay

For each alternative, provide:
- segment_name: Clear, specific segment name
- segment_description: 2-3 sentence description of who they are
- why_better_fit: Why this segment might resonate more with the problem
- confidence: Your confidence score (0.0-1.0) that this segment will show stronger interest

Return as JSON array, sorted by confidence (highest first).

Example format:
[
  {{
    "segment_name": "Enterprise SaaS Customer Success Teams",
    "segment_description": "B2B SaaS companies with 1000+ customers...",
    "why_better_fit": "Higher support volume and cost pressure...",
    "confidence": 0.75
  }}
]

IMPORTANT: The alternatives should be meaningfully DIFFERENT from the failed segment, not just variations."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a startup strategy expert specializing in customer segmentation and market validation."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        # Handle both direct array and wrapped object
        alternatives = result if isinstance(result, list) else result.get("alternatives", result.get("segments", []))

        # Sort by confidence (highest first)
        alternatives = sorted(alternatives, key=lambda x: x.get("confidence", 0), reverse=True)

        logger.info(json.dumps({
            "event": "segment_alternatives_generated",
            "num_alternatives": len(alternatives),
            "top_confidence": alternatives[0].get("confidence") if alternatives else 0,
        }))

        return alternatives

    except Exception as e:
        error_msg = str(e)
        logger.error(json.dumps({
            "event": "segment_alternatives_error",
            "error": error_msg,
            "founders_brief_keys": list(founders_brief.keys()) if founders_brief else [],
            "failed_segment_name": failed_segment.get("segment_name", "unknown"),
        }))
        # Return a fallback alternative with error info so HITL has something to show
        # This ensures the pivot flow doesn't break silently
        return [
            {
                "segment_name": "Custom Segment (Generation Failed)",
                "segment_description": f"Automatic segment generation failed: {error_msg}. Please specify a custom segment.",
                "why_better_fit": "Unable to generate alternatives - please choose 'Specify Different Segment' option.",
                "confidence": 0.0,
                "_error": error_msg,
            }
        ]


def format_segment_options(
    alternatives: list[dict[str, Any]],
    include_custom: bool = True,
    include_override: bool = True,
    include_iterate: bool = True,
) -> list[dict[str, Any]]:
    """
    Format alternative segments as HITL options for the founder to choose from.

    Args:
        alternatives: List of alternative segments from generate_alternative_segments
        include_custom: Include option for founder to specify custom segment
        include_override: Include option to override and proceed anyway
        include_iterate: Include option to run more experiments

    Returns:
        List of HITL options formatted for the approval UI
    """
    options = []

    # Add each alternative as an option
    for i, alt in enumerate(alternatives):
        confidence = alt.get("confidence", 0)
        confidence_label = ""
        if confidence >= 0.7:
            confidence_label = " (Recommended)"
        elif confidence >= 0.5:
            confidence_label = " (Promising)"

        options.append({
            "id": f"segment_{i+1}",
            "label": f"{alt['segment_name']}{confidence_label}",
            "description": alt.get("why_better_fit", alt.get("segment_description", "")),
            "segment_data": {
                "segment_name": alt["segment_name"],
                "segment_description": alt.get("segment_description", ""),
                "confidence": confidence,
            },
        })

    # Add custom segment option
    if include_custom:
        options.append({
            "id": "custom_segment",
            "label": "Specify Different Segment",
            "description": "Enter your own customer segment hypothesis to test",
            "requires_input": True,
            "input_placeholder": "Describe your target customer segment...",
        })

    # Add override option
    if include_override:
        options.append({
            "id": "override_proceed",
            "label": "Override - Proceed Anyway",
            "description": "Ignore the pivot signal and continue to Phase 3 (requires justification)",
            "requires_input": True,
            "input_placeholder": "Explain why you want to proceed despite low interest...",
        })

    # Add iterate option
    if include_iterate:
        options.append({
            "id": "iterate",
            "label": "Run More Experiments",
            "description": "Gather additional evidence with current segment before deciding",
        })

    return options
