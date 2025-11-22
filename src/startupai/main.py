"""
Main entry point for StartupAI Internal Validation Flow.

This demonstrates how to use the Innovation Physics flow logic
to validate a startup idea through the three phases.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from startupai.flows import create_validation_flow, ValidationState


def main():
    """Run the internal validation flow with StartupAI's own business idea."""

    # Load environment variables
    load_dotenv()

    # Verify OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or environment")
        return

    # StartupAI's own business idea for internal validation
    entrepreneur_input = """
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
    competitive analysis, and validation experiments automatically. We deliver a
    complete Value Proposition Canvas, validated assumptions, and strategic
    recommendations in 1 hour for <$100.

    Key Assumptions to Test:
    1. Founders will trust AI-generated validation insights
    2. The pain of slow/expensive validation is severe enough to pay for
    3. AI can match or exceed human consultant quality for validation
    4. The market is large enough (enough founders need this)
    5. We can deliver results in 1 hour with sufficient quality
    """

    print("=" * 80)
    print("STARTUPAI INTERNAL VALIDATION SYSTEM")
    print("Innovation Physics Flow Engine v1.0")
    print("=" * 80)
    print("\n📋 Business Idea Submitted:")
    print(entrepreneur_input[:300] + "...\n")

    # Create the validation flow
    print("🚀 Initializing validation flow with Innovation Physics logic...")
    flow = create_validation_flow(entrepreneur_input)

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

        if hasattr(result, 'final_recommendation'):
            print(f"\n📊 Final Recommendation: {result.final_recommendation}")

        if hasattr(result, 'pivot_recommendation'):
            print(f"🔄 Pivot Recommendation: {result.pivot_recommendation}")

        if hasattr(result, 'evidence_summary'):
            print("\n📈 Evidence Summary:")
            for key, value in result.evidence_summary.items():
                print(f"  • {key}: {value}")

        if hasattr(result, 'next_steps'):
            print("\n📝 Next Steps:")
            for i, step in enumerate(result.next_steps, 1):
                print(f"  {i}. {step}")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"validation_results_{timestamp}.json"

        print(f"\n💾 Results saved to: {output_file}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        return
    except Exception as e:
        print(f"\n❌ Error during validation: {str(e)}")
        raise

    print("\n✅ Validation flow completed successfully!")
    print("\n" + "=" * 80)
    print("Innovation Physics: Evidence drives iteration, not intuition.")
    print("=" * 80)


if __name__ == "__main__":
    main()