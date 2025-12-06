#!/usr/bin/env python
"""
StartupAI Decision Crew - Main Entry Point

This crew receives validation results from Crew 2 and facilitates the final decision.
"""

import sys
from decision_crew.crew import DecisionCrew


def run():
    """Run the Decision Crew with sample inputs from Crew 2."""
    inputs = {
        # Input from Crew 2 (Validation)
        "desirability_signal": {
            "classification": "STRONG_COMMITMENT",
            "metrics": {
                "ctr": 4.2,
                "conversion_rate": 3.1,
                "cpa": 28.50,
                "zombie_ratio": 0.25,
            },
            "confidence": "HIGH",
        },
        "feasibility_assessment": {
            "status": "GREEN",
            "tech_stack": ["Next.js", "Supabase", "CrewAI"],
            "effort_estimate": "M",
            "risks": [
                {"risk": "LLM rate limits at scale", "severity": "medium"},
            ],
        },
        "viability_metrics": {
            "cac": 35.00,
            "ltv": 420.00,
            "ltv_cac_ratio": 12.0,
            "payback_months": 2,
            "status": "PROFITABLE",
            "confidence": "MEDIUM",
        },
        "learnings": {
            "validated_hypotheses": [
                "Founders value speed over depth",
                "Consultants want white-label option",
            ],
            "invalidated_hypotheses": [
                "Enterprise buyers were not interested",
            ],
            "surprising_findings": [
                "High conversion from Twitter ads vs LinkedIn",
            ],
        },
    }
    DecisionCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew for a given number of iterations."""
    inputs = {"desirability_signal": "Sample signal for training"}
    try:
        DecisionCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        DecisionCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and return results."""
    inputs = {"desirability_signal": "Sample signal for testing"}
    try:
        DecisionCrew().crew().test(
            n_iterations=int(sys.argv[1]),
            openai_model_name=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        print("Commands: run, train, replay, test")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
