"""
Consultant Onboarding Flow.

This flow processes consultant practice data collected during onboarding
and generates personalized recommendations for how to use StartupAI effectively.

Unlike the internal validation flow (which validates business ideas), this flow
helps consultants optimize their practice and understand how to best leverage
the StartupAI platform for their clients.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import traceback
import os
import httpx
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, start, listen
from crewai import Crew

from startupai.crews.service.service_crew import ServiceCrew


# =======================================================================================
# STATE SCHEMAS
# =======================================================================================

class ConsultantPracticeData(BaseModel):
    """Data collected during consultant onboarding."""
    company_name: str = ""
    practice_size: str = "solo"  # solo, 2-10, 11-50, 51+
    current_clients: int = 0
    industries: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    pain_points: str = ""
    white_label_enabled: bool = False
    goals: Dict[str, Any] = Field(default_factory=dict)


class ConsultantOnboardingState(BaseModel):
    """State for the consultant onboarding flow."""
    # Identifiers
    id: str = ""
    user_id: str = ""
    session_id: str = ""

    # Input data
    practice_data: ConsultantPracticeData = Field(default_factory=ConsultantPracticeData)
    conversation_summary: str = ""

    # Analysis results
    practice_analysis: Dict[str, Any] = Field(default_factory=dict)
    client_fit_assessment: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    onboarding_tips: List[str] = Field(default_factory=list)

    # Platform configuration
    suggested_templates: List[str] = Field(default_factory=list)
    suggested_workflows: List[str] = Field(default_factory=list)
    white_label_config_suggestions: Dict[str, Any] = Field(default_factory=dict)

    # Status
    completed: bool = False
    error: Optional[str] = None


# =======================================================================================
# OUTPUT MODELS
# =======================================================================================

class PracticeAnalysisOutput(BaseModel):
    """Output from practice analysis task."""
    practice_strengths: List[str] = Field(default_factory=list)
    practice_gaps: List[str] = Field(default_factory=list)
    market_positioning: str = ""
    growth_opportunities: List[str] = Field(default_factory=list)
    client_profile_summary: str = ""


class ConsultantRecommendationsOutput(BaseModel):
    """Output from recommendations task."""
    platform_recommendations: List[str] = Field(default_factory=list)
    client_onboarding_tips: List[str] = Field(default_factory=list)
    suggested_templates: List[str] = Field(default_factory=list)
    suggested_workflows: List[str] = Field(default_factory=list)
    white_label_suggestions: Dict[str, Any] = Field(default_factory=dict)
    success_metrics: List[str] = Field(default_factory=list)


# =======================================================================================
# CONSULTANT ONBOARDING FLOW
# =======================================================================================

class ConsultantOnboardingFlow(Flow[ConsultantOnboardingState]):
    """
    Flow for processing consultant onboarding data and generating
    personalized recommendations.

    This flow:
    1. Analyzes the consultant's practice (focus areas, services, tools)
    2. Assesses what types of clients would benefit most
    3. Generates platform usage recommendations
    4. Suggests templates and workflows based on practice focus
    5. Provides white-label configuration suggestions if enabled
    """

    @start()
    def analyze_practice(self):
        """
        Analyze the consultant's practice data to understand their
        specialization, strengths, and gaps.
        """
        print("\n🏢 Starting Consultant Onboarding Flow")
        print(f"   Consultant: {self.state.practice_data.company_name}")
        print(f"   Practice Size: {self.state.practice_data.practice_size}")

        try:
            # Build analysis prompt from practice data
            practice_summary = self._build_practice_summary()

            # Use Service Crew's consultant_onboarding_agent for analysis
            result = ServiceCrew().crew().kickoff(
                inputs={
                    "task": "analyze_consultant_practice",
                    "practice_summary": practice_summary,
                    "industries": self.state.practice_data.industries,
                    "services": self.state.practice_data.services,
                    "tools": self.state.practice_data.tools_used,
                    "pain_points": self.state.practice_data.pain_points,
                }
            )

            if result.pydantic:
                output: PracticeAnalysisOutput = result.pydantic
                self.state.practice_analysis = {
                    "strengths": output.practice_strengths,
                    "gaps": output.practice_gaps,
                    "positioning": output.market_positioning,
                    "opportunities": output.growth_opportunities,
                    "client_profile": output.client_profile_summary,
                }
                print(f"✅ Practice analysis complete")
                print(f"   Strengths identified: {len(output.practice_strengths)}")
                print(f"   Growth opportunities: {len(output.growth_opportunities)}")
            else:
                # Fallback: create basic analysis
                self.state.practice_analysis = self._create_basic_analysis()
                print("⚠️ Using basic practice analysis (no structured output)")

        except Exception as e:
            error_msg = f"Practice analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            # Continue with basic analysis
            self.state.practice_analysis = self._create_basic_analysis()

    def _build_practice_summary(self) -> str:
        """Build a text summary of the practice for analysis."""
        pd = self.state.practice_data
        return f"""
