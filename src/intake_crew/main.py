#!/usr/bin/env python
"""
StartupAI Intake Crew - Main Entry Point

This is the entry point for running the Intake Crew locally.
"""

import sys
from intake_crew.crew import IntakeCrew


def run():
    """Run the Intake Crew with sample inputs."""
    inputs = {
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
        An AI-powered platform with specialized crews that conduct customer research,
        competitive analysis, and validation experiments automatically.
        """
    }
    IntakeCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        "entrepreneur_input": "Sample business idea for training"
    }
    try:
        IntakeCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        IntakeCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and return results."""
    inputs = {
        "entrepreneur_input": "Sample business idea for testing"
    }
    try:
        IntakeCrew().crew().test(
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
