"""
Internal Validation Flow with Innovation Physics Logic.

This flow implements the specific decision trees from Strategyzer methodologies,
enforcing non-linear iteration based on evidence signals.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback
import os
import httpx
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.persistence import persist
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

# Import Pydantic output models for type-safe crew results
from startupai.crews.crew_outputs import (
    ServiceCrewOutput,
    SegmentPivotOutput,
    AnalysisCrewOutput,
    CompetitorAnalysisOutput,
    ValuePropIterationOutput,
    BuildCrewOutput,
    DowngradeOutput,
    GrowthCrewOutput,
    PricingTestOutput,
    DegradationTestOutput,
    SynthesisCrewOutput,
    PivotDecisionOutput,
    FinanceCrewOutput,
    OptimizedMetricsOutput,
    GovernanceCrewOutput,
)

# Import Flywheel Learning tools
from startupai.tools.learning_capture import (
    LearningCaptureTool,
    capture_pattern_learning,
    capture_outcome_learning,
)

# Import HITL tools for creative review
from startupai.tools.guardian_review import (
    GuardianReviewTool,
    review_landing_page,
    ReviewDecision,
)
# Import HITL tools for viability decisions
from startupai.tools.viability_approval import (
    ViabilityApprovalTool,
    ViabilityStatus,
    analyze_viability,
    format_viability_for_dashboard,
)
from startupai.webhooks.resume_handler import (
    ResumeHandler,
    ApprovalType,
    ViabilityChoice,
)


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

    @persist()  # Checkpoint: Initial state captured
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
                inputs={"entrepreneur_input": self.state.entrepreneur_input},
                output_pydantic=ServiceCrewOutput
            )

            # Parse the brief from Service Crew with typed output
            if result.pydantic:
                output: ServiceCrewOutput = result.pydantic
                self.state.business_idea = output.business_idea
                self.state.target_segments = output.target_segments
                self.state.assumptions = output.assumptions
                # Store additional fields from typed output
                if output.problem_statement:
                    self.state.problem_statement = output.problem_statement
                if output.solution_description:
                    self.state.solution_description = output.solution_description
                if output.revenue_model:
                    self.state.revenue_model = output.revenue_model
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

    @persist()  # Checkpoint: Customer profiles loaded
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
                        },
                        output_pydantic=AnalysisCrewOutput
                    )

                    # Store customer profile and value map with typed output
                    if result.pydantic:
                        output: AnalysisCrewOutput = result.pydantic
                        self.state.customer_profiles[segment] = output.customer_profile
                        self.state.value_maps[segment] = output.value_map
                        # Store fit score and insights
                        if output.fit_score:
                            self.state.segment_fit_scores[segment] = output.fit_score
                        if output.key_insights:
                            self.state.analysis_insights.extend(output.key_insights)
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
                    },
                    output_pydantic=CompetitorAnalysisOutput
                )
                if comp_result.pydantic:
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

    @persist()  # Checkpoint: Desirability evidence collected
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
                },
                output_pydantic=GrowthCrewOutput
            )

            # Store desirability evidence with typed output
            if result.pydantic:
                output: GrowthCrewOutput = result.pydantic
                self.state.desirability_evidence = output
                # Store ad campaign metrics
                self.state.ad_impressions = output.impressions
                self.state.ad_clicks = output.clicks
                self.state.ad_signups = output.signups
                self.state.ad_spend = output.spend_usd
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

    # ===========================================================================
    # CREATIVE APPROVAL WORKFLOW (HITL)
    # ===========================================================================

    @persist()  # Checkpoint: Before HITL creative review
    @listen(test_desirability)
    def review_creatives_for_deployment(self):
        """
        Guardian's auto-QA review of creatives (landing pages, ad copy).

        This runs after Growth Crew generates landing pages and before deployment.
        Uses GuardianReviewTool to auto-approve safe content or flag for human review.
        """
        print("\n🎨 Reviewing creatives for deployment...")

        # Check if we have landing pages to review
        landing_pages = getattr(self.state, 'landing_pages', [])
        if not landing_pages:
            print("   No landing pages to review, skipping")
            return

        # Initialize results storage
        self.state.creative_review_results = []
        self.state.creatives_needing_human_review = []
        self.state.auto_approved_creatives = []

        # Review each landing page
        for i, page in enumerate(landing_pages):
            artifact_id = f"lp_{i+1}"
            html_content = page.get('html', page) if isinstance(page, dict) else str(page)

            # Run auto-QA
            review_result = review_landing_page(
                artifact_id=artifact_id,
                html_content=html_content,
                business_context={
                    "business_idea": self.state.business_idea,
                    "target_segment": self.state.current_segment,
                }
            )

            self.state.creative_review_results.append(review_result)

            # Categorize by decision
            if review_result.decision == ReviewDecision.AUTO_APPROVED:
                self.state.auto_approved_creatives.append(artifact_id)
                print(f"   ✅ {artifact_id}: AUTO-APPROVED")
            elif review_result.decision == ReviewDecision.REJECTED:
                # Rejected creatives need fixes, not approval
                print(f"   ❌ {artifact_id}: REJECTED - {len(review_result.blocking_issues)} blockers")
            else:
                # Needs human review
                self.state.creatives_needing_human_review.append({
                    "artifact_id": artifact_id,
                    "issues": [issue.dict() for issue in review_result.issues],
                    "summary": review_result.summary,
                })
                print(f"   ⏸️ {artifact_id}: NEEDS HUMAN REVIEW - {len(review_result.issues)} issues")

        print(f"\n   Summary: {len(self.state.auto_approved_creatives)} auto-approved, "
              f"{len(self.state.creatives_needing_human_review)} need review")

    @router(review_creatives_for_deployment)
    def creative_approval_gate(self) -> str:
        """
        Router to determine if creatives can proceed or need human approval.

        Returns:
            - "creatives_approved" if all auto-approved or no creatives
            - "await_creative_approval" if some need human review
            - "creatives_rejected" if all rejected (must regenerate)
        """
        # No creatives to review
        if not hasattr(self.state, 'creative_review_results') or not self.state.creative_review_results:
            return "creatives_approved"

        needs_review = len(getattr(self.state, 'creatives_needing_human_review', []))
        auto_approved = len(getattr(self.state, 'auto_approved_creatives', []))
        total = len(self.state.creative_review_results)

        # All auto-approved
        if auto_approved == total:
            print("✅ All creatives auto-approved")
            return "creatives_approved"

        # Some need human review
        if needs_review > 0:
            print(f"⏸️ {needs_review} creatives need human review - pausing for approval")
            self.state.human_input_required = True
            self.state.human_input_reason = (
                f"{needs_review} creative artifacts need human review before deployment. "
                "Please review the flagged issues in the dashboard."
            )
            return "await_creative_approval"

        # All rejected - need to regenerate
        print("❌ All creatives rejected - regeneration required")
        return "creatives_rejected"

    @persist()  # Checkpoint: HITL pause - awaiting creative approval
    @listen("await_creative_approval")
    def pause_for_creative_approval(self):
        """
        Pause the flow to await human approval of creatives.

        In production, this triggers a webhook to the product app dashboard
        where the user can review and approve/reject each creative.

        The flow resumes when the product app calls POST /resume with:
        {
            "kickoff_id": "...",
            "approval_type": "creative_approval",
            "creative_approval": {
                "approved_artifact_ids": ["lp_1", "lp_2"],
                "rejected_artifact_ids": ["lp_3"],
                "feedback": "Please fix the headline on lp_3"
            }
        }
        """
        print("\n⏸️ FLOW PAUSED: Awaiting human creative approval")
        print(f"   Kickoff ID: {self.state.kickoff_id}")
        print(f"   Artifacts needing review: {len(self.state.creatives_needing_human_review)}")

        # Notify product app via webhook that approval is needed
        self._notify_creative_approval_needed()

        # In production with CrewAI AMP, the flow state is persisted and
        # the flow resumes when /resume webhook is called.
        # For local testing, we simulate immediate approval.
        if not os.environ.get("CREWAI_AMP"):
            print("   (Local mode: simulating immediate approval)")
            self._handle_creative_resume({
                "approved_artifact_ids": [item["artifact_id"] for item in self.state.creatives_needing_human_review],
                "rejected_artifact_ids": [],
            })

    def _notify_creative_approval_needed(self):
        """Notify product app that creative approval is needed."""
        webhook_url = os.environ.get("STARTUPAI_WEBHOOK_URL")
        bearer_token = os.environ.get("STARTUPAI_WEBHOOK_BEARER_TOKEN")

        if not webhook_url or not bearer_token:
            print("   ⚠️ Webhook not configured, cannot notify")
            return

        payload = {
            "flow_type": "creative_approval_needed",
            "kickoff_id": self.state.kickoff_id,
            "project_id": self.state.project_id,
            "user_id": self.state.user_id,
            "creatives_needing_review": self.state.creatives_needing_human_review,
            "auto_approved_creatives": self.state.auto_approved_creatives,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {bearer_token}",
                        "Content-Type": "application/json",
                    }
                )
                if response.status_code == 200:
                    print("   📤 Product app notified of pending approval")
                else:
                    print(f"   ⚠️ Notification failed: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Notification error: {e}")

    def _handle_creative_resume(self, creative_approval: Dict[str, Any]):
        """
        Handle resume from creative approval webhook.

        Called when the product app sends POST /resume with approval decision.
        """
        approved = creative_approval.get("approved_artifact_ids", [])
        rejected = creative_approval.get("rejected_artifact_ids", [])
        feedback = creative_approval.get("feedback", "")

        print(f"\n🔄 Creative approval received:")
        print(f"   Approved: {len(approved)}")
        print(f"   Rejected: {len(rejected)}")

        # Update state
        self.state.human_input_required = False
        self.state.auto_approved_creatives.extend(approved)

        # Store feedback for rejected items
        if rejected and feedback:
            self.state.guardian_last_issues.append(f"Creative feedback: {feedback}")

        # If any approved, we can proceed
        if approved:
            print("   → Proceeding with approved creatives")
        elif rejected:
            print("   → All creatives rejected, may need regeneration")

    @listen("creatives_approved")
    def proceed_with_approved_creatives(self):
        """Continue flow after creatives are approved (auto or human)."""
        print("\n✅ Creatives approved - continuing validation flow")
        # The flow continues naturally from here via the desirability_gate router

    @listen("creatives_rejected")
    def handle_rejected_creatives(self):
        """Handle case where all creatives were rejected."""
        print("\n🔧 Regenerating creatives after rejection...")

        # Clear old results
        self.state.landing_pages = []
        self.state.creative_review_results = []

        # The Growth Crew will regenerate when desirability retests
        self.state.guardian_last_issues.append(
            "All creatives rejected - regeneration triggered"
        )

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
            },
            output_pydantic=SegmentPivotOutput
        )

        # Update state with new segment from typed output
        output: SegmentPivotOutput = result.pydantic
        new_segment = output.new_segment
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
            },
            output_pydantic=ValuePropIterationOutput
        )

        # Update value proposition from typed output
        output: ValuePropIterationOutput = result.pydantic
        self.state.value_maps[self.state.target_segments[0]] = output.new_value_map
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
                },
                output_pydantic=GrowthCrewOutput
            )

            # Update evidence with typed output
            if result.pydantic:
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

    @persist()  # Checkpoint: Feasibility phase entered
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
                },
                output_pydantic=BuildCrewOutput
            )

            # Store feasibility evidence with typed output
            if result.pydantic:
                output: BuildCrewOutput = result.pydantic
                self.state.feasibility_evidence = output
                # Store cost estimates
                self.state.api_costs = output.api_costs
                self.state.infra_costs = output.infra_costs
                self.state.total_monthly_cost = output.total_monthly_cost
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
            },
            output_pydantic=DowngradeOutput
        )

        # Update value maps with downgraded version from typed output
        output: DowngradeOutput = downgrade_result.pydantic
        for segment in self.state.target_segments:
            self.state.value_maps[segment] = output.downgraded_value_maps[segment]

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
            },
            output_pydantic=DegradationTestOutput
        )

        # Compare acceptance of degraded version from typed output
        output: DegradationTestOutput = result.pydantic
        degraded_acceptance = output.acceptance_rate

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

    @persist()  # Checkpoint: Viability phase entered
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
                },
                output_pydantic=FinanceCrewOutput
            )

            # Store viability evidence with typed output
            if result.pydantic:
                output: FinanceCrewOutput = result.pydantic
                self.state.viability_evidence = output
                # Store key metrics in state for easy access
                self.state.cac = output.cac
                self.state.ltv = output.ltv
                self.state.ltv_cac_ratio = output.ltv_cac_ratio
                self.state.gross_margin = output.gross_margin
                self.state.tam = output.tam_usd
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
        - If CAC > LTV → Route to HITL for Strategic Pivot Decision
        - Two paths: Increase Price (test willingness) OR Reduce Cost (reduce features)
        """
        print("\n🚦 Viability Gate - Evaluating unit economics...")

        # UNIT ECONOMICS TRIGGER
        if self.state.unit_economics_status == UnitEconomicsStatus.UNDERWATER:
            print(f"❌ UNIT ECONOMICS FAILURE: CAC > LTV ({self.state.viability_evidence.ltv_cac_ratio:.1f})")
            print("   → Routing to HITL for strategic pivot decision")
            print("   → Options: 1) Increase Price, 2) Reduce Cost, 3) Kill")

            self.state.human_input_required = True
            self.state.human_input_reason = (
                f"Unit economics underwater (LTV/CAC = {self.state.viability_evidence.ltv_cac_ratio:.1f}). "
                "Strategic decision needed: increase price, reduce costs, or kill?"
            )
            return "await_viability_decision"

        # MARGINAL ECONOMICS
        elif self.state.unit_economics_status == UnitEconomicsStatus.MARGINAL:
            print("⚠️ Marginal unit economics - optimization needed")
            if self.state.retry_count < 2:  # Allow 2 optimization attempts
                self.state.retry_count += 1
                return "optimize_economics"
            else:
                # After 2 failed optimizations, escalate to HITL
                self.state.human_input_required = True
                self.state.human_input_reason = (
                    f"Marginal unit economics (LTV/CAC = {self.state.viability_evidence.ltv_cac_ratio:.1f}) "
                    "after optimization attempts. Human decision needed."
                )
                return "await_viability_decision"

        # PROFITABLE
        elif self.state.unit_economics_status == UnitEconomicsStatus.PROFITABLE:
            print("✅ Viability VALIDATED - Unit economics profitable")
            self.state.phase = Phase.VALIDATED
            return "validation_complete"

        else:
            return "compass_synthesis_required"

    # ===========================================================================
    # VIABILITY APPROVAL WORKFLOW (HITL)
    # ===========================================================================

    @persist()  # Checkpoint: HITL pause - awaiting viability decision
    @listen("await_viability_decision")
    def pause_for_viability_decision(self):
        """
        Pause the flow to await human viability/pivot decision.

        Uses ViabilityApprovalTool to analyze unit economics and generate
        pivot recommendations for the human dashboard.

        The flow resumes when the product app calls POST /resume with:
        {
            "kickoff_id": "...",
            "approval_type": "viability_decision",
            "viability_decision": {
                "choice": "price_pivot" | "cost_pivot" | "kill" | "continue",
                "rationale": "...",
                "new_price_target": 99.0,        // for price_pivot
                "cost_reduction_target": 0.3,    // for cost_pivot
                "features_to_cut": ["feature1"]  // for cost_pivot
            }
        }
        """
        print("\n⏸️ FLOW PAUSED: Awaiting human viability decision")
        print(f"   Kickoff ID: {self.state.kickoff_id}")

        # Use ViabilityApprovalTool to analyze and generate recommendations
        viability_result = analyze_viability(
            cac=self.state.viability_evidence.cac if self.state.viability_evidence else 0,
            ltv=self.state.viability_evidence.ltv if self.state.viability_evidence else 0,
            gross_margin=self.state.viability_evidence.gross_margin if self.state.viability_evidence else 0,
            tam=self.state.viability_evidence.tam_usd if self.state.viability_evidence else None,
            context={
                "business_idea": self.state.business_idea,
                "segment": self.state.current_segment,
            }
        )

        # Store viability analysis for dashboard
        self.state.viability_analysis = format_viability_for_dashboard(viability_result)

        print(f"   Status: {viability_result.status.value}")
        print(f"   LTV/CAC: {viability_result.ltv_cac_ratio:.2f}")
        if viability_result.recommended_pivot:
            print(f"   Recommended: {viability_result.recommended_pivot.value}")

        # Notify product app via webhook
        self._notify_viability_approval_needed(viability_result)

        # In production with CrewAI AMP, the flow state is persisted and
        # the flow resumes when /resume webhook is called.
        # For local testing, simulate immediate decision.
        if not os.environ.get("CREWAI_AMP"):
            print("   (Local mode: simulating immediate decision)")
            # Simulate choosing the recommended pivot or cost_pivot
            simulated_choice = viability_result.recommended_pivot.value if viability_result.recommended_pivot else "cost_pivot"
            self._handle_viability_resume({
                "choice": simulated_choice,
                "rationale": "Auto-selected in local mode",
                "cost_reduction_target": 0.3,
                "features_to_cut": [],
            })

    def _notify_viability_approval_needed(self, viability_result):
        """Notify product app that viability decision is needed."""
        webhook_url = os.environ.get("STARTUPAI_WEBHOOK_URL")
        bearer_token = os.environ.get("STARTUPAI_WEBHOOK_BEARER_TOKEN")

        if not webhook_url or not bearer_token:
            print("   ⚠️ Webhook not configured, cannot notify")
            return

        payload = {
            "flow_type": "viability_decision_needed",
            "kickoff_id": self.state.kickoff_id,
            "project_id": self.state.project_id,
            "user_id": self.state.user_id,
            "viability_analysis": format_viability_for_dashboard(viability_result),
            "current_metrics": {
                "cac": self.state.viability_evidence.cac if self.state.viability_evidence else 0,
                "ltv": self.state.viability_evidence.ltv if self.state.viability_evidence else 0,
                "ltv_cac_ratio": self.state.viability_evidence.ltv_cac_ratio if self.state.viability_evidence else 0,
                "gross_margin": self.state.viability_evidence.gross_margin if self.state.viability_evidence else 0,
            }
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {bearer_token}",
                        "Content-Type": "application/json",
                    }
                )
                if response.status_code == 200:
                    print("   📤 Product app notified of pending viability decision")
                else:
                    print(f"   ⚠️ Notification failed: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Notification error: {e}")

    def _handle_viability_resume(self, viability_decision: Dict[str, Any]):
        """
        Handle resume from viability decision webhook.

        Routes to appropriate pivot execution based on human choice.
        """
        choice = viability_decision.get("choice", "")
        rationale = viability_decision.get("rationale", "")

        print(f"\n🔄 Viability decision received: {choice}")
        print(f"   Rationale: {rationale}")

        # Update state
        self.state.human_input_required = False
        self.state.viability_decision = viability_decision

        # Route based on choice
        if choice == ViabilityChoice.PRICE_PIVOT.value or choice == "price_pivot":
            print("   → Executing price pivot")
            new_price_target = viability_decision.get("new_price_target")
            self._execute_price_pivot(new_price_target)
        elif choice == ViabilityChoice.COST_PIVOT.value or choice == "cost_pivot":
            print("   → Executing cost pivot")
            cost_target = viability_decision.get("cost_reduction_target", 0.3)
            features_to_cut = viability_decision.get("features_to_cut", [])
            self._execute_cost_pivot(cost_target, features_to_cut)
        elif choice == ViabilityChoice.KILL.value or choice == "kill":
            print("   → Project KILLED by human decision")
            kill_reason = viability_decision.get("kill_reason", rationale)
            self._execute_kill(kill_reason)
        elif choice == ViabilityChoice.CONTINUE.value or choice == "continue":
            print("   → Proceeding despite warnings")
            self.state.phase = Phase.VALIDATED

    def _execute_price_pivot(self, new_price_target: Optional[float] = None):
        """Execute price pivot and re-test desirability."""
        # Calculate price multiplier
        current_price = self.state.viability_evidence.ltv / 12 if self.state.viability_evidence else 100
        if new_price_target:
            price_multiplier = new_price_target / current_price
        else:
            price_multiplier = 1.5  # Default 50% increase

        print(f"   Price multiplier: {price_multiplier:.1f}x")

        # Update viability evidence optimistically
        if self.state.viability_evidence:
            self.state.viability_evidence.ltv *= price_multiplier
            self.state.viability_evidence.ltv_cac_ratio = (
                self.state.viability_evidence.ltv / self.state.viability_evidence.cac
            )

        # Record pivot
        self.state.add_pivot_to_history(
            PivotRecommendation.PRICE_PIVOT,
            f"Price pivot: {price_multiplier:.1f}x increase"
        )

        # Recalculate signals
        self._calculate_viability_signals()

        # Route back to test if price change is accepted
        if self.state.unit_economics_status == UnitEconomicsStatus.PROFITABLE:
            print("   ✅ Price pivot successful - economics now profitable")
            self.state.phase = Phase.VALIDATED
        else:
            print("   ⚠️ Price pivot not sufficient - further optimization needed")

    def _execute_cost_pivot(self, cost_reduction_target: float, features_to_cut: List[str]):
        """Execute cost pivot by reducing CAC."""
        print(f"   Cost reduction target: {cost_reduction_target:.0%}")
        if features_to_cut:
            print(f"   Features to cut: {', '.join(features_to_cut)}")

        # Update viability evidence
        if self.state.viability_evidence:
            new_cac = self.state.viability_evidence.cac * (1 - cost_reduction_target)
            self.state.viability_evidence.cac = new_cac
            self.state.viability_evidence.ltv_cac_ratio = (
                self.state.viability_evidence.ltv / new_cac
            )
            print(f"   New CAC: ${new_cac:.2f}")

        # Record pivot
        self.state.add_pivot_to_history(
            PivotRecommendation.COST_PIVOT,
            f"Cost pivot: {cost_reduction_target:.0%} reduction, cut features: {features_to_cut}"
        )

        # Recalculate signals
        self._calculate_viability_signals()

        # Check if economics are now viable
        if self.state.unit_economics_status == UnitEconomicsStatus.PROFITABLE:
            print("   ✅ Cost pivot successful - economics now profitable")
            self.state.phase = Phase.VALIDATED
        else:
            print("   ⚠️ Cost pivot not sufficient - may need further action")

    def _execute_kill(self, reason: str):
        """Execute project kill based on human decision."""
        print(f"   Kill reason: {reason}")

        self.state.phase = Phase.KILLED
        self.state.pivot_recommendation = PivotRecommendation.KILL
        self.state.final_recommendation = f"Project terminated by human decision: {reason}"

        # Record in history
        self.state.add_pivot_to_history(
            PivotRecommendation.KILL,
            reason
        )

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
            },
            output_pydantic=PivotDecisionOutput
        )

        # Get pivot decision from typed output
        pivot_decision: PivotDecisionOutput = result.pydantic

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
            },
            output_pydantic=PricingTestOutput
        )

        # Update viability evidence with new pricing from typed output
        output: PricingTestOutput = result.pydantic
        if output.acceptance_rate > 0.5:  # 50% accept higher price
            print(f"✅ Higher price accepted ({output.acceptance_rate:.1%})")
            self.state.viability_evidence.ltv *= new_price_multiplier
            self.state.viability_evidence.ltv_cac_ratio = (
                self.state.viability_evidence.ltv / self.state.viability_evidence.cac
            )
            self._calculate_viability_signals()
        else:
            print(f"❌ Higher price rejected ({output.acceptance_rate:.1%})")
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
            },
            output_pydantic=DowngradeOutput
        )

        # Update cost structure from typed output
        output: DowngradeOutput = result.pydantic
        reduced_features = output.removed_features
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
                },
                output_pydantic=OptimizedMetricsOutput
            )

            # Apply optimizations from typed output
            if result.pydantic:
                output: OptimizedMetricsOutput = result.pydantic
                self.state.viability_evidence = output.optimized_metrics
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
                },
                output_pydantic=SynthesisCrewOutput
            )

            # Extract recommendation from typed output
            if result.pydantic:
                synthesis: SynthesisCrewOutput = result.pydantic
                self.state.final_recommendation = synthesis.recommendation
                self.state.evidence_summary = synthesis.evidence_summary
                self.state.next_steps = synthesis.next_steps
                self.state.pivot_recommendation = synthesis.pivot_recommendation
                # Store confidence score
                self.state.synthesis_confidence = synthesis.confidence_score
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

    @persist()  # Checkpoint: Final validation state
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
                },
                output_pydantic=GovernanceCrewOutput
            )

            # Process typed output from Governance Crew
            if result.pydantic:
                qa_report: GovernanceCrewOutput = result.pydantic
                self.state.qa_reports.append(qa_report)
                self.state.current_qa_status = qa_report.status
                # Store governance metrics
                self.state.framework_compliance = qa_report.framework_compliance
                self.state.logical_consistency = qa_report.logical_consistency
                self.state.completeness = qa_report.completeness
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
            deliverables = self._generate_final_deliverables()

            # Persist to Supabase via product app webhook
            self._persist_to_supabase(deliverables)

            return deliverables

        except Exception as e:
            error_msg = f"Final validation failed: {str(e)}"
            self.state.guardian_last_issues.append(error_msg)
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            # Still generate deliverables with available data and try to persist
            deliverables = self._generate_final_deliverables()
            self._persist_to_supabase(deliverables)
            return deliverables

    def _capture_flywheel_learnings(self):
        """
        Capture learnings for the Flywheel continuous improvement system.

        Persists anonymized learnings to the learnings table via LearningCaptureTool.
        Captures three types of learnings:
        1. Outcome learning - final validation result
        2. Pattern learnings - recurring patterns observed during validation
        3. Domain learnings - industry-specific insights
        """
        print("\n📚 Capturing Flywheel learnings...")

        captured_count = 0

        # Build context for learning capture (will be anonymized)
        context = {
            "desirability_signal": self.state.evidence_strength.value if self.state.evidence_strength else "NONE",
            "feasibility_signal": self.state.feasibility_status.value if self.state.feasibility_status else "NONE",
            "viability_signal": self.state.unit_economics_status.value if self.state.unit_economics_status else "NONE",
            "phase": self.state.phase.value if self.state.phase else "UNKNOWN",
            "pivot_history": [p.get("type", "unknown") for p in self.state.pivot_history] if self.state.pivot_history else [],
        }

        # Determine industry from business idea (simplified classification)
        industry = self._classify_industry()

        try:
            # 1. Capture OUTCOME learning - the final validation result
            outcome_title = f"Validation outcome: {self.state.pivot_recommendation.value if self.state.pivot_recommendation else 'PROCEED'}"
            outcome_description = (
                f"Business idea validation completed in phase {self.state.phase.value if self.state.phase else 'UNKNOWN'}. "
                f"Desirability: {context['desirability_signal']}, "
                f"Feasibility: {context['feasibility_signal']}, "
                f"Viability: {context['viability_signal']}. "
                f"Pivots executed: {len(self.state.pivot_history)}."
            )

            result = capture_outcome_learning(
                title=outcome_title,
                description=outcome_description,
                context=context,
                founder=self.state.user_id or self.state.id,
                phase=self.state.phase.value if self.state.phase else "VALIDATED",
                tags=["validation_outcome", f"phase_{self.state.phase.value if self.state.phase else 'validated'}"],
                confidence_score=self.state.synthesis_confidence if hasattr(self.state, 'synthesis_confidence') and self.state.synthesis_confidence else 0.7,
                industry=industry,
            )
            if "successfully" in result.lower():
                captured_count += 1

            # 2. Capture PATTERN learnings from pivots
            if self.state.pivot_history:
                for pivot in self.state.pivot_history:
                    pivot_type = pivot.get("type", "unknown")
                    pivot_reason = pivot.get("reason", "No reason provided")

                    pattern_title = f"Pivot pattern: {pivot_type}"
                    pattern_description = (
                        f"Pivot executed during validation: {pivot_type}. "
                        f"Trigger: {pivot_reason}"
                    )

                    result = capture_pattern_learning(
                        title=pattern_title,
                        description=pattern_description,
                        context=context,
                        founder=self.state.user_id or self.state.id,
                        phase=self.state.phase.value if self.state.phase else "VALIDATED",
                        tags=["pivot_pattern", pivot_type.lower().replace(" ", "_")],
                        confidence_score=0.8,
                        industry=industry,
                    )
                    if "successfully" in result.lower():
                        captured_count += 1

            # 3. Capture key learnings from experiments
            if self.state.desirability_evidence and hasattr(self.state.desirability_evidence, 'experiments'):
                for experiment in self.state.desirability_evidence.experiments[:3]:  # Limit to top 3
                    if hasattr(experiment, 'key_learnings') and experiment.key_learnings:
                        for learning in experiment.key_learnings[:2]:  # Max 2 per experiment
                            result = capture_pattern_learning(
                                title=f"Experiment insight: {experiment.name if hasattr(experiment, 'name') else 'Unnamed'}",
                                description=learning,
                                context=context,
                                founder=self.state.user_id or self.state.id,
                                phase="DESIRABILITY",
                                tags=["experiment_insight", "desirability"],
                                confidence_score=0.6,
                                industry=industry,
                            )
                            if "successfully" in result.lower():
                                captured_count += 1

            print(f"   ✅ Captured {captured_count} learnings for Flywheel system")

        except Exception as e:
            # Learning capture should not fail the flow
            print(f"   ⚠️ Flywheel learning capture failed (non-blocking): {str(e)}")
            traceback.print_exc()

    def _classify_industry(self) -> Optional[str]:
        """
        Simple industry classification based on business idea keywords.
        In production, this could use NLP/LLM classification.
        """
        if not self.state.business_idea:
            return None

        idea_lower = self.state.business_idea.lower()

        # Simple keyword-based classification
        if any(kw in idea_lower for kw in ["saas", "software", "platform", "api", "cloud"]):
            if any(kw in idea_lower for kw in ["enterprise", "b2b", "business"]):
                return "B2B SaaS"
            return "SaaS"
        elif any(kw in idea_lower for kw in ["ecommerce", "e-commerce", "shop", "retail", "d2c", "direct-to-consumer"]):
            return "E-commerce"
        elif any(kw in idea_lower for kw in ["marketplace", "platform", "two-sided", "matching"]):
            return "Marketplace"
        elif any(kw in idea_lower for kw in ["fintech", "finance", "payment", "banking", "lending"]):
            return "Fintech"
        elif any(kw in idea_lower for kw in ["health", "medical", "healthcare", "wellness"]):
            return "Healthcare"
        elif any(kw in idea_lower for kw in ["education", "learning", "edtech", "course"]):
            return "EdTech"
        else:
            return None  # Unknown - will still capture learning without industry filter

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

    def _persist_to_supabase(self, deliverables: Dict[str, Any]) -> bool:
        """
        Persist validation results to Supabase via the unified webhook.

        Calls POST /api/crewai/webhook on app.startupai.site to store:
        - Validation report in reports table
        - Evidence in evidence table
        - Entrepreneur brief in entrepreneur_briefs table

        Returns:
            True if persistence succeeded, False otherwise
        """
        # Get unified webhook URL and bearer token from environment
        webhook_url = os.environ.get("STARTUPAI_WEBHOOK_URL")
        bearer_token = os.environ.get("STARTUPAI_WEBHOOK_BEARER_TOKEN")

        if not webhook_url:
            print("⚠️ STARTUPAI_WEBHOOK_URL not configured, skipping persistence")
            return False

        if not bearer_token:
            print("⚠️ STARTUPAI_WEBHOOK_BEARER_TOKEN not configured, skipping persistence")
            return False

        # Skip persistence if no project_id or user_id
        if not self.state.project_id or not self.state.user_id:
            print("⚠️ Missing project_id or user_id, skipping persistence")
            return False

        # Build the payload for the unified webhook with flow_type
        payload = {
            "flow_type": "founder_validation",
            "project_id": self.state.project_id,
            "user_id": self.state.user_id,
            "kickoff_id": self.state.kickoff_id or "",
            "session_id": self.state.session_id or None,
            "validation_report": deliverables.get("validation_report", {}),
            "value_proposition_canvas": deliverables.get("value_proposition_canvas", {}),
            "evidence": deliverables.get("evidence", {}),
            "qa_report": deliverables.get("qa_report"),
            "completed_at": datetime.now().isoformat(),
        }

        try:
            print(f"\n📤 Persisting results to Supabase...")
            print(f"   Webhook: {webhook_url}")
            print(f"   Project: {self.state.project_id}")

            # Make the HTTP request
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {bearer_token}",
                        "Content-Type": "application/json",
                    }
                )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Results persisted successfully")
                print(f"   Report ID: {result.get('report_id')}")
                print(f"   Evidence created: {result.get('evidence_created', 0)}")
                return True
            else:
                print(f"❌ Persistence failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False

        except httpx.TimeoutException:
            print("❌ Persistence timed out")
            return False
        except httpx.RequestError as e:
            print(f"❌ Persistence request failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected persistence error: {e}")
            traceback.print_exc()
            return False

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

def create_validation_flow(
    entrepreneur_input: str,
    project_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    kickoff_id: Optional[str] = None,
) -> InternalValidationFlow:
    """
    Factory function to create and initialize a validation flow.

    Args:
        entrepreneur_input: The raw business idea and context from the entrepreneur
        project_id: UUID of the project in the product app (for result persistence)
        user_id: UUID of the user in the product app (for result persistence)
        session_id: Onboarding session ID (for entrepreneur_briefs linking)
        kickoff_id: CrewAI kickoff ID (for status tracking)

    Returns:
        Configured InternalValidationFlow ready to run
    """
    # Generate a unique validation ID
    validation_id = f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Create flow with state values passed as kwargs
    # CrewAI Flow expects state fields as direct kwargs, not an initial_state object
    flow = InternalValidationFlow(
        id=validation_id,
        entrepreneur_input=entrepreneur_input,
        phase=Phase.IDEATION.value,  # Pass enum value for serialization
        project_id=project_id or validation_id,
        user_id=user_id or "",
        session_id=session_id or "",
        kickoff_id=kickoff_id or "",
    )

    return flow