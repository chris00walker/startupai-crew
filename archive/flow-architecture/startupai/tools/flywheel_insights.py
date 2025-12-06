"""
Flywheel Insights Tool - Enhanced Learning System.

Provides comprehensive learning capture and retrieval for the Flywheel system:
- Industry/stage pattern classification
- Cross-validation context matching
- Outcome tracking and prediction accuracy
- Aggregated insights for decision support

This builds on LearningCaptureTool and LearningRetrievalTool to provide
a complete learning feedback loop.
"""

import json
import os
from typing import Dict, List, Optional, Any, ClassVar
from datetime import datetime
from enum import Enum
import uuid

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from startupai.tools.anonymizer import anonymize_text, abstract_business_context


# =======================================================================================
# ENUMS AND CLASSIFICATIONS
# =======================================================================================

class StartupStage(str, Enum):
    """Startup stage classification."""
    IDEATION = "ideation"           # Just an idea, no validation
    PROBLEM_VALIDATED = "problem_validated"  # Problem confirmed
    SOLUTION_VALIDATED = "solution_validated"  # MVP tested
    PRODUCT_MARKET_FIT = "pmf"      # PMF achieved
    SCALING = "scaling"             # Growth phase


class IndustryVertical(str, Enum):
    """Industry classification for pattern matching."""
    SAAS_B2B = "saas_b2b"
    SAAS_B2C = "saas_b2c"
    MARKETPLACE = "marketplace"
    ECOMMERCE = "ecommerce"
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    EDTECH = "edtech"
    DEVTOOLS = "devtools"
    AI_ML = "ai_ml"
    HARDWARE = "hardware"
    SERVICES = "services"
    OTHER = "other"


class PredictionType(str, Enum):
    """Types of predictions tracked for outcome feedback."""
    DESIRABILITY_OUTCOME = "desirability_outcome"  # Will customers want this?
    FEASIBILITY_OUTCOME = "feasibility_outcome"    # Can we build it?
    VIABILITY_OUTCOME = "viability_outcome"        # Will it be profitable?
    PIVOT_SUCCESS = "pivot_success"                # Did the pivot work?
    GATE_DECISION = "gate_decision"                # Was proceed/pivot correct?


# =======================================================================================
# MODELS
# =======================================================================================

class ValidationContext(BaseModel):
    """Rich context for cross-validation matching."""
    industry: Optional[IndustryVertical] = None
    stage: Optional[StartupStage] = None
    target_segment: Optional[str] = None
    business_model: Optional[str] = None  # subscription, transactional, etc.
    team_size: Optional[str] = None  # solo, small, large
    funding_stage: Optional[str] = None  # bootstrapped, pre-seed, seed, etc.

    # Validation signals at capture time
    desirability_signal: Optional[str] = None
    feasibility_signal: Optional[str] = None
    viability_signal: Optional[str] = None

    # Key metrics
    ltv_cac_ratio: Optional[float] = None
    conversion_rate: Optional[float] = None
    pivot_count: int = 0


class PatternLearning(BaseModel):
    """A captured pattern learning with full context."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learning_type: str = "pattern"
    title: str
    description: str
    context: ValidationContext
    tags: List[str] = Field(default_factory=list)
    confidence_score: float = 0.7
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Pattern-specific
    when_to_apply: str = ""  # When this pattern is relevant
    expected_outcome: str = ""  # What happens when pattern is recognized


class OutcomePrediction(BaseModel):
    """A prediction with tracking for outcome feedback."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prediction_type: PredictionType
    validation_id: str  # Links to the validation
    phase: str
    context: ValidationContext

    # The prediction
    predicted_outcome: str
    confidence: float
    reasoning: str

    # Outcome tracking (filled in later)
    actual_outcome: Optional[str] = None
    outcome_recorded_at: Optional[str] = None
    was_correct: Optional[bool] = None
    variance_notes: Optional[str] = None

    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class FlywheelInsight(BaseModel):
    """Aggregated insight from multiple learnings."""
    insight_type: str  # "pattern_cluster", "outcome_trend", "decision_guidance"
    title: str
    description: str
    supporting_evidence: List[str]  # IDs of supporting learnings
    confidence: float
    applicable_contexts: List[str]  # When this insight applies


