#!/usr/bin/env python
"""
Main entry point for StartupAI CrewAI Flows.

This module provides the required entry points for CrewAI AMP deployment:
- kickoff(inputs): Main execution entry point (supports multiple flow types)
- plot(): Flow visualization generator

Supported Flow Types:
- "founder_validation" (default): Full business idea validation
- "consultant_onboarding": Consultant practice analysis and recommendations
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from startupai.flows import (
    FounderValidationFlow,
    create_founder_validation_flow,
    ConsultantOnboardingFlow,
    create_consultant_onboarding_flow,
)


def kickoff(inputs: dict = None):
    """
    Main entry point for CrewAI AMP deployment.

    This function is called when the flow is triggered via the AMP API.
    It supports multiple flow types via the 'flow_type' input parameter.

    Args:
        inputs: Dictionary containing flow inputs.

        For founder_validation (default):
            - entrepreneur_input: The business idea description (required)
            - project_id: UUID of project in product app (optional)
            - user_id: UUID of user in product app (optional)
            - session_id: Onboarding session ID (optional)
            - kickoff_id: CrewAI kickoff ID (optional)

        For consultant_onboarding:
            - flow_type: "consultant_onboarding" (required to select this flow)
            - user_id: UUID of consultant (required)
            - session_id: Onboarding session ID (required)
            - practice_data: Dict with practice info (required)
            - conversation_summary: Optional summary of onboarding chat

    Returns:
        Flow execution result
    """
    # Load environment variables (for local development)
    load_dotenv()

    # Handle inputs
    if inputs is None:
        inputs = {}

    # Determine flow type
    flow_type = inputs.get("flow_type", "founder_validation")

    # Debug logging for flow routing
    print(f"[ROUTING] Received flow_type: '{flow_type}'")
    print(f"[ROUTING] Full inputs keys: {list(inputs.keys())}")
    print(f"[ROUTING] Routing to: {'consultant_onboarding' if flow_type == 'consultant_onboarding' else 'founder_validation'}")

    # Verify OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "error": "OPENAI_API_KEY not found in environment variables",
            "status": "failed"
        }

    # Route to appropriate flow
    if flow_type == "consultant_onboarding":
        return _run_consultant_onboarding(inputs)
    else:
        return _run_founder_validation(inputs)


def _run_founder_validation(inputs: dict):
    """Run the founder validation flow."""
    entrepreneur_input = inputs.get("entrepreneur_input", "")

    if not entrepreneur_input:
        return {
            "error": "Missing required input: entrepreneur_input",
            "status": "failed"
        }

    # Extract optional context for persistence
    project_id = inputs.get("project_id")
    user_id = inputs.get("user_id")
    session_id = inputs.get("session_id")
    kickoff_id = inputs.get("kickoff_id")

    print("=" * 80)
    print("STARTUPAI INTERNAL VALIDATION SYSTEM")
    print("Innovation Physics Flow Engine v1.0")
    print("=" * 80)
    print(f"\n📋 Business Idea Submitted ({len(entrepreneur_input)} chars)")
    if project_id:
        print(f"📁 Project: {project_id}")
    if user_id:
        print(f"👤 User: {user_id}")

    # Create the founder validation flow with context for persistence
    print("\n🚀 Initializing founder validation flow with Innovation Physics logic...")
    flow = create_founder_validation_flow(
        entrepreneur_input=entrepreneur_input,
        project_id=project_id,
        user_id=user_id,
        session_id=session_id,
        kickoff_id=kickoff_id,
    )

    # Run the flow
    print("\n▶️  Starting validation process...")
    print("This will proceed through three gated phases:")
    print("  1. DESIRABILITY - Do customers want this?")
    print("  2. FEASIBILITY - Can we build it?")
    print("  3. VIABILITY - Can we make money?")
    print("\n" + "=" * 80)

    try:
        # Execute the flow
        result = flow.kickoff()

        # Display results
        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)

        if isinstance(result, dict):
            if result.get('validation_report'):
                report = result['validation_report']
                print(f"\n📊 Final Recommendation: {report.get('validation_outcome', 'N/A')}")
                print(f"🔄 Pivot Recommendation: {report.get('pivot_recommendation', 'N/A')}")

                if report.get('next_steps'):
                    print("\n📝 Next Steps:")
                    for i, step in enumerate(report['next_steps'], 1):
                        print(f"  {i}. {step}")

        print("\n✅ Validation flow completed successfully!")
        print("\n" + "=" * 80)
        print("Innovation Physics: Evidence drives iteration, not intuition.")
        print("=" * 80)

        return result

    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        return {"error": "Interrupted", "status": "cancelled"}
    except Exception as e:
        print(f"\n❌ Error during validation: {str(e)}")
        return {"error": str(e), "status": "failed"}


def _run_consultant_onboarding(inputs: dict):
    """Run the consultant onboarding flow."""
    user_id = inputs.get("user_id")
    session_id = inputs.get("session_id")
    practice_data = inputs.get("practice_data", {})
    conversation_summary = inputs.get("conversation_summary", "")

    if not user_id:
        return {
            "error": "Missing required input: user_id",
            "status": "failed"
        }

    if not session_id:
        return {
            "error": "Missing required input: session_id",
            "status": "failed"
        }

    print("=" * 80)
    print("STARTUPAI CONSULTANT ONBOARDING")
    print("Practice Analysis & Recommendations Engine")
    print("=" * 80)
    print(f"\n👤 Consultant: {user_id}")
    print(f"📋 Session: {session_id}")
    if practice_data.get("company_name"):
        print(f"🏢 Practice: {practice_data.get('company_name')}")

    # Create the consultant onboarding flow
    print("\n🚀 Initializing consultant onboarding flow...")
    flow = create_consultant_onboarding_flow(
        user_id=user_id,
        session_id=session_id,
        practice_data=practice_data,
        conversation_summary=conversation_summary,
    )

    # Run the flow
    print("\n▶️  Starting practice analysis...")
    print("This will:")
    print("  1. Analyze your practice strengths and opportunities")
    print("  2. Generate personalized platform recommendations")
    print("  3. Suggest templates and workflows for your clients")
    print("\n" + "=" * 80)

    try:
        # Execute the flow
        result = flow.kickoff()

        # Display results
        print("\n" + "=" * 80)
        print("CONSULTANT ONBOARDING COMPLETE")
        print("=" * 80)

        if isinstance(result, dict):
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("\n💡 Platform Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"  {i}. {rec}")

        print("\n✅ Consultant onboarding flow completed successfully!")
        print("=" * 80)

        return result

    except KeyboardInterrupt:
        print("\n\n⚠️  Onboarding interrupted by user")
        return {"error": "Interrupted", "status": "cancelled"}
    except Exception as e:
        print(f"\n❌ Error during onboarding: {str(e)}")
        return {"error": str(e), "status": "failed"}


def plot():
    """
    Generate flow visualization.

    This function is called by `crewai flow plot` command to generate
    a visual representation of the flow structure.
    """
    from startupai.flows.state_schemas import ValidationState

    # Create flow instance for plotting
    initial_state = ValidationState(
        id="plot_preview",
        timestamp_created=datetime.now(),
        timestamp_updated=datetime.now(),
        entrepreneur_input=""
    )

    flow = FounderValidationFlow(initial_state=initial_state)
    flow.plot("founder_validation_flow")
    print("✅ Flow visualization saved to founder_validation_flow.png")


# For local testing
if __name__ == "__main__":
    # Example input for local testing
    test_inputs = {
        "entrepreneur_input": """
        StartupAI is an AI-powered startup validation platform that helps founders and
        innovation consultants validate their business ideas in hours instead of weeks.

        Target Customers:
        1. Early-stage founders who need to validate ideas quickly before building
        2. Innovation consultants who want to deliver faster, data-driven validation

        Problem Statement:
        Traditional validation takes 2-4 weeks and costs $3-10K through consultants,
        or requires 80+ hours using a complex tool stack. Founders often build products
        nobody wants because they skip proper validation.

        Our Solution:
        An AI-powered platform with 8 specialized crews that conduct customer research,
        competitive analysis, and validation experiments automatically.
        """
    }

    result = kickoff(test_inputs)
    print("\nFinal Result:", result)
