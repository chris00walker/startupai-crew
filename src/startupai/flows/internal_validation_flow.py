"""
Internal Validation Flow with Innovation Physics Logic.

This flow implements the specific decision trees from Strategyzer methodologies,
enforcing non-linear iteration based on evidence signals.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import traceback
from crewai.flow.flow import Flow, start, listen, router
from crewai import Crew

# Import error handling
from startupai.models.tool_contracts import FlowExecutionError

from startupai.flows.state_schemas import (
    # Main state class (aliased for compatibility)
    ValidationState,  # Alias for StartupValidationState
    StartupValidationState,
    # Phase enums
    Phase,
    ValidationPhase,  # Alias for Phase
    RiskAxis,
    # Signal enums
    DesirabilitySignal,
    FeasibilitySignal,
    ViabilitySignal,
    ProblemFit,
    # Legacy aliases (for existing code)
    EvidenceStrength,
    CommitmentType,
    FeasibilityStatus,  # Alias for FeasibilitySignal
    UnitEconomicsStatus,  # Alias for ViabilitySignal
    # Pivot types
    PivotType,
    PivotRecommendation,  # Alias for PivotType
    # HITL
    HumanApprovalStatus,
    # Flow control
    RouterDecision,
    QAStatus,
)

# Import crews (these will be created separately)
from startupai.crews.service.service_crew import ServiceCrew
from startupai.crews.analysis.analysis_crew import AnalysisCrew
from startupai.crews.governance.governance_crew import GovernanceCrew
from startupai.crews.build.build_crew import BuildCrew
from startupai.crews.growth.growth_crew import GrowthCrew
from startupai.crews.synthesis.synthesis_crew import SynthesisCrew
from startupai.crews.finance.finance_crew import FinanceCrew


class InternalValidationFlow(Flow[ValidationState]):
    """
    The master flow orchestrating 8 crews through the Innovation Physics logic.

    Key Innovation Physics Rules:
    1. Desirability: Problem-Solution Filter and Product-Market Filter
    2. Feasibility: Downgrade Protocol (can't build = re-test desirability)
    3. Viability: Unit Economics Trigger (CAC > LTV = strategic pivot)
    """

    # ===========================================================================
    # PHASE 1: INTAKE & INITIAL ANALYSIS
    # ===========================================================================

    @start()
    def intake_entrepreneur_input(self):
        """
        Entry point: Capture entrepreneur's business idea and context.
        This is Sage's Service Crew collecting the initial brief.
        """
        print("\n🚀 Starting Internal Validation Flow")
        print(f"Phase: {self.state.phase}")

        try:
            # Service Crew captures the entrepreneur input
            result = ServiceCrew().crew().kickoff(
                inputs={"entrepreneur_input": self.state.entrepreneur_input}
            )

            # Parse the brief from Service Crew
            if result and hasattr(result, 'pydantic') and result.pydantic:
                self.state.business_idea = getattr(result.pydantic, 'business_idea', self.state.entrepreneur_input)
                self.state.target_segments = getattr(result.pydantic, 'target_segments', [])
                self.state.assumptions = getattr(result.pydantic, 'assumptions', [])
            else:
                # Fallback: use raw output
                self.state.business_idea = self.state.entrepreneur_input
                self.state.target_segments = ["General Market"]
                self.state.guardian_last_issues.append("Service Crew returned no structured output - using defaults")

            self.state.phase = Phase.DESIRABILITY
            self.state.current_segment = self.state.target_segments[0] if self.state.target_segments else None

            print(f"✅ Intake complete. Target segments: {self.state.target_segments}")

        except Exception as e:
            error_msg = f"Intake failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")

            # Log traceback for debugging
            print(traceback.format_exc())

            # Set minimal state to allow flow to continue with degraded data
            self.state.business_idea = self.state.entrepreneur_input or "Unknown business idea"
            self.state.target_segments = ["General Market"]
            self.state.phase = Phase.DESIRABILITY

            raise FlowExecutionError(
                error_msg,
                error_code="INTAKE_ERROR",
                phase="intake",
                crew="service",
                recoverable=True,
                context={"entrepreneur_input": self.state.entrepreneur_input}
            )

    @listen(intake_entrepreneur_input)
    def analyze_customer_segments(self):
        """
        Sage's Analysis Crew: Deep dive into customer Jobs, Pains, Gains.
        This creates the initial Value Proposition Canvas.
        """
        print("\n🔍 Analyzing customer segments...")

        try:
            # Analyze each target segment
            for segment in self.state.target_segments:
                try:
                    result = AnalysisCrew().crew().kickoff(
                        inputs={
                            "segment": segment,
                            "business_idea": self.state.business_idea,
                            "assumptions": [a.dict() for a in self.state.assumptions]
                        }
                    )

                    # Store customer profile and value map
                    if result and hasattr(result, 'pydantic') and result.pydantic:
                        self.state.customer_profiles[segment] = result.pydantic.customer_profile
                        self.state.value_maps[segment] = result.pydantic.value_map
                    else:
                        self.state.guardian_last_issues.append(f"Analysis Crew returned no structured output for segment: {segment}")
                except Exception as segment_error:
                    error_msg = f"Analysis failed for segment {segment}: {str(segment_error)}"
                    self.state.guardian_last_issues.append(error_msg)
                    print(f"⚠️ {error_msg}")

            # Competitive analysis
            try:
                comp_result = AnalysisCrew().crew().kickoff(
                    inputs={
                        "task": "competitor_analysis",
                        "business_idea": self.state.business_idea,
                        "segments": self.state.target_segments
                    }
                )
                if comp_result and hasattr(comp_result, 'pydantic') and comp_result.pydantic:
                    self.state.competitor_report = comp_result.pydantic
                else:
                    self.state.guardian_last_issues.append("Competitor analysis returned no structured output")
            except Exception as comp_error:
                error_msg = f"Competitor analysis failed: {str(comp_error)}"
                self.state.guardian_last_issues.append(error_msg)
                print(f"⚠️ {error_msg}")

            print(f"✅ Analysis complete for {len(self.state.target_segments)} segments")

        except Exception as e:
            error_msg = f"Customer segment analysis failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            raise FlowExecutionError(
                error_msg,
                error_code="ANALYSIS_ERROR",
                phase="desirability",
                crew="analysis",
                recoverable=True,
                context={"segments": self.state.target_segments}
            )

    # ===========================================================================
    # PHASE 1 LOGIC: DESIRABILITY (The "Truth" Engine)
    # ===========================================================================

    @listen(analyze_customer_segments)
    def test_desirability(self):
        """
        Pulse's Growth Crew: Run experiments to test desirability assumptions.
        This is where we discover if customers actually care.
        """
        print("\n🧪 Testing desirability assumptions...")

        try:
            # Growth Crew runs desirability experiments
            result = GrowthCrew().crew().kickoff(
                inputs={
                    "customer_profiles": {k: v.dict() for k, v in self.state.customer_profiles.items()},
                    "value_maps": {k: v.dict() for k, v in self.state.value_maps.items()},
                    "assumptions": [a.dict() for a in self.state.get_critical_assumptions()],
                    "competitor_analysis": self.state.competitor_report.dict() if self.state.competitor_report else None
                }
            )

            # Store desirability evidence
            if result and hasattr(result, 'pydantic') and result.pydantic:
                self.state.desirability_evidence = result.pydantic
            else:
                self.state.guardian_last_issues.append("Growth Crew returned no structured output for desirability testing")

            # Calculate key signals for routing
            self._calculate_desirability_signals()

            print(f"✅ Desirability testing complete")
            if self.state.desirability_evidence:
                print(f"   Problem resonance: {self.state.desirability_evidence.problem_resonance:.1%}")
                print(f"   Commitment type: {self.state.commitment_type}")
                print(f"   Zombie ratio: {self.state.calculate_zombie_ratio():.1%}")

        except Exception as e:
            error_msg = f"Desirability testing failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            raise FlowExecutionError(
                error_msg,
                error_code="DESIRABILITY_TEST_ERROR",
                phase="desirability",
                crew="growth",
                recoverable=True,
                context={"segments": self.state.target_segments}
            )

    def _calculate_desirability_signals(self):
        """Calculate the Innovation Physics signals from desirability evidence"""
        evidence = self.state.desirability_evidence

        # Evidence strength based on problem resonance and conversion
        if evidence.problem_resonance > 0.6 and evidence.conversion_rate > 0.1:
            self.state.evidence_strength = EvidenceStrength.STRONG
        elif evidence.problem_resonance > 0.3 and evidence.conversion_rate > 0.05:
            self.state.evidence_strength = EvidenceStrength.WEAK
        else:
            self.state.evidence_strength = EvidenceStrength.NONE

        # Commitment type from evidence
        self.state.commitment_type = evidence.commitment_depth

        # Update timestamp
        # Timestamp tracked via persistence layer

    @router(test_desirability)
    def desirability_gate(self) -> str:
        """
        INNOVATION PHYSICS - Phase 1 Router

        The Problem-Solution Filter:
        - If customer_interest is "Low" → Route back to Sage with "Pivot Customer Segment"

        The Product-Market Filter:
        - If traffic "High" but commitment "Low" → Route back to Analysis with "Iterate Value Proposition"
        """
        print("\n🚦 Desirability Gate - Evaluating evidence...")

        evidence = self.state.desirability_evidence
        zombie_ratio = self.state.calculate_zombie_ratio()

        # PROBLEM-SOLUTION FILTER
        if evidence.problem_resonance < 0.3:  # Low interest in the problem
            print("❌ Problem-Solution Filter FAILED: Low problem resonance")
            print("   → Routing back to Sage: 'Pivot Customer Segment'")
            self.state.pivot_recommendation = PivotRecommendation.SEGMENT_PIVOT
            self.state.human_input_required = True
            self.state.human_input_reason = "Customer segment shows low interest in the problem. Should we pivot to a different segment?"
            return "segment_pivot_required"

        # PRODUCT-MARKET FILTER
        elif evidence.traffic_quality == "High" and zombie_ratio < 0.1:  # High traffic, low commitment
            print("❌ Product-Market Filter FAILED: High traffic but low commitment (Zombie detected)")
            print("   → Routing back to Analysis: 'Iterate Value Proposition'")
            self.state.pivot_recommendation = PivotRecommendation.VALUE_PIVOT
            self.state.human_input_required = True
            self.state.human_input_reason = "High interest but low commitment detected. Should we iterate the value proposition?"
            return "value_pivot_required"

        # WEAK SIGNAL - Need more evidence
        elif self.state.evidence_strength == EvidenceStrength.WEAK:
            print("⚠️ Weak desirability signal - need more testing")
            if self.state.retry_count < self.state.max_retries:
                self.state.retry_count += 1
                return "refine_and_retest_desirability"
            else:
                print("   → Max retries reached, escalating to Compass")
                return "compass_synthesis_required"

        # STRONG SIGNAL - Proceed to feasibility
        elif self.state.evidence_strength == EvidenceStrength.STRONG:
            print("✅ Desirability VALIDATED - Strong signal with commitment")
            self.state.phase = Phase.FEASIBILITY
            self.state.retry_count = 0  # Reset for next phase
            return "proceed_to_feasibility"

        # NO SIGNAL - Major pivot needed
        else:
            print("❌ No desirability signal - fundamental pivot required")
            return "compass_synthesis_required"

    # ===========================================================================
    # DESIRABILITY PIVOT HANDLERS
    # ===========================================================================

    @listen("segment_pivot_required")
    def pivot_customer_segment(self):
        """
        Innovation Physics: Don't change the solution; change the audience.
        Route back to Sage (Service Crew) to identify new segment.
        """
        if self.state.human_input_required:
            # In production, this would trigger a human approval workflow
            print("\n🤔 HUMAN INPUT REQUIRED")
            print(f"   Reason: {self.state.human_input_reason}")
            print("   Waiting for strategic decision on customer segment pivot...")

            # Simulate human decision (in production, this would be async)
            human_decision = self._get_human_input_segment_pivot()

            if not human_decision.get("approved"):
                self.state.pivot_recommendation = PivotRecommendation.KILL
                return

        print("\n🔄 Pivoting Customer Segment...")

        # Sage identifies new segment to target
        result = ServiceCrew().crew().kickoff(
            inputs={
                "task": "segment_pivot",
                "current_segment": self.state.target_segments[0],
                "evidence": self.state.desirability_evidence.dict(),
                "business_idea": self.state.business_idea
            }
        )

        # Update state with new segment
        new_segment = result.pydantic.new_segment
        self.state.target_segments = [new_segment]
        self.state.add_pivot_to_history(
            PivotRecommendation.SEGMENT_PIVOT,
            f"Low problem resonance ({self.state.desirability_evidence.problem_resonance:.1%})"
        )

        # Reset and reanalyze
        self.state.customer_profiles = {}
        self.state.value_maps = {}
        self.state.desirability_evidence = None

        print(f"✅ Pivoted to new segment: {new_segment}")
        # Re-run analysis for new segment
        self.analyze_customer_segments()

    @listen("value_pivot_required")
    def pivot_value_proposition(self):
        """
        Innovation Physics: The audience is right, but the promise is wrong.
        Route back to Analysis Crew to iterate value proposition.
        """
        if self.state.human_input_required:
            print("\n🤔 HUMAN INPUT REQUIRED")
            print(f"   Reason: {self.state.human_input_reason}")
            print("   Waiting for strategic decision on value proposition iteration...")

            human_decision = self._get_human_input_value_pivot()

            if not human_decision.get("approved"):
                self.state.pivot_recommendation = PivotRecommendation.KILL
                return

        print("\n🔄 Iterating Value Proposition...")

        # Analysis Crew redesigns value proposition
        result = AnalysisCrew().crew().kickoff(
            inputs={
                "task": "value_iteration",
                "current_value_map": self.state.value_maps[self.state.target_segments[0]].dict(),
                "customer_profile": self.state.customer_profiles[self.state.target_segments[0]].dict(),
                "evidence": self.state.desirability_evidence.dict(),
                "zombie_ratio": self.state.calculate_zombie_ratio()
            }
        )

        # Update value proposition
        self.state.value_maps[self.state.target_segments[0]] = result.pydantic.new_value_map
        self.state.add_pivot_to_history(
            PivotRecommendation.VALUE_PIVOT,
            f"High traffic but low commitment (zombie ratio: {self.state.calculate_zombie_ratio():.1%})"
        )

        # Reset evidence and retest
        self.state.desirability_evidence = None

        print("✅ Value proposition updated, retesting desirability...")
        self.test_desirability()

    @listen("refine_and_retest_desirability")
    def refine_desirability_tests(self):
        """Refine experiments and retest with better targeting"""
        print(f"\n🔧 Refining desirability tests (attempt {self.state.retry_count}/{self.state.max_retries})...")

        try:
            # Growth Crew refines and retests
            result = GrowthCrew().crew().kickoff(
                inputs={
                    "task": "refine_experiments",
                    "previous_evidence": self.state.desirability_evidence.dict() if self.state.desirability_evidence else {},
                    "customer_profiles": {k: v.dict() for k, v in self.state.customer_profiles.items()},
                    "value_maps": {k: v.dict() for k, v in self.state.value_maps.items()}
                }
            )

            # Update evidence
            if result and hasattr(result, 'pydantic') and result.pydantic:
                self.state.desirability_evidence = result.pydantic
            else:
                self.state.guardian_last_issues.append("Growth Crew returned no structured output for refined testing")

            self._calculate_desirability_signals()

            print("✅ Refined testing complete, re-evaluating...")

        except Exception as e:
            error_msg = f"Refining desirability tests failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

    # ===========================================================================
    # PHASE 2 LOGIC: FEASIBILITY (The "Reality" Check)
    # ===========================================================================

    @listen("proceed_to_feasibility")
    def test_feasibility(self):
        """
        Forge's Build Crew: Test if we can actually build what we're promising.
        This is where dreams meet engineering reality.
        """
        print("\n🔨 Testing feasibility of validated value proposition...")

        try:
            # Build Crew assesses feasibility
            result = BuildCrew().crew().kickoff(
                inputs={
                    "value_maps": {k: v.dict() for k, v in self.state.value_maps.items()},
                    "desirability_evidence": self.state.desirability_evidence.dict() if self.state.desirability_evidence else {},
                    "technical_requirements": self._extract_technical_requirements()
                }
            )

            # Store feasibility evidence
            if result and hasattr(result, 'pydantic') and result.pydantic:
                self.state.feasibility_evidence = result.pydantic
            else:
                self.state.guardian_last_issues.append("Build Crew returned no structured output for feasibility testing")

            # Calculate feasibility status
            self._calculate_feasibility_signals()

            print(f"✅ Feasibility assessment complete")
            print(f"   Status: {self.state.feasibility_status}")
            if self.state.feasibility_evidence and self.state.feasibility_evidence.downgrade_required:
                print(f"   ⚠️ Downgrade required: {self.state.feasibility_evidence.downgrade_impact}")

        except Exception as e:
            error_msg = f"Feasibility testing failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            raise FlowExecutionError(
                error_msg,
                error_code="FEASIBILITY_TEST_ERROR",
                phase="feasibility",
                crew="build",
                recoverable=True,
                context={"value_maps": list(self.state.value_maps.keys())}
            )

    def _extract_technical_requirements(self) -> Dict[str, Any]:
        """Extract technical requirements from value propositions"""
        requirements = []
        for segment, value_map in self.state.value_maps.items():
            for service in value_map.products_services:
                requirements.append({
                    "service": service,
                    "segment": segment,
                    "critical": True  # Assume all are critical initially
                })
        return {"requirements": requirements}

    def _calculate_feasibility_signals(self):
        """Calculate the Innovation Physics signals from feasibility evidence"""
        evidence = self.state.feasibility_evidence

        # Check if any core features are impossible
        impossible_count = sum(
            1 for status in evidence.core_features_feasible.values()
            if status == FeasibilityStatus.IMPOSSIBLE
        )

        if impossible_count > 0:
            self.state.feasibility_status = FeasibilityStatus.IMPOSSIBLE
        elif evidence.downgrade_required:
            self.state.feasibility_status = FeasibilityStatus.CONSTRAINED
        else:
            self.state.feasibility_status = FeasibilityStatus.POSSIBLE

        # Timestamp tracked via persistence layer

    @router(test_feasibility)
    def feasibility_gate(self) -> str:
        """
        INNOVATION PHYSICS - Phase 2 Router

        The Downgrade Protocol:
        - If feature is "Technically Impossible" → Route to Pulse to Re-Test Desirability
        - We must verify if customers still want the product without that feature
        """
        print("\n🚦 Feasibility Gate - Evaluating technical reality...")

        # DOWNGRADE PROTOCOL - CRITICAL LOGIC
        if self.state.feasibility_status == FeasibilityStatus.IMPOSSIBLE:
            print("❌ DOWNGRADE PROTOCOL TRIGGERED: Core feature technically impossible")
            print("   → Must route back to Pulse (Growth Crew) to re-test desirability")
            print("   → Customers must validate the downgraded value proposition")

            self.state.human_input_required = True
            self.state.human_input_reason = (
                f"Core features are technically impossible: "
                f"{', '.join([k for k, v in self.state.feasibility_evidence.core_features_feasible.items() if v == FeasibilityStatus.IMPOSSIBLE])}. "
                "Should we test a downgraded value proposition?"
            )
            return "downgrade_and_retest"

        # CONSTRAINED BUT POSSIBLE
        elif self.state.feasibility_status == FeasibilityStatus.CONSTRAINED:
            print("⚠️ Feasibility constrained - can build degraded version")
            print("   → Testing if degraded version maintains desirability")
            return "test_degraded_desirability"

        # FULLY FEASIBLE
        elif self.state.feasibility_status == FeasibilityStatus.POSSIBLE:
            print("✅ Feasibility VALIDATED - Can build as promised")
            self.state.phase = Phase.VIABILITY
            self.state.retry_count = 0
            return "proceed_to_viability"

        else:
            print("❓ Unexpected feasibility state, requesting synthesis")
            return "compass_synthesis_required"

    @listen("downgrade_and_retest")
    def downgrade_value_proposition(self):
        """
        Innovation Physics: Can't build it, so downgrade the promise.
        Must verify customers still want the degraded version.
        """
        if self.state.human_input_required:
            print("\n🤔 HUMAN INPUT REQUIRED")
            print(f"   Reason: {self.state.human_input_reason}")

            human_decision = self._get_human_input_downgrade()

            if not human_decision.get("approved"):
                self.state.pivot_recommendation = PivotRecommendation.KILL
                return

        print("\n📉 Downgrading value proposition based on feasibility constraints...")

        # Forge designs the downgraded offering
        downgrade_result = BuildCrew().crew().kickoff(
            inputs={
                "task": "design_downgrade",
                "current_value_maps": {k: v.dict() for k, v in self.state.value_maps.items()},
                "feasibility_evidence": self.state.feasibility_evidence.dict(),
                "impossible_features": [
                    k for k, v in self.state.feasibility_evidence.core_features_feasible.items()
                    if v == FeasibilityStatus.IMPOSSIBLE
                ]
            }
        )

        # Update value maps with downgraded version
        for segment in self.state.target_segments:
            self.state.value_maps[segment] = downgrade_result.pydantic.downgraded_value_maps[segment]

        self.state.add_pivot_to_history(
            PivotRecommendation.FEATURE_PIVOT,
            f"Technical impossibility forced downgrade: {self.state.feasibility_evidence.downgrade_impact}"
        )

        print("✅ Value proposition downgraded, now re-testing desirability...")

        # CRITICAL: Route back to Pulse to re-test desirability
        self.state.phase = Phase.DESIRABILITY
        self.state.desirability_evidence = None  # Reset evidence
        self.test_desirability()

    @listen("test_degraded_desirability")
    def test_degraded_version(self):
        """Test if customers accept the degraded but feasible version"""
        print("\n🧪 Testing desirability of degraded version...")

        # Pulse tests the degraded value proposition
        result = GrowthCrew().crew().kickoff(
            inputs={
                "task": "test_degraded",
                "original_value_maps": {k: v.dict() for k, v in self.state.value_maps.items()},
                "degradation_impact": self.state.feasibility_evidence.downgrade_impact,
                "customer_profiles": {k: v.dict() for k, v in self.state.customer_profiles.items()}
            }
        )

        # Compare acceptance of degraded version
        degraded_acceptance = result.pydantic.acceptance_rate

        if degraded_acceptance > 0.6:  # 60% still want it
            print(f"✅ Degraded version accepted ({degraded_acceptance:.1%} acceptance)")
            self.state.phase = Phase.VIABILITY
            return "proceed_to_viability"
        else:
            print(f"❌ Degraded version rejected ({degraded_acceptance:.1%} acceptance)")
            return "compass_synthesis_required"

    # ===========================================================================
    # PHASE 3 LOGIC: VIABILITY (The "Survival" Equation)
    # ===========================================================================

    @listen("proceed_to_viability")
    def test_viability(self):
        """
        Ledger's Finance Crew: Calculate if we can make money.
        This is where unit economics determine survival.
        """
        print("\n💰 Testing viability and unit economics...")

        try:
            # Finance Crew analyzes viability
            result = FinanceCrew().crew().kickoff(
                inputs={
                    "value_maps": {k: v.dict() for k, v in self.state.value_maps.items()},
                    "desirability_evidence": self.state.desirability_evidence.dict() if self.state.desirability_evidence else {},
                    "feasibility_evidence": self.state.feasibility_evidence.dict() if self.state.feasibility_evidence else {},
                    "market_size": self._estimate_market_size()
                }
            )

            # Store viability evidence
            if result and hasattr(result, 'pydantic') and result.pydantic:
                self.state.viability_evidence = result.pydantic
            else:
                self.state.guardian_last_issues.append("Finance Crew returned no structured output for viability testing")

            # Calculate viability signals
            self._calculate_viability_signals()

            print(f"✅ Viability assessment complete")
            if self.state.viability_evidence:
                print(f"   CAC: ${self.state.viability_evidence.cac:.2f}")
                print(f"   LTV: ${self.state.viability_evidence.ltv:.2f}")
                print(f"   LTV/CAC: {self.state.viability_evidence.ltv_cac_ratio:.1f}")
                print(f"   Status: {self.state.unit_economics_status}")

        except Exception as e:
            error_msg = f"Viability testing failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            raise FlowExecutionError(
                error_msg,
                error_code="VIABILITY_TEST_ERROR",
                phase="viability",
                crew="finance",
                recoverable=True,
                context={"segments": self.state.target_segments}
            )

    def _estimate_market_size(self) -> Dict[str, Any]:
        """Estimate market size from segments and evidence"""
        return {
            "segments": self.state.target_segments,
            "conversion_rate": self.state.desirability_evidence.conversion_rate,
            "problem_resonance": self.state.desirability_evidence.problem_resonance
        }

    def _calculate_viability_signals(self):
        """Calculate the Innovation Physics signals from viability evidence"""
        evidence = self.state.viability_evidence

        # Unit economics status based on LTV/CAC ratio
        if evidence.ltv_cac_ratio and evidence.ltv_cac_ratio > 3:
            self.state.unit_economics_status = UnitEconomicsStatus.PROFITABLE
        elif evidence.ltv_cac_ratio and evidence.ltv_cac_ratio > 1:
            self.state.unit_economics_status = UnitEconomicsStatus.MARGINAL
        else:
            self.state.unit_economics_status = UnitEconomicsStatus.UNDERWATER

        # Timestamp tracked via persistence layer

    @router(test_viability)
    def viability_gate(self) -> str:
        """
        INNOVATION PHYSICS - Phase 3 Router

        The Unit Economics Trigger:
        - If CAC > LTV → Route to Compass for Strategic Pivot Decision
        - Two paths: Increase Price (test willingness) OR Reduce Cost (reduce features)
        """
        print("\n🚦 Viability Gate - Evaluating unit economics...")

        # UNIT ECONOMICS TRIGGER
        if self.state.unit_economics_status == UnitEconomicsStatus.UNDERWATER:
            print(f"❌ UNIT ECONOMICS FAILURE: CAC > LTV ({self.state.viability_evidence.ltv_cac_ratio:.1f})")
            print("   → Routing to Compass for strategic pivot decision")
            print("   → Options: 1) Increase Price, 2) Reduce Cost")

            self.state.human_input_required = True
            self.state.human_input_reason = (
                f"Unit economics underwater (LTV/CAC = {self.state.viability_evidence.ltv_cac_ratio:.1f}). "
                "Strategic decision needed: increase price or reduce costs?"
            )
            return "strategic_pivot_required"

        # MARGINAL ECONOMICS
        elif self.state.unit_economics_status == UnitEconomicsStatus.MARGINAL:
            print("⚠️ Marginal unit economics - optimization needed")
            if self.state.retry_count < 2:  # Allow 2 optimization attempts
                self.state.retry_count += 1
                return "optimize_economics"
            else:
                return "compass_synthesis_required"

        # PROFITABLE
        elif self.state.unit_economics_status == UnitEconomicsStatus.PROFITABLE:
            print("✅ Viability VALIDATED - Unit economics profitable")
            self.state.phase = Phase.VALIDATED
            return "validation_complete"

        else:
            return "compass_synthesis_required"

    @listen("strategic_pivot_required")
    def execute_strategic_pivot(self):
        """
        Innovation Physics: CAC > LTV requires fundamental model change.
        Compass synthesizes evidence and recommends pivot path.
        """
        print("\n🧭 Compass synthesizing evidence for strategic pivot...")

        # Compass analyzes all evidence and recommends pivot
        result = SynthesisCrew().crew().kickoff(
            inputs={
                "task": "strategic_pivot",
                "desirability_evidence": self.state.desirability_evidence.dict(),
                "feasibility_evidence": self.state.feasibility_evidence.dict(),
                "viability_evidence": self.state.viability_evidence.dict(),
                "pivot_history": self.state.pivot_history,
                "current_cac": self.state.viability_evidence.cac,
                "current_ltv": self.state.viability_evidence.ltv
            }
        )

        pivot_decision = result.pydantic.pivot_decision

        if self.state.human_input_required:
            print("\n🤔 HUMAN INPUT REQUIRED")
            print(f"   Reason: {self.state.human_input_reason}")
            print(f"   Compass recommends: {pivot_decision.pivot_type}")
            print(f"   Specific changes: {', '.join(pivot_decision.specific_changes)}")

            human_decision = self._get_human_input_strategic_pivot(pivot_decision)

            if not human_decision.get("approved"):
                self.state.pivot_recommendation = PivotRecommendation.KILL
                return

            # Override with human choice if provided
            if human_decision.get("chosen_path"):
                pivot_decision.pivot_type = human_decision["chosen_path"]

        # Execute the chosen pivot path
        if pivot_decision.pivot_type == "increase_price":
            print("\n📈 Pivoting to increase price...")
            self._pivot_increase_price()
        elif pivot_decision.pivot_type == "reduce_cost":
            print("\n📉 Pivoting to reduce costs...")
            self._pivot_reduce_costs()
        else:
            print(f"\n🔄 Executing {pivot_decision.pivot_type} pivot...")
            self.state.pivot_recommendation = pivot_decision.pivot_type
            return "compass_synthesis_required"

    def _pivot_increase_price(self):
        """
        Route to Pulse to re-test Willingness-to-Pay at higher price point.
        """
        print("   → Routing to Pulse to test higher price point")

        # Calculate new price point (e.g., 50% increase)
        new_price_multiplier = 1.5

        # Pulse tests willingness to pay at higher price
        result = GrowthCrew().crew().kickoff(
            inputs={
                "task": "test_pricing",
                "current_price": self.state.viability_evidence.ltv / 12,  # Monthly price
                "new_price_multiplier": new_price_multiplier,
                "customer_profiles": {k: v.dict() for k, v in self.state.customer_profiles.items()},
                "value_maps": {k: v.dict() for k, v in self.state.value_maps.items()}
            }
        )

        # Update viability evidence with new pricing
        if result.pydantic.acceptance_rate > 0.5:  # 50% accept higher price
            print(f"✅ Higher price accepted ({result.pydantic.acceptance_rate:.1%})")
            self.state.viability_evidence.ltv *= new_price_multiplier
            self.state.viability_evidence.ltv_cac_ratio = (
                self.state.viability_evidence.ltv / self.state.viability_evidence.cac
            )
            self._calculate_viability_signals()
        else:
            print(f"❌ Higher price rejected ({result.pydantic.acceptance_rate:.1%})")
            self.state.pivot_recommendation = PivotRecommendation.MODEL_PIVOT

    def _pivot_reduce_costs(self):
        """
        Route to Forge to reduce Feature Scope and lower costs.
        """
        print("   → Routing to Forge to reduce feature scope")

        # Forge identifies features to cut
        result = BuildCrew().crew().kickoff(
            inputs={
                "task": "reduce_scope",
                "current_features": list(self.state.feasibility_evidence.core_features_feasible.keys()),
                "cost_reduction_target": 0.4,  # 40% cost reduction target
                "value_maps": {k: v.dict() for k, v in self.state.value_maps.items()}
            }
        )

        # Update cost structure
        reduced_features = result.pydantic.features_to_remove
        new_cac = self.state.viability_evidence.cac * 0.6  # 40% reduction

        print(f"   Features to remove: {', '.join(reduced_features)}")
        print(f"   New CAC: ${new_cac:.2f} (was ${self.state.viability_evidence.cac:.2f})")

        # Update viability metrics
        self.state.viability_evidence.cac = new_cac
        self.state.viability_evidence.ltv_cac_ratio = (
            self.state.viability_evidence.ltv / new_cac
        )
        self._calculate_viability_signals()

    @listen("optimize_economics")
    def optimize_unit_economics(self):
        """Attempt to optimize marginal unit economics"""
        print(f"\n🔧 Optimizing unit economics (attempt {self.state.retry_count}/2)...")

        try:
            # Finance Crew optimizes
            result = FinanceCrew().crew().kickoff(
                inputs={
                    "task": "optimize",
                    "current_cac": self.state.viability_evidence.cac if self.state.viability_evidence else 0,
                    "current_ltv": self.state.viability_evidence.ltv if self.state.viability_evidence else 0,
                    "current_margin": self.state.viability_evidence.gross_margin if self.state.viability_evidence else 0
                }
            )

            # Apply optimizations
            if result and hasattr(result, 'pydantic') and result.pydantic:
                self.state.viability_evidence = result.pydantic.optimized_metrics
            else:
                self.state.guardian_last_issues.append("Finance Crew returned no structured output for optimization")

            self._calculate_viability_signals()

            if self.state.viability_evidence:
                print(f"   New LTV/CAC: {self.state.viability_evidence.ltv_cac_ratio:.1f}")

        except Exception as e:
            error_msg = f"Unit economics optimization failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

    # ===========================================================================
    # SYNTHESIS & COMPLETION
    # ===========================================================================

    @listen("compass_synthesis_required")
    def compass_synthesis(self):
        """
        Compass (CPO) synthesizes all evidence and makes final recommendation.
        This is called when standard paths fail or complex decisions are needed.
        """
        print("\n🧭 Compass synthesizing all evidence for final recommendation...")

        try:
            # Compass performs comprehensive synthesis
            result = SynthesisCrew().crew().kickoff(
                inputs={
                    "task": "final_synthesis",
                    "full_state": self.state.dict(),
                    "phase": self.state.phase.value,
                    "pivot_history": self.state.pivot_history
                }
            )

            # Extract recommendation
            if result and hasattr(result, 'pydantic') and result.pydantic:
                synthesis = result.pydantic
                self.state.final_recommendation = synthesis.recommendation
                self.state.evidence_summary = synthesis.evidence_summary
                self.state.next_steps = synthesis.next_steps
                self.state.pivot_recommendation = synthesis.pivot_recommendation
            else:
                self.state.guardian_last_issues.append("Synthesis Crew returned no structured output")
                self.state.phase = Phase.VALIDATED
                return

            print(f"\n📊 COMPASS SYNTHESIS COMPLETE")
            print(f"   Recommendation: {self.state.final_recommendation}")
            print(f"   Pivot Type: {self.state.pivot_recommendation}")
            print(f"   Next Steps: {len(self.state.next_steps)} actions identified")

            # Handle the recommendation
            if self.state.pivot_recommendation == PivotRecommendation.KILL:
                print("\n☠️ PROJECT TERMINATED - No viable path forward")
                self.state.phase = Phase.VALIDATED
                return
            elif self.state.pivot_recommendation != PivotRecommendation.NO_PIVOT:
                print(f"\n🔄 Executing {self.state.pivot_recommendation} pivot...")
                # Route to appropriate pivot handler based on type
                if self.state.pivot_recommendation == PivotRecommendation.SEGMENT_PIVOT:
                    self.pivot_customer_segment()
                elif self.state.pivot_recommendation == PivotRecommendation.VALUE_PIVOT:
                    self.pivot_value_proposition()
                elif self.state.pivot_recommendation == PivotRecommendation.MODEL_PIVOT:
                    self.execute_strategic_pivot()
            else:
                print("\n✅ Proceeding with current approach")
                self.state.phase = Phase.VALIDATED

        except Exception as e:
            error_msg = f"Compass synthesis failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            # Graceful degradation: mark as validated with issues
            self.state.phase = Phase.VALIDATED
            self.state.final_recommendation = "Synthesis failed - manual review required"

    @listen("validation_complete")
    def finalize_validation(self):
        """
        Guardian's final governance review and documentation.
        Captures learnings for the Flywheel system.
        """
        print("\n🎯 Validation Complete - Final governance review...")

        try:
            # Guardian performs final audit
            result = GovernanceCrew().crew().kickoff(
                inputs={
                    "task": "final_audit",
                    "full_state": self.state.dict()
                }
            )

            if result and hasattr(result, 'pydantic') and result.pydantic:
                qa_report = result.pydantic
                self.state.qa_reports.append(qa_report)
                self.state.current_qa_status = qa_report.status
            else:
                self.state.guardian_last_issues.append("Governance Crew returned no structured output for final audit")
                self.state.current_qa_status = QAStatus.CONDITIONAL

            # Capture Flywheel learnings
            self._capture_flywheel_learnings()

            print("\n✅ VALIDATION FLOW COMPLETE")
            if self.state.qa_reports:
                print(f"   Final QA Status: {self.state.qa_reports[-1].status}")
            print(f"   Pivots executed: {len(self.state.pivot_history)}")
            print(f"   Evidence strength: {self.state.evidence_strength}")
            print(f"   Unit economics: {self.state.unit_economics_status}")

            # Generate final deliverables
            return self._generate_final_deliverables()

        except Exception as e:
            error_msg = f"Final validation failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            # Still generate deliverables with available data
            return self._generate_final_deliverables()

    def _capture_flywheel_learnings(self):
        """Capture learnings for continuous improvement"""
        learnings = {
            "validation_id": self.state.id,
            "business_idea": self.state.business_idea,
            "segments_tested": self.state.target_segments,
            "pivots_executed": self.state.pivot_history,
            "final_evidence": {
                "desirability": self.state.evidence_strength.value if self.state.evidence_strength else None,
                "feasibility": self.state.feasibility_status.value if self.state.feasibility_status else None,
                "viability": self.state.unit_economics_status.value if self.state.unit_economics_status else None
            },
            "key_learnings": [],
            "timestamp": datetime.now().isoformat()
        }

        # Extract key learnings from evidence
        if self.state.desirability_evidence:
            for experiment in self.state.desirability_evidence.experiments:
                learnings["key_learnings"].extend(experiment.key_learnings)

        # In production, this would be persisted to a knowledge base
        print(f"   📚 Captured {len(learnings['key_learnings'])} learnings for Flywheel")

    def _generate_final_deliverables(self) -> Dict[str, Any]:
        """Generate structured outputs for the user"""
        return {
            "validation_report": {
                "id": self.state.id,
                "business_idea": self.state.business_idea,
                "validation_outcome": self.state.final_recommendation,
                "evidence_summary": self.state.evidence_summary,
                "pivot_recommendation": self.state.pivot_recommendation.value if self.state.pivot_recommendation else None,
                "next_steps": self.state.next_steps
            },
            "value_proposition_canvas": {
                segment: {
                    "customer_profile": profile.dict() if profile else None,
                    "value_map": self.state.value_maps.get(segment, {})
                }
                for segment, profile in self.state.customer_profiles.items()
            },
            "evidence": {
                "desirability": self.state.desirability_evidence.dict() if self.state.desirability_evidence else None,
                "feasibility": self.state.feasibility_evidence.dict() if self.state.feasibility_evidence else None,
                "viability": self.state.viability_evidence.dict() if self.state.viability_evidence else None
            },
            "qa_report": self.state.qa_reports[-1].dict() if self.state.qa_reports else None
        }

    # ===========================================================================
    # HUMAN INPUT SIMULATION (In production, these would be async webhooks)
    # ===========================================================================

    def _get_human_input_segment_pivot(self) -> Dict[str, Any]:
        """Simulate human input for segment pivot decision"""
        # In production, this would trigger a webhook to the product app
        # For now, we simulate approval
        return {"approved": True, "new_segment": "Enterprise Consultants"}

    def _get_human_input_value_pivot(self) -> Dict[str, Any]:
        """Simulate human input for value proposition iteration"""
        return {"approved": True, "direction": "intensify_pain_relievers"}

    def _get_human_input_downgrade(self) -> Dict[str, Any]:
        """Simulate human input for feature downgrade decision"""
        return {"approved": True, "acceptable_tradeoffs": ["reduced_automation", "longer_delivery"]}

    def _get_human_input_strategic_pivot(self, pivot_decision) -> Dict[str, Any]:
        """Simulate human input for strategic pivot decision"""
        # In production, user chooses between increasing price or reducing cost
        return {"approved": True, "chosen_path": "reduce_cost"}


# ===========================================================================
# FLOW INITIALIZATION
# ===========================================================================

def create_validation_flow(entrepreneur_input: str) -> InternalValidationFlow:
    """
    Factory function to create and initialize a validation flow.

    Args:
        entrepreneur_input: The raw business idea and context from the entrepreneur

    Returns:
        Configured InternalValidationFlow ready to run
    """
    # Initialize state with new StartupValidationState schema
    initial_state = StartupValidationState(
        project_id=f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        entrepreneur_input=entrepreneur_input,
        phase=Phase.IDEATION
    )

    # Create flow with initial state
    flow = InternalValidationFlow(initial_state=initial_state)

    return flow