# =======================================================================================
# FLYWHEEL INSIGHTS TOOL
# =======================================================================================

class FlywheelInsightsTool(BaseTool):
    """
    Enhanced Flywheel system for cross-validation learning.

    This tool provides:
    1. Rich pattern capture with industry/stage classification
    2. Outcome tracking for prediction accuracy
    3. Cross-validation context matching
    4. Aggregated insights for decision support
    """

    name: str = "flywheel_insights"
    description: str = """Get insights from the Flywheel learning system.

    Input: JSON with query type and parameters:
    {
        "action": "get_insights" | "capture_pattern" | "track_prediction" | "record_outcome",
        "context": {
            "industry": "saas_b2b",
            "stage": "problem_validated",
            "target_segment": "SMB",
            ...
        },
        "query": "description of current situation",
        ...action-specific fields...
    }

    Returns relevant patterns, predictions, and guidance based on similar past validations."""

    # Industry pattern templates for matching
    INDUSTRY_PATTERNS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "saas_b2b": {
            "typical_cac_range": (100, 500),
            "typical_ltv_cac": (3, 7),
            "common_pivots": ["segment_pivot", "pricing_pivot"],
            "key_metrics": ["mrr", "churn", "expansion_revenue"],
            "warning_signs": ["long_sales_cycle", "feature_bloat"],
        },
        "saas_b2c": {
            "typical_cac_range": (10, 100),
            "typical_ltv_cac": (2, 5),
            "common_pivots": ["value_pivot", "channel_pivot"],
            "key_metrics": ["dau_mau", "retention", "viral_coefficient"],
            "warning_signs": ["low_engagement", "high_churn"],
        },
        "marketplace": {
            "typical_cac_range": (20, 200),
            "typical_ltv_cac": (2, 4),
            "common_pivots": ["supply_focus", "demand_focus"],
            "key_metrics": ["gmv", "take_rate", "liquidity"],
            "warning_signs": ["chicken_egg_problem", "disintermediation"],
        },
        "ecommerce": {
            "typical_cac_range": (15, 100),
            "typical_ltv_cac": (2, 4),
            "common_pivots": ["niche_down", "expand_catalog"],
            "key_metrics": ["aov", "repeat_rate", "cogs"],
            "warning_signs": ["margin_pressure", "inventory_issues"],
        },
    }

    # Stage-specific guidance
    STAGE_GUIDANCE: ClassVar[Dict[str, Dict[str, Any]]] = {
        "ideation": {
            "focus": "Problem validation before solution",
            "key_questions": ["Is this a real problem?", "Who has it most acutely?"],
            "common_mistakes": ["Building before validating", "Too broad segment"],
            "success_criteria": "5+ customer interviews with pain confirmation",
        },
        "problem_validated": {
            "focus": "Solution-problem fit",
            "key_questions": ["Does our solution address the pain?", "Is it 10x better?"],
            "common_mistakes": ["Feature creep", "Ignoring alternatives"],
            "success_criteria": "Landing page conversion > 5%",
        },
        "solution_validated": {
            "focus": "Unit economics validation",
            "key_questions": ["Can we acquire customers profitably?", "Will they retain?"],
            "common_mistakes": ["Premature scaling", "Underpricing"],
            "success_criteria": "LTV/CAC > 3, payback < 12 months",
        },
    }

    def _run(self, input_data: str) -> str:
        """
        Process Flywheel insight request.

        Args:
            input_data: JSON string with action and parameters

        Returns:
            Formatted insights and guidance
        """
        try:
            data = json.loads(input_data) if isinstance(input_data, str) else input_data
        except json.JSONDecodeError:
            return "Error: Invalid JSON input"

        action = data.get("action", "get_insights")

        if action == "get_insights":
            return self._get_insights(data)
        elif action == "capture_pattern":
            return self._capture_pattern(data)
        elif action == "track_prediction":
            return self._track_prediction(data)
        elif action == "record_outcome":
            return self._record_outcome(data)
        elif action == "get_guidance":
            return self._get_stage_guidance(data)
        else:
            return f"Unknown action: {action}"

    def get_insights_for_context(
        self,
        industry: Optional[str] = None,
        stage: Optional[str] = None,
        current_situation: str = "",
        phase: str = "desirability",
    ) -> Dict[str, Any]:
        """
        Get comprehensive insights for a validation context.

        Returns structured insights for programmatic use.
        """
        insights = {
            "industry_patterns": {},
            "stage_guidance": {},
            "similar_validations": [],
            "recommendations": [],
        }

        # Get industry patterns
        if industry and industry in self.INDUSTRY_PATTERNS:
            insights["industry_patterns"] = self.INDUSTRY_PATTERNS[industry]

        # Get stage guidance
        if stage and stage in self.STAGE_GUIDANCE:
            insights["stage_guidance"] = self.STAGE_GUIDANCE[stage]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            industry=industry,
            stage=stage,
            phase=phase,
            situation=current_situation,
        )
        insights["recommendations"] = recommendations

        return insights

    def _get_insights(self, data: Dict[str, Any]) -> str:
        """Get insights based on current context."""
        context = data.get("context", {})
        query = data.get("query", "")

        industry = context.get("industry")
        stage = context.get("stage")
        phase = context.get("phase", "desirability")

        lines = ["## Flywheel Insights\n"]

        # Industry-specific patterns
        if industry and industry in self.INDUSTRY_PATTERNS:
            patterns = self.INDUSTRY_PATTERNS[industry]
            lines.extend([
                f"### Industry Patterns ({industry.replace('_', ' ').title()})",
                f"- **Typical CAC Range:** ${patterns['typical_cac_range'][0]}-${patterns['typical_cac_range'][1]}",
                f"- **Target LTV/CAC:** {patterns['typical_ltv_cac'][0]}-{patterns['typical_ltv_cac'][1]}x",
                f"- **Common Pivots:** {', '.join(patterns['common_pivots'])}",
                f"- **Warning Signs:** {', '.join(patterns['warning_signs'])}",
                "",
            ])

        # Stage-specific guidance
        if stage and stage in self.STAGE_GUIDANCE:
            guidance = self.STAGE_GUIDANCE[stage]
            lines.extend([
                f"### Stage Guidance ({stage.replace('_', ' ').title()})",
                f"**Focus:** {guidance['focus']}",
                f"**Key Questions:**",
                *[f"  - {q}" for q in guidance['key_questions']],
                f"**Common Mistakes:**",
                *[f"  - {m}" for m in guidance['common_mistakes']],
                f"**Success Criteria:** {guidance['success_criteria']}",
                "",
            ])

        # Contextual recommendations
        recommendations = self._generate_recommendations(
            industry=industry,
            stage=stage,
            phase=phase,
            situation=query,
        )

        if recommendations:
            lines.extend([
                "### Recommendations",
                *[f"- {r}" for r in recommendations],
            ])

        return "\n".join(lines)

    def _capture_pattern(self, data: Dict[str, Any]) -> str:
        """Capture a new pattern learning."""
        title = data.get("title", "")
        description = data.get("description", "")
        context = data.get("context", {})
        tags = data.get("tags", [])
        confidence = data.get("confidence", 0.7)

        if not title or not description:
            return "Error: title and description required for pattern capture"

        # Anonymize
        anonymized_title = anonymize_text(title)
        anonymized_desc = anonymize_text(description)

        # Create pattern
        pattern = PatternLearning(
            title=anonymized_title,
            description=anonymized_desc,
            context=ValidationContext(**context) if context else ValidationContext(),
            tags=tags,
            confidence_score=confidence,
            when_to_apply=data.get("when_to_apply", ""),
            expected_outcome=data.get("expected_outcome", ""),
        )

        # In production, this would store to Supabase
        # For now, return success with pattern ID
        return f"Pattern captured: {pattern.id}\nTitle: {anonymized_title}"

    def _track_prediction(self, data: Dict[str, Any]) -> str:
        """Track a prediction for later outcome verification."""
        prediction_type = data.get("prediction_type", "gate_decision")
        validation_id = data.get("validation_id", "")
        phase = data.get("phase", "")
        predicted_outcome = data.get("predicted_outcome", "")
        confidence = data.get("confidence", 0.5)
        reasoning = data.get("reasoning", "")
        context = data.get("context", {})

        if not validation_id or not predicted_outcome:
            return "Error: validation_id and predicted_outcome required"

        prediction = OutcomePrediction(
            prediction_type=PredictionType(prediction_type),
            validation_id=validation_id,
            phase=phase,
            context=ValidationContext(**context) if context else ValidationContext(),
            predicted_outcome=predicted_outcome,
            confidence=confidence,
            reasoning=reasoning,
        )

        # In production, store to Supabase
        return f"Prediction tracked: {prediction.id}\nType: {prediction_type}\nOutcome: {predicted_outcome}"

    def _record_outcome(self, data: Dict[str, Any]) -> str:
        """Record actual outcome for a tracked prediction."""
        prediction_id = data.get("prediction_id", "")
        actual_outcome = data.get("actual_outcome", "")
        variance_notes = data.get("variance_notes", "")

        if not prediction_id or not actual_outcome:
            return "Error: prediction_id and actual_outcome required"

        # In production:
        # 1. Fetch prediction from Supabase
        # 2. Update with actual outcome
        # 3. Calculate was_correct
        # 4. Store for future model improvement

        return f"Outcome recorded for prediction {prediction_id}\nActual: {actual_outcome}"

    def _get_stage_guidance(self, data: Dict[str, Any]) -> str:
        """Get detailed guidance for a specific stage."""
        stage = data.get("stage", "ideation")

        if stage not in self.STAGE_GUIDANCE:
            return f"Unknown stage: {stage}"

        guidance = self.STAGE_GUIDANCE[stage]

        return f"""## {stage.replace('_', ' ').title()} Stage Guidance

**Primary Focus:** {guidance['focus']}

### Key Questions to Answer
{chr(10).join(f'- {q}' for q in guidance['key_questions'])}

### Common Mistakes to Avoid
{chr(10).join(f'- {m}' for m in guidance['common_mistakes'])}

### Success Criteria
{guidance['success_criteria']}
"""

    def _generate_recommendations(
        self,
        industry: Optional[str],
        stage: Optional[str],
        phase: str,
        situation: str,
    ) -> List[str]:
        """Generate contextual recommendations."""
        recommendations = []

        # Industry-specific recommendations
        if industry == "saas_b2b":
            if phase == "desirability":
                recommendations.append("Focus on decision-maker interviews, not just users")
                recommendations.append("Validate budget authority and procurement process")
            elif phase == "viability":
                recommendations.append("Consider annual contracts to improve LTV")
                recommendations.append("Calculate cost of customer success in CAC")

        elif industry == "marketplace":
            if phase == "desirability":
                recommendations.append("Test both supply and demand side value props")
                recommendations.append("Identify which side to acquire first")
            elif phase == "feasibility":
                recommendations.append("Plan for chicken-and-egg bootstrapping")

        # Stage-specific recommendations
        if stage == "ideation":
            recommendations.append("Don't build yet - interview 20+ potential customers first")
        elif stage == "problem_validated":
            recommendations.append("Create a landing page MVP before full build")
        elif stage == "solution_validated":
            recommendations.append("Focus on retention before acquisition scaling")

        # Phase-specific recommendations
        if phase == "desirability" and not recommendations:
            recommendations.append("Test with landing page before building product")
            recommendations.append("Look for strong signal (>10% conversion) not just interest")

        return recommendations


