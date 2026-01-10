"""
LLM-Based Tools for Structured Output.

These tools generate structured outputs using LLM prompts with Pydantic schemas.
They don't make external API calls - they provide structured frameworks for
agents to produce specific deliverables.

Tools:
- CanvasBuilderTool: Build VPC canvas elements (solutions, pain relievers, gain creators)
- TestCardTool: Design validation experiments using Test Card format
- LearningCardTool: Capture experiment learnings using Learning Card format

Usage:
    from shared.tools import CanvasBuilderTool, TestCardTool, LearningCardTool

    @agent
    def value_designer(self) -> Agent:
        return Agent(
            tools=[CanvasBuilderTool()],
            ...
        )
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ===========================================================================
# ENUMS
# ===========================================================================


class CanvasElementType(str, Enum):
    """Types of VPC canvas elements."""

    PRODUCT_SERVICE = "product_service"
    PAIN_RELIEVER = "pain_reliever"
    GAIN_CREATOR = "gain_creator"


class ExperimentType(str, Enum):
    """Types of validation experiments."""

    INTERVIEW = "interview"
    SURVEY = "survey"
    LANDING_PAGE = "landing_page"
    AD_CAMPAIGN = "ad_campaign"
    PROTOTYPE = "prototype"
    CONCIERGE = "concierge"
    SMOKE_TEST = "smoke_test"
    PRICING_TEST = "pricing_test"


class EvidenceType(str, Enum):
    """Types of evidence collected."""

    SAY = "say"  # What customers say (interviews, surveys)
    DO = "do"  # What customers do (behavior, actions)
    DO_DIRECT = "do_direct"  # Direct behavioral evidence
    DO_INDIRECT = "do_indirect"  # Indirect behavioral evidence


class SignalStrength(str, Enum):
    """Strength of validation signal."""

    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    INCONCLUSIVE = "inconclusive"


# ===========================================================================
# PYDANTIC MODELS - Canvas Builder
# ===========================================================================


class CanvasElement(BaseModel):
    """A single element in the Value Proposition Canvas."""

    element_type: CanvasElementType
    name: str = Field(..., description="Short name for the element")
    description: str = Field(..., description="Detailed description")
    target_job: Optional[str] = Field(None, description="Customer job this addresses")
    target_pain: Optional[str] = Field(None, description="Pain this relieves")
    target_gain: Optional[str] = Field(None, description="Gain this creates")
    priority: int = Field(1, ge=1, le=5, description="Priority 1-5 (1=highest)")
    assumptions: List[str] = Field(default_factory=list, description="Key assumptions")
    evidence_needed: List[str] = Field(
        default_factory=list, description="Evidence required to validate"
    )


class CanvasBuilderOutput(BaseModel):
    """Output from CanvasBuilderTool."""

    element_type: CanvasElementType
    elements: List[CanvasElement]
    total_elements: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    context: Optional[str] = Field(None, description="Business context used")


# ===========================================================================
# PYDANTIC MODELS - Test Card
# ===========================================================================


class TestCard(BaseModel):
    """Strategyzer Test Card format for validation experiments."""

    hypothesis: str = Field(..., description="We believe that...")
    test_description: str = Field(..., description="To verify, we will...")
    metric: str = Field(..., description="And measure...")
    success_criteria: str = Field(..., description="We are right if...")
    experiment_type: ExperimentType
    evidence_type: EvidenceType
    time_box: str = Field(..., description="Time limit for experiment (e.g., '1 week')")
    cost_estimate: Optional[str] = Field(None, description="Estimated cost")
    priority: int = Field(1, ge=1, le=5, description="Priority 1-5")
    assumptions_tested: List[str] = Field(
        default_factory=list, description="Assumptions being tested"
    )


class TestCardOutput(BaseModel):
    """Output from TestCardTool."""

    test_cards: List[TestCard]
    total_cards: int
    prioritized_order: List[int] = Field(
        default_factory=list, description="Order by priority"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ===========================================================================
# PYDANTIC MODELS - Learning Card
# ===========================================================================


class LearningCard(BaseModel):
    """Strategyzer Learning Card format for capturing experiment results."""

    hypothesis_tested: str = Field(..., description="The hypothesis we tested")
    observation: str = Field(..., description="We observed...")
    insight: str = Field(..., description="From that we learned...")
    decision: str = Field(..., description="Therefore we will...")
    signal_strength: SignalStrength
    evidence_type: EvidenceType
    sample_size: Optional[int] = Field(None, description="Number of data points")
    confidence_level: Optional[float] = Field(
        None, ge=0, le=1, description="Confidence 0-1"
    )
    quotes: List[str] = Field(
        default_factory=list, description="Supporting quotes/data"
    )
    next_experiment: Optional[str] = Field(
        None, description="Follow-up experiment if needed"
    )


class LearningCardOutput(BaseModel):
    """Output from LearningCardTool."""

    learning_cards: List[LearningCard]
    total_learnings: int
    validated_hypotheses: int
    invalidated_hypotheses: int
    inconclusive: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ===========================================================================
# CANVAS BUILDER TOOL
# ===========================================================================


class CanvasBuilderTool(BaseTool):
    """
    Build Value Proposition Canvas elements.

    Helps agents structure product/service offerings, pain relievers,
    and gain creators using the VPC framework.
    """

    name: str = "build_canvas_element"
    description: str = """
    Build Value Proposition Canvas elements (products/services, pain relievers, gain creators).

    Input: JSON with:
    - element_type: "product_service", "pain_reliever", or "gain_creator"
    - customer_jobs: List of customer jobs to address
    - customer_pains: List of customer pains to relieve
    - customer_gains: List of customer gains to create
    - business_context: Description of the business idea

    Returns structured canvas elements with priorities and assumptions.
    """

    def _run(self, input_data: str) -> str:
        """Generate canvas elements based on customer profile."""
        try:
            # Parse input
            if input_data.strip().startswith("{"):
                params = json.loads(input_data)
            else:
                # Simple string input - assume it's business context
                params = {"business_context": input_data, "element_type": "product_service"}

            element_type_str = params.get("element_type", "product_service")
            element_type = CanvasElementType(element_type_str)
            business_context = params.get("business_context", "")
            customer_jobs = params.get("customer_jobs", [])
            customer_pains = params.get("customer_pains", [])
            customer_gains = params.get("customer_gains", [])

            # Generate canvas elements based on type
            elements = self._generate_elements(
                element_type,
                business_context,
                customer_jobs,
                customer_pains,
                customer_gains,
            )

            output = CanvasBuilderOutput(
                element_type=element_type,
                elements=elements,
                total_elements=len(elements),
                context=business_context[:200] if business_context else None,
            )

            return self._format_output(output)

        except json.JSONDecodeError as e:
            return f"Error parsing input: {e}. Provide valid JSON or business context string."
        except Exception as e:
            return f"Error building canvas: {e}"

    def _generate_elements(
        self,
        element_type: CanvasElementType,
        context: str,
        jobs: List[str],
        pains: List[str],
        gains: List[str],
    ) -> List[CanvasElement]:
        """Generate canvas elements based on type and inputs."""
        elements = []

        if element_type == CanvasElementType.PRODUCT_SERVICE:
            # Generate product/service elements for each job
            for i, job in enumerate(jobs[:3]):  # Limit to top 3
                elements.append(
                    CanvasElement(
                        element_type=element_type,
                        name=f"Solution for: {job[:50]}",
                        description=f"Product/service that helps customers {job}",
                        target_job=job,
                        priority=i + 1,
                        assumptions=[
                            f"Customers prioritize {job}",
                            "Proposed solution is technically feasible",
                            "Market will pay for this solution",
                        ],
                        evidence_needed=[
                            "Customer interviews confirming job priority",
                            "Technical prototype validation",
                            "Willingness to pay test",
                        ],
                    )
                )

        elif element_type == CanvasElementType.PAIN_RELIEVER:
            # Generate pain reliever elements
            for i, pain in enumerate(pains[:3]):
                elements.append(
                    CanvasElement(
                        element_type=element_type,
                        name=f"Reliever for: {pain[:50]}",
                        description=f"Feature that reduces or eliminates {pain}",
                        target_pain=pain,
                        priority=i + 1,
                        assumptions=[
                            f"Pain '{pain[:30]}...' is significant enough to address",
                            "Proposed solution actually reduces this pain",
                            "Customers will adopt solution for pain relief",
                        ],
                        evidence_needed=[
                            "Pain severity rating from interviews",
                            "Competitive analysis of alternatives",
                            "User testing of pain reliever prototype",
                        ],
                    )
                )

        elif element_type == CanvasElementType.GAIN_CREATOR:
            # Generate gain creator elements
            for i, gain in enumerate(gains[:3]):
                elements.append(
                    CanvasElement(
                        element_type=element_type,
                        name=f"Creator for: {gain[:50]}",
                        description=f"Feature that delivers {gain}",
                        target_gain=gain,
                        priority=i + 1,
                        assumptions=[
                            f"Gain '{gain[:30]}...' is desirable",
                            "We can deliver this gain better than alternatives",
                            "Gain is worth paying for",
                        ],
                        evidence_needed=[
                            "Gain desirability score from surveys",
                            "Competitive differentiation analysis",
                            "Value proposition testing",
                        ],
                    )
                )

        # If no specific inputs, generate placeholder
        if not elements:
            elements.append(
                CanvasElement(
                    element_type=element_type,
                    name="Placeholder - needs customer profile input",
                    description="Run customer profile analysis first to generate specific elements",
                    priority=1,
                    assumptions=["Customer profile is complete"],
                    evidence_needed=["Customer interviews", "Market research"],
                )
            )

        return elements

    def _format_output(self, output: CanvasBuilderOutput) -> str:
        """Format output as markdown."""
        lines = [
            f"# Canvas Elements: {output.element_type.value.replace('_', ' ').title()}",
            "",
            f"**Generated**: {output.timestamp}",
            f"**Total Elements**: {output.total_elements}",
            "",
        ]

        if output.context:
            lines.extend(["**Context**:", f"> {output.context}", ""])

        lines.append("## Elements")
        lines.append("")
        lines.append("| Priority | Name | Target | Assumptions |")
        lines.append("|----------|------|--------|-------------|")

        for elem in output.elements:
            target = elem.target_job or elem.target_pain or elem.target_gain or "N/A"
            target_short = target[:40] + "..." if len(target) > 40 else target
            assumptions_count = len(elem.assumptions)
            lines.append(
                f"| {elem.priority} | {elem.name[:30]} | {target_short} | {assumptions_count} assumptions |"
            )

        lines.extend(["", "## Detailed Elements", ""])

        for elem in output.elements:
            lines.extend(
                [
                    f"### {elem.priority}. {elem.name}",
                    "",
                    f"**Description**: {elem.description}",
                    "",
                    "**Assumptions to Test**:",
                ]
            )
            for assumption in elem.assumptions:
                lines.append(f"- {assumption}")

            lines.extend(["", "**Evidence Needed**:"])
            for evidence in elem.evidence_needed:
                lines.append(f"- {evidence}")
            lines.append("")

        return "\n".join(lines)


# ===========================================================================
# TEST CARD TOOL
# ===========================================================================


class TestCardTool(BaseTool):
    """
    Design validation experiments using Test Card format.

    Creates structured experiment designs following Strategyzer's Test Card
    methodology for assumption testing.
    """

    name: str = "design_test_card"
    description: str = """
    Design validation experiments using Strategyzer Test Card format.

    Input: JSON with:
    - assumptions: List of assumptions to test (required)
    - experiment_type: Type of experiment (interview, survey, landing_page, etc.)
    - time_budget: Available time for experiments (e.g., "2 weeks")
    - cost_budget: Available budget (e.g., "$500")

    Returns structured Test Cards with hypotheses, metrics, and success criteria.
    """

    def _run(self, input_data: str) -> str:
        """Generate test cards for assumptions."""
        try:
            # Parse input
            if input_data.strip().startswith("{"):
                params = json.loads(input_data)
            else:
                # Simple string - treat as single assumption
                params = {"assumptions": [input_data]}

            assumptions = params.get("assumptions", [])
            experiment_type_str = params.get("experiment_type", "interview")
            time_budget = params.get("time_budget", "1 week")
            cost_budget = params.get("cost_budget", "$0")

            if not assumptions:
                return "Error: No assumptions provided. Include 'assumptions' list in input."

            # Map experiment type
            try:
                experiment_type = ExperimentType(experiment_type_str)
            except ValueError:
                experiment_type = ExperimentType.INTERVIEW

            # Generate test cards
            test_cards = self._generate_test_cards(
                assumptions, experiment_type, time_budget, cost_budget
            )

            output = TestCardOutput(
                test_cards=test_cards,
                total_cards=len(test_cards),
                prioritized_order=list(range(1, len(test_cards) + 1)),
            )

            return self._format_output(output)

        except json.JSONDecodeError as e:
            return f"Error parsing input: {e}. Provide valid JSON with 'assumptions' list."
        except Exception as e:
            return f"Error generating test cards: {e}"

    def _generate_test_cards(
        self,
        assumptions: List[str],
        experiment_type: ExperimentType,
        time_budget: str,
        cost_budget: str,
    ) -> List[TestCard]:
        """Generate test cards for each assumption."""
        cards = []

        # Map experiment types to evidence types
        evidence_map = {
            ExperimentType.INTERVIEW: EvidenceType.SAY,
            ExperimentType.SURVEY: EvidenceType.SAY,
            ExperimentType.LANDING_PAGE: EvidenceType.DO_DIRECT,
            ExperimentType.AD_CAMPAIGN: EvidenceType.DO_DIRECT,
            ExperimentType.PROTOTYPE: EvidenceType.DO,
            ExperimentType.CONCIERGE: EvidenceType.DO,
            ExperimentType.SMOKE_TEST: EvidenceType.DO_DIRECT,
            ExperimentType.PRICING_TEST: EvidenceType.DO_DIRECT,
        }

        # Test descriptions by experiment type
        test_templates = {
            ExperimentType.INTERVIEW: "conduct {n} customer discovery interviews asking about",
            ExperimentType.SURVEY: "send a survey to {n} potential customers measuring",
            ExperimentType.LANDING_PAGE: "create a landing page and drive {n} visitors to measure",
            ExperimentType.AD_CAMPAIGN: "run targeted ads to reach {n} impressions measuring",
            ExperimentType.PROTOTYPE: "build a prototype and have {n} users test",
            ExperimentType.CONCIERGE: "manually deliver the service to {n} customers measuring",
            ExperimentType.SMOKE_TEST: "create a fake door test measuring {n} click-throughs on",
            ExperimentType.PRICING_TEST: "show {n} customers different price points measuring",
        }

        for i, assumption in enumerate(assumptions[:5]):  # Limit to 5 cards
            test_template = test_templates.get(
                experiment_type, "conduct {n} tests measuring"
            )
            sample_size = 5 if experiment_type in [ExperimentType.INTERVIEW, ExperimentType.CONCIERGE] else 100

            cards.append(
                TestCard(
                    hypothesis=f"We believe that {assumption}",
                    test_description=f"To verify, we will {test_template.format(n=sample_size)} {assumption[:50]}",
                    metric=self._generate_metric(experiment_type, assumption),
                    success_criteria=self._generate_success_criteria(experiment_type),
                    experiment_type=experiment_type,
                    evidence_type=evidence_map.get(experiment_type, EvidenceType.DO),
                    time_box=time_budget,
                    cost_estimate=cost_budget,
                    priority=i + 1,
                    assumptions_tested=[assumption],
                )
            )

        return cards

    def _generate_metric(self, experiment_type: ExperimentType, assumption: str) -> str:
        """Generate appropriate metric for experiment type."""
        metrics = {
            ExperimentType.INTERVIEW: "number of interviewees who confirm the assumption without prompting",
            ExperimentType.SURVEY: "percentage of respondents who strongly agree (4-5 on Likert scale)",
            ExperimentType.LANDING_PAGE: "conversion rate (signups / visitors)",
            ExperimentType.AD_CAMPAIGN: "click-through rate and cost per click",
            ExperimentType.PROTOTYPE: "task completion rate and time on task",
            ExperimentType.CONCIERGE: "customer satisfaction score and retention",
            ExperimentType.SMOKE_TEST: "click-through rate on the feature",
            ExperimentType.PRICING_TEST: "willingness to pay at each price point",
        }
        return metrics.get(experiment_type, "success rate of the test")

    def _generate_success_criteria(self, experiment_type: ExperimentType) -> str:
        """Generate success criteria for experiment type."""
        criteria = {
            ExperimentType.INTERVIEW: "at least 4 out of 5 interviewees confirm without prompting",
            ExperimentType.SURVEY: "at least 60% strongly agree (4-5 rating)",
            ExperimentType.LANDING_PAGE: "conversion rate exceeds 3%",
            ExperimentType.AD_CAMPAIGN: "CTR exceeds 1% with CPC under $2",
            ExperimentType.PROTOTYPE: "80% task completion rate",
            ExperimentType.CONCIERGE: "NPS score above 50",
            ExperimentType.SMOKE_TEST: "at least 5% click-through rate",
            ExperimentType.PRICING_TEST: "at least 30% select the target price point",
        }
        return criteria.get(experiment_type, "majority of participants succeed")

    def _format_output(self, output: TestCardOutput) -> str:
        """Format output as markdown."""
        lines = [
            "# Test Cards",
            "",
            f"**Generated**: {output.timestamp}",
            f"**Total Cards**: {output.total_cards}",
            "",
            "## Summary",
            "",
            "| # | Hypothesis | Experiment | Time |",
            "|---|------------|------------|------|",
        ]

        for card in output.test_cards:
            hyp_short = card.hypothesis[:40] + "..." if len(card.hypothesis) > 40 else card.hypothesis
            lines.append(
                f"| {card.priority} | {hyp_short} | {card.experiment_type.value} | {card.time_box} |"
            )

        lines.extend(["", "## Detailed Test Cards", ""])

        for card in output.test_cards:
            lines.extend(
                [
                    f"### Test Card {card.priority}",
                    "",
                    f"**Hypothesis**: {card.hypothesis}",
                    "",
                    f"**Test**: {card.test_description}",
                    "",
                    f"**Metric**: {card.metric}",
                    "",
                    f"**Success Criteria**: {card.success_criteria}",
                    "",
                    f"| Experiment Type | Evidence Type | Time Box | Cost |",
                    f"|-----------------|---------------|----------|------|",
                    f"| {card.experiment_type.value} | {card.evidence_type.value} | {card.time_box} | {card.cost_estimate or 'N/A'} |",
                    "",
                ]
            )

        return "\n".join(lines)


# ===========================================================================
# LEARNING CARD TOOL
# ===========================================================================


class LearningCardTool(BaseTool):
    """
    Capture experiment learnings using Learning Card format.

    Creates structured learning documentation following Strategyzer's
    Learning Card methodology.
    """

    name: str = "capture_learning"
    description: str = """
    Capture experiment learnings using Strategyzer Learning Card format.

    Input: JSON with:
    - hypothesis: The hypothesis that was tested (required)
    - observation: What was observed during the experiment (required)
    - sample_size: Number of data points collected
    - quotes: List of supporting quotes or data points
    - signal_strength: "strong", "moderate", "weak", or "inconclusive"

    Returns structured Learning Card with insights and decisions.
    """

    def _run(self, input_data: str) -> str:
        """Generate learning card from experiment results."""
        try:
            # Parse input
            if input_data.strip().startswith("{"):
                params = json.loads(input_data)
            else:
                return "Error: Learning card requires JSON input with 'hypothesis' and 'observation'"

            hypothesis = params.get("hypothesis", "")
            observation = params.get("observation", "")
            sample_size = params.get("sample_size")
            quotes = params.get("quotes", [])
            signal_str = params.get("signal_strength", "moderate")
            evidence_str = params.get("evidence_type", "do")

            if not hypothesis or not observation:
                return "Error: Both 'hypothesis' and 'observation' are required."

            # Map signal strength
            try:
                signal_strength = SignalStrength(signal_str)
            except ValueError:
                signal_strength = SignalStrength.MODERATE

            # Map evidence type
            try:
                evidence_type = EvidenceType(evidence_str)
            except ValueError:
                evidence_type = EvidenceType.DO

            # Generate learning card
            learning_card = self._generate_learning_card(
                hypothesis,
                observation,
                signal_strength,
                evidence_type,
                sample_size,
                quotes,
            )

            output = LearningCardOutput(
                learning_cards=[learning_card],
                total_learnings=1,
                validated_hypotheses=1 if signal_strength == SignalStrength.STRONG else 0,
                invalidated_hypotheses=1 if signal_strength == SignalStrength.WEAK else 0,
                inconclusive=1 if signal_strength == SignalStrength.INCONCLUSIVE else 0,
            )

            return self._format_output(output)

        except json.JSONDecodeError as e:
            return f"Error parsing input: {e}. Provide valid JSON."
        except Exception as e:
            return f"Error generating learning card: {e}"

    def _generate_learning_card(
        self,
        hypothesis: str,
        observation: str,
        signal_strength: SignalStrength,
        evidence_type: EvidenceType,
        sample_size: Optional[int],
        quotes: List[str],
    ) -> LearningCard:
        """Generate a learning card from inputs."""
        # Generate insight based on signal strength
        insight = self._generate_insight(hypothesis, observation, signal_strength)

        # Generate decision based on signal strength
        decision = self._generate_decision(signal_strength)

        # Calculate confidence level from sample size
        confidence = None
        if sample_size:
            if sample_size >= 30:
                confidence = 0.95
            elif sample_size >= 10:
                confidence = 0.80
            elif sample_size >= 5:
                confidence = 0.60
            else:
                confidence = 0.40

        # Suggest next experiment for weak/inconclusive signals
        next_experiment = None
        if signal_strength in [SignalStrength.WEAK, SignalStrength.INCONCLUSIVE]:
            next_experiment = f"Run a different experiment type to gather more evidence for: {hypothesis[:50]}"

        return LearningCard(
            hypothesis_tested=hypothesis,
            observation=observation,
            insight=insight,
            decision=decision,
            signal_strength=signal_strength,
            evidence_type=evidence_type,
            sample_size=sample_size,
            confidence_level=confidence,
            quotes=quotes[:5],  # Limit to 5 quotes
            next_experiment=next_experiment,
        )

    def _generate_insight(
        self, hypothesis: str, observation: str, signal: SignalStrength
    ) -> str:
        """Generate insight based on signal strength."""
        if signal == SignalStrength.STRONG:
            return f"The data strongly supports the hypothesis. {observation[:100]}"
        elif signal == SignalStrength.MODERATE:
            return f"The data provides moderate support. Further validation may be needed. {observation[:80]}"
        elif signal == SignalStrength.WEAK:
            return f"The data does not support the hypothesis. Consider pivoting. {observation[:80]}"
        else:
            return f"The results are inconclusive. Need more data or different experiment design."

    def _generate_decision(self, signal: SignalStrength) -> str:
        """Generate decision recommendation based on signal."""
        decisions = {
            SignalStrength.STRONG: "Proceed with confidence. Move to next validation phase.",
            SignalStrength.MODERATE: "Proceed with caution. Gather additional evidence before major investment.",
            SignalStrength.WEAK: "Pivot required. Revisit assumptions and explore alternatives.",
            SignalStrength.INCONCLUSIVE: "Design a different experiment to get clearer signal.",
        }
        return decisions.get(signal, "Review results and determine next steps.")

    def _format_output(self, output: LearningCardOutput) -> str:
        """Format output as markdown."""
        lines = [
            "# Learning Card",
            "",
            f"**Generated**: {output.timestamp}",
            "",
            "## Summary",
            "",
            f"| Validated | Invalidated | Inconclusive |",
            f"|-----------|-------------|--------------|",
            f"| {output.validated_hypotheses} | {output.invalidated_hypotheses} | {output.inconclusive} |",
            "",
        ]

        for card in output.learning_cards:
            lines.extend(
                [
                    "---",
                    "",
                    f"### Hypothesis Tested",
                    f"> {card.hypothesis_tested}",
                    "",
                    f"### We Observed",
                    f"{card.observation}",
                    "",
                    f"### From That We Learned",
                    f"{card.insight}",
                    "",
                    f"### Therefore We Will",
                    f"**{card.decision}**",
                    "",
                    "### Evidence Quality",
                    "",
                    f"| Signal | Evidence Type | Sample Size | Confidence |",
                    f"|--------|---------------|-------------|------------|",
                    f"| {card.signal_strength.value.upper()} | {card.evidence_type.value} | {card.sample_size or 'N/A'} | {f'{card.confidence_level:.0%}' if card.confidence_level else 'N/A'} |",
                    "",
                ]
            )

            if card.quotes:
                lines.extend(["### Supporting Evidence", ""])
                for quote in card.quotes:
                    lines.append(f'> "{quote}"')
                lines.append("")

            if card.next_experiment:
                lines.extend(
                    [
                        "### Recommended Next Experiment",
                        f"{card.next_experiment}",
                        "",
                    ]
                )

        return "\n".join(lines)


# ===========================================================================
# CONVENIENCE FUNCTIONS
# ===========================================================================


def build_canvas_element(
    element_type: str,
    customer_jobs: Optional[List[str]] = None,
    customer_pains: Optional[List[str]] = None,
    customer_gains: Optional[List[str]] = None,
    business_context: Optional[str] = None,
) -> str:
    """Build VPC canvas elements."""
    tool = CanvasBuilderTool()
    input_data = json.dumps(
        {
            "element_type": element_type,
            "customer_jobs": customer_jobs or [],
            "customer_pains": customer_pains or [],
            "customer_gains": customer_gains or [],
            "business_context": business_context or "",
        }
    )
    return tool._run(input_data)


def design_test_card(
    assumptions: List[str],
    experiment_type: str = "interview",
    time_budget: str = "1 week",
    cost_budget: str = "$0",
) -> str:
    """Design validation experiments."""
    tool = TestCardTool()
    input_data = json.dumps(
        {
            "assumptions": assumptions,
            "experiment_type": experiment_type,
            "time_budget": time_budget,
            "cost_budget": cost_budget,
        }
    )
    return tool._run(input_data)


def capture_learning(
    hypothesis: str,
    observation: str,
    signal_strength: str = "moderate",
    sample_size: Optional[int] = None,
    quotes: Optional[List[str]] = None,
) -> str:
    """Capture experiment learnings."""
    tool = LearningCardTool()
    input_data = json.dumps(
        {
            "hypothesis": hypothesis,
            "observation": observation,
            "signal_strength": signal_strength,
            "sample_size": sample_size,
            "quotes": quotes or [],
        }
    )
    return tool._run(input_data)