Practice: {pd.company_name}
Size: {pd.practice_size} ({pd.current_clients} current clients)
Industries: {', '.join(pd.industries) if pd.industries else 'Not specified'}
Services: {', '.join(pd.services) if pd.services else 'Not specified'}
Tools Used: {', '.join(pd.tools_used) if pd.tools_used else 'Not specified'}
Pain Points: {pd.pain_points or 'Not specified'}
White Label Interest: {'Yes' if pd.white_label_enabled else 'No'}
"""

    def _create_basic_analysis(self) -> Dict[str, Any]:
        """Create basic analysis when AI analysis fails."""
        pd = self.state.practice_data
        return {
            "strengths": [
                f"Experience in {', '.join(pd.industries[:3])}" if pd.industries else "Broad industry experience",
                f"Offering {len(pd.services)} service types" if pd.services else "Diverse service offerings",
            ],
            "gaps": [
                "Consider expanding digital tools usage" if len(pd.tools_used or []) < 3 else "",
            ],
            "positioning": f"{'Solo practitioner' if pd.practice_size == 'solo' else 'Team-based'} innovation consultancy",
            "opportunities": [
                "AI-powered validation for clients",
                "Scalable startup assessment services",
            ],
            "client_profile": "Early-stage founders and corporate innovation teams",
        }

    @listen(analyze_practice)
    def generate_recommendations(self):
        """
        Generate personalized recommendations for platform usage
        based on the practice analysis.
        """
        print("\n💡 Generating platform recommendations...")

        try:
            # Use Service Crew to generate recommendations
            result = ServiceCrew().crew().kickoff(
                inputs={
                    "task": "generate_consultant_recommendations",
                    "practice_analysis": self.state.practice_analysis,
                    "practice_data": self.state.practice_data.model_dump(),
                    "conversation_summary": self.state.conversation_summary,
                }
            )

            if result.pydantic:
                output: ConsultantRecommendationsOutput = result.pydantic
                self.state.recommendations = output.platform_recommendations
                self.state.onboarding_tips = output.client_onboarding_tips
                self.state.suggested_templates = output.suggested_templates
                self.state.suggested_workflows = output.suggested_workflows

                if self.state.practice_data.white_label_enabled:
                    self.state.white_label_config_suggestions = output.white_label_suggestions

                print(f"✅ Recommendations generated")
                print(f"   Platform tips: {len(self.state.recommendations)}")
                print(f"   Suggested templates: {len(self.state.suggested_templates)}")
            else:
                # Fallback recommendations
                self.state.recommendations = self._create_basic_recommendations()
                self.state.onboarding_tips = self._create_basic_tips()
                print("⚠️ Using basic recommendations (no structured output)")

        except Exception as e:
            error_msg = f"Recommendation generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            # Use fallback recommendations
            self.state.recommendations = self._create_basic_recommendations()
            self.state.onboarding_tips = self._create_basic_tips()

    def _create_basic_recommendations(self) -> List[str]:
        """Create basic recommendations when AI fails."""
        pd = self.state.practice_data
        recs = [
            "Start by adding your first client to experience the validation workflow",
            "Review the validation report templates to customize for your brand",
        ]

        if pd.white_label_enabled:
            recs.append("Configure your white-label settings to match your brand identity")

        if "lean startup" in ' '.join(pd.services or []).lower():
            recs.append("The Lean Canvas integration will complement your existing methodology")

        if pd.practice_size in ["11-50", "51+"]:
            recs.append("Consider setting up team roles for collaborative client management")

        return recs

    def _create_basic_tips(self) -> List[str]:
        """Create basic onboarding tips."""
        return [
            "Introduce StartupAI validation to clients as an objective 'second opinion' on their business model",
            "Use the evidence-based reports to facilitate strategic discussions",
            "Share gated progress with clients to maintain engagement throughout validation",
        ]

    @listen(generate_recommendations)
    def finalize_onboarding(self):
        """
        Finalize the onboarding process and persist results.
        """
        print("\n🎯 Finalizing consultant onboarding...")

        self.state.completed = True

        # Build deliverables
        deliverables = {
            "consultant_id": self.state.user_id,
            "session_id": self.state.session_id,
            "practice_analysis": self.state.practice_analysis,
            "recommendations": self.state.recommendations,
            "onboarding_tips": self.state.onboarding_tips,
            "suggested_templates": self.state.suggested_templates,
            "suggested_workflows": self.state.suggested_workflows,
            "white_label_suggestions": self.state.white_label_config_suggestions,
            "completed_at": datetime.now().isoformat(),
        }

        # Persist to Supabase
        success = self._persist_to_supabase(deliverables)

        print("\n✅ CONSULTANT ONBOARDING COMPLETE")
        print(f"   Recommendations: {len(self.state.recommendations)}")
        print(f"   Client tips: {len(self.state.onboarding_tips)}")
        print(f"   Persisted: {'Yes' if success else 'No'}")

        return deliverables

    def _persist_to_supabase(self, deliverables: Dict[str, Any]) -> bool:
        """
        Persist onboarding results to Supabase via the unified webhook.

        Updates the consultant_profiles table with:
        - AI-generated recommendations
        - Suggested templates and workflows
        - White-label configuration suggestions
        """
        webhook_url = os.environ.get("STARTUPAI_WEBHOOK_URL")
        bearer_token = os.environ.get("STARTUPAI_WEBHOOK_BEARER_TOKEN")

        if not webhook_url:
            print("⚠️ STARTUPAI_WEBHOOK_URL not configured, skipping persistence")
            return False

        if not bearer_token:
            print("⚠️ STARTUPAI_WEBHOOK_BEARER_TOKEN not configured, skipping persistence")
            return False

        if not self.state.user_id:
            print("⚠️ No user_id provided, skipping persistence")
            return False

        # Build payload with flow_type for unified webhook
        payload = {
            "flow_type": "consultant_onboarding",
            "consultant_id": self.state.user_id,
            "session_id": self.state.session_id,
            "practice_analysis": self.state.practice_analysis,
            "recommendations": self.state.recommendations,
            "onboarding_tips": self.state.onboarding_tips,
            "suggested_templates": self.state.suggested_templates,
            "suggested_workflows": self.state.suggested_workflows,
            "white_label_suggestions": self.state.white_label_config_suggestions,
            "completed_at": datetime.now().isoformat(),
        }

        try:
            print(f"\n📤 Persisting consultant onboarding results...")
            print(f"   Webhook: {webhook_url}")
            print(f"   Consultant: {self.state.user_id}")

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
                print("✅ Consultant onboarding results persisted successfully")
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


# =======================================================================================
# FLOW INITIALIZATION
# =======================================================================================

def create_consultant_onboarding_flow(
    user_id: str,
    session_id: str,
    practice_data: Dict[str, Any],
    conversation_summary: str = "",
) -> ConsultantOnboardingFlow:
    """
    Factory function to create and initialize a consultant onboarding flow.

    Args:
        user_id: UUID of the consultant in the product app
        session_id: Onboarding session ID
        practice_data: Practice data collected during onboarding
        conversation_summary: Optional summary of the onboarding conversation

    Returns:
        Configured ConsultantOnboardingFlow ready to run
    """
    # Generate a unique flow ID
    flow_id = f"consultant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Convert practice_data dict to ConsultantPracticeData
    practice = ConsultantPracticeData(
        company_name=practice_data.get("company_name", ""),
        practice_size=practice_data.get("practice_size", "solo"),
        current_clients=practice_data.get("current_clients", 0),
        industries=practice_data.get("industries", []),
        services=practice_data.get("services", []),
        tools_used=practice_data.get("tools_used", []),
        pain_points=practice_data.get("pain_points", ""),
        white_label_enabled=practice_data.get("white_label_enabled", False),
        goals=practice_data.get("goals", {}),
    )

    # Create flow with state values
    flow = ConsultantOnboardingFlow(
        id=flow_id,
        user_id=user_id,
        session_id=session_id,
        practice_data=practice.model_dump(),
        conversation_summary=conversation_summary,
    )

    return flow