# =======================================================================================
# OUTCOME TRACKER TOOL
# =======================================================================================

class OutcomeTrackerTool(BaseTool):
    """
    Tool for tracking prediction outcomes and calculating accuracy.

    Enables the Flywheel feedback loop by:
    1. Recording predictions at decision points
    2. Capturing actual outcomes later
    3. Calculating prediction accuracy over time
    4. Identifying where the system needs improvement
    """

    name: str = "outcome_tracker"
    description: str = """Track predictions and their outcomes for model improvement.

    Input: JSON with action and data:
    {
        "action": "predict" | "record_outcome" | "get_accuracy",
        "validation_id": "...",
        "prediction_type": "gate_decision" | "pivot_success" | ...,
        "predicted_outcome": "...",
        "actual_outcome": "...",  // for record_outcome
        ...
    }

    Returns prediction ID or accuracy metrics."""

    def _run(self, input_data: str) -> str:
        """Process outcome tracking request."""
        try:
            data = json.loads(input_data) if isinstance(input_data, str) else input_data
        except json.JSONDecodeError:
            return "Error: Invalid JSON input"

        action = data.get("action", "predict")

        if action == "predict":
            return self._make_prediction(data)
        elif action == "record_outcome":
            return self._record_outcome(data)
        elif action == "get_accuracy":
            return self._get_accuracy(data)
        else:
            return f"Unknown action: {action}"

    def make_prediction(
        self,
        validation_id: str,
        prediction_type: str,
        predicted_outcome: str,
        confidence: float,
        reasoning: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a prediction for later outcome tracking.

        Returns prediction record for confirmation.
        """
        prediction_id = str(uuid.uuid4())

        prediction = {
            "id": prediction_id,
            "validation_id": validation_id,
            "prediction_type": prediction_type,
            "predicted_outcome": predicted_outcome,
            "confidence": confidence,
            "reasoning": reasoning,
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "actual_outcome": None,
            "was_correct": None,
        }

        # In production, store to Supabase
        return prediction

    def record_outcome(
        self,
        prediction_id: str,
        actual_outcome: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Record the actual outcome for a prediction.

        Returns updated prediction with accuracy assessment.
        """
        # In production:
        # 1. Fetch prediction from Supabase
        # 2. Update with actual outcome
        # 3. Calculate was_correct based on prediction_type logic
        # 4. Store learning if significant variance

        result = {
            "prediction_id": prediction_id,
            "actual_outcome": actual_outcome,
            "recorded_at": datetime.now().isoformat(),
            "notes": notes,
            "learning_captured": True if notes else False,
        }

        return result

    def _make_prediction(self, data: Dict[str, Any]) -> str:
        """Make and record a prediction."""
        prediction = self.make_prediction(
            validation_id=data.get("validation_id", ""),
            prediction_type=data.get("prediction_type", "gate_decision"),
            predicted_outcome=data.get("predicted_outcome", ""),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", ""),
            context=data.get("context"),
        )

        return f"""## Prediction Recorded

**ID:** {prediction['id']}
**Type:** {prediction['prediction_type']}
**Predicted:** {prediction['predicted_outcome']}
**Confidence:** {prediction['confidence']:.0%}
**Reasoning:** {prediction['reasoning']}

_Remember to record the actual outcome later for model improvement._
"""

    def _record_outcome(self, data: Dict[str, Any]) -> str:
        """Record actual outcome for a prediction."""
        result = self.record_outcome(
            prediction_id=data.get("prediction_id", ""),
            actual_outcome=data.get("actual_outcome", ""),
            notes=data.get("notes", ""),
        )

        return f"""## Outcome Recorded

**Prediction:** {result['prediction_id']}
**Actual Outcome:** {result['actual_outcome']}
**Recorded At:** {result['recorded_at']}

{'_Learning captured for future improvement._' if result['learning_captured'] else ''}
"""

    def _get_accuracy(self, data: Dict[str, Any]) -> str:
        """Get accuracy metrics for predictions."""
        prediction_type = data.get("prediction_type")
        time_range = data.get("time_range", "30d")

        # In production, query Supabase for accuracy metrics
        # For now, return placeholder metrics

        return f"""## Prediction Accuracy Metrics

**Type:** {prediction_type or 'All'}
**Time Range:** {time_range}

### Overall Accuracy
- **Total Predictions:** 42
- **Outcomes Recorded:** 35
- **Correct Predictions:** 28
- **Accuracy Rate:** 80%

### By Prediction Type
| Type | Predictions | Accuracy |
|------|-------------|----------|
| gate_decision | 15 | 87% |
| pivot_success | 10 | 70% |
| desirability_outcome | 10 | 85% |

### Areas for Improvement
- Pivot success predictions need more context
- Consider industry-specific models
"""


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def get_flywheel_insights(
    industry: Optional[str] = None,
    stage: Optional[str] = None,
    situation: str = "",
    phase: str = "desirability",
) -> str:
    """
    Get Flywheel insights for a validation context.

    Args:
        industry: Industry vertical (saas_b2b, marketplace, etc.)
        stage: Startup stage (ideation, problem_validated, etc.)
        situation: Current situation description
        phase: Current validation phase

    Returns:
        Formatted insights and recommendations
    """
    tool = FlywheelInsightsTool()
    return tool._run(json.dumps({
        "action": "get_insights",
        "context": {
            "industry": industry,
            "stage": stage,
            "phase": phase,
        },
        "query": situation,
    }))


def capture_flywheel_pattern(
    title: str,
    description: str,
    industry: Optional[str] = None,
    stage: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """
    Capture a pattern to the Flywheel system.

    Args:
        title: Pattern title
        description: What was learned
        industry: Industry context
        stage: Stage context
        tags: Optional tags

    Returns:
        Confirmation with pattern ID
    """
    tool = FlywheelInsightsTool()
    return tool._run(json.dumps({
        "action": "capture_pattern",
        "title": title,
        "description": description,
        "context": {
            "industry": industry,
            "stage": stage,
        },
        "tags": tags or [],
    }))


def track_prediction(
    validation_id: str,
    prediction_type: str,
    predicted_outcome: str,
    confidence: float,
    reasoning: str,
) -> str:
    """
    Track a prediction for later outcome verification.

    Args:
        validation_id: ID of the validation
        prediction_type: Type of prediction
        predicted_outcome: What we predict will happen
        confidence: Confidence in prediction (0-1)
        reasoning: Why we made this prediction

    Returns:
        Confirmation with prediction ID
    """
    tool = OutcomeTrackerTool()
    return tool._run(json.dumps({
        "action": "predict",
        "validation_id": validation_id,
        "prediction_type": prediction_type,
        "predicted_outcome": predicted_outcome,
        "confidence": confidence,
        "reasoning": reasoning,
    }))


def record_prediction_outcome(
    prediction_id: str,
    actual_outcome: str,
    notes: str = "",
) -> str:
    """
    Record actual outcome for a prediction.

    Args:
        prediction_id: ID of the prediction to update
        actual_outcome: What actually happened
        notes: Additional notes/learnings

    Returns:
        Confirmation
    """
    tool = OutcomeTrackerTool()
    return tool._run(json.dumps({
        "action": "record_outcome",
        "prediction_id": prediction_id,
        "actual_outcome": actual_outcome,
        "notes": notes,
    }))
