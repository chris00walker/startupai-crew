#!/usr/bin/env python
"""
Main entry point for StartupAI Internal Validation Flow.

This module provides the required entry points for CrewAI AMP deployment:
- kickoff(inputs): Main execution entry point
- plot(): Flow visualization generator
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from startupai.flows import create_validation_flow, InternalValidationFlow


def kickoff(inputs: dict = None):
    """
    Main entry point for CrewAI AMP deployment.

    This function is called when the flow is triggered via the AMP API.

    Args:
        inputs: Dictionary containing flow inputs. Expected keys:
            - entrepreneur_input: The business idea description (required)
            - project_id: UUID of project in product app (optional, for persistence)
            - user_id: UUID of user in product app (optional, for persistence)
            - session_id: Onboarding session ID (optional, for brief linking)
            - kickoff_id: CrewAI kickoff ID (optional, for tracking)

    Returns:
        Flow execution result with validation report
    """
    # Load environment variables (for local development)
    load_dotenv()

    # Handle inputs
    if inputs is None:
        inputs = {}

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

    # Verify OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "error": "OPENAI_API_KEY not found in environment variables",
            "status": "failed"
        }

    print("=" * 80)
    print("STARTUPAI INTERNAL VALIDATION SYSTEM")
    print("Innovation Physics Flow Engine v1.0")
    print("=" * 80)
    print(f"\n📋 Business Idea Submitted ({len(entrepreneur_input)} chars)")
    if project_id:
        print(f"📁 Project: {project_id}")
    if user_id:
        print(f"👤 User: {user_id}")

    # Create the validation flow with context for persistence
    print("\n🚀 Initializing validation flow with Innovation Physics logic...")
    flow = create_validation_flow(
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

    flow = InternalValidationFlow(initial_state=initial_state)
    flow.plot("startupai_validation_flow")
    print("✅ Flow visualization saved to startupai_validation_flow.png")


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
