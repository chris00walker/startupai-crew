#!/usr/bin/env python
"""
StartupAI Validation Crew - Main Entry Point

This crew receives intake data from Crew 1 and executes validation experiments.
"""

import sys
from validation_crew.crew import ValidationCrew


def run():
    """Run the Validation Crew with sample inputs from Crew 1."""
    inputs = {
        # Input from Crew 1 (Intake)
        "entrepreneur_brief": {
            "business_idea": "AI-powered startup validation platform",
            "target_customers": ["Early-stage founders", "Innovation consultants"],
            "problem_statement": "Traditional validation is slow and expensive",
            "proposed_solution": "Automated validation with AI crews",
            "key_hypotheses": [
                {"hypothesis": "Founders will pay for faster validation", "risk_level": "medium"},
                {"hypothesis": "AI can replace manual research", "risk_level": "high"},
            ],
        },
        "customer_profile": {
            "segment_name": "Early-stage founders",
            "jobs_to_be_done": {
                "functional": ["Validate business idea", "Get investor-ready"],
                "emotional": ["Feel confident in decisions"],
                "social": ["Be seen as a smart founder"],
            },
            "pains": ["Validation takes too long", "Expensive consultants"],
            "gains": ["Faster time to market", "Lower risk of failure"],
        },
        "value_proposition_canvas": {
            "customer_profile": "Early-stage founders seeking validation",
            "value_map": {
                "products_services": ["AI validation platform"],
                "pain_relievers": ["24-hour validation vs 4 weeks"],
                "gain_creators": ["Data-driven confidence"],
            },
        },
    }
    ValidationCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew for a given number of iterations."""
    inputs = {"entrepreneur_brief": "Sample brief for training"}
    try:
        ValidationCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        ValidationCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and return results."""
    inputs = {"entrepreneur_brief": "Sample brief for testing"}
    try:
        ValidationCrew().crew().test(
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
