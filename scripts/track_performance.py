#!/usr/bin/env python3
"""
Track CrewAI test performance metrics over time.

This script runs `crewai test` and captures performance metrics,
storing them in metrics/performance_history.json for trend analysis.

Usage:
    python scripts/track_performance.py --iterations 3 --model gpt-4o-mini
    python scripts/track_performance.py -n 5 -m gpt-4o --threshold 7.0
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


METRICS_DIR = Path(__file__).parent / "metrics"
HISTORY_FILE = METRICS_DIR / "performance_history.json"


def run_crewai_test(iterations: int, model: str) -> tuple[str, int]:
    """Run crewai test and return output and return code."""
    cmd = ["crewai", "test", "-n", str(iterations), "-m", model]
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    return output, result.returncode


def parse_metrics(output: str) -> dict:
    """Parse crewai test output for scores and timing."""
    metrics = {
        "task_scores": [],
        "average_score": None,
        "execution_times": [],
        "average_time": None,
    }

    # Parse task scores (format: "Task Name | 8.5 | 9.0 | 8.75")
    score_pattern = r"([A-Za-z_\s]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)"
    for match in re.finditer(score_pattern, output):
        task_name = match.group(1).strip()
        avg_score = float(match.group(4))
        metrics["task_scores"].append({"task": task_name, "average": avg_score})

    # Parse overall average score
    overall_pattern = r"(?:Overall|Crew)\s+(?:Score|Average)[:\s]+([\d.]+)"
    overall_match = re.search(overall_pattern, output, re.IGNORECASE)
    if overall_match:
        metrics["average_score"] = float(overall_match.group(1))
    elif metrics["task_scores"]:
        # Calculate from task scores if not explicitly provided
        metrics["average_score"] = sum(t["average"] for t in metrics["task_scores"]) / len(metrics["task_scores"])

    # Parse execution times (format: "Execution time: 45.2s")
    time_pattern = r"(?:Execution\s+time|Time)[:\s]+([\d.]+)\s*s"
    for match in re.finditer(time_pattern, output, re.IGNORECASE):
        metrics["execution_times"].append(float(match.group(1)))

    if metrics["execution_times"]:
        metrics["average_time"] = sum(metrics["execution_times"]) / len(metrics["execution_times"])

    return metrics


def load_history() -> list[dict]:
    """Load existing performance history."""
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def save_history(history: list[dict]) -> None:
    """Save performance history to file."""
    METRICS_DIR.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Track CrewAI test performance metrics")
    parser.add_argument("-n", "--iterations", type=int, default=3, help="Number of test iterations")
    parser.add_argument("-m", "--model", default="gpt-4o-mini", help="Model to use for testing")
    parser.add_argument("--threshold", type=float, default=7.0, help="Minimum average score to pass")
    parser.add_argument("--dry-run", action="store_true", help="Parse output without running tests")
    args = parser.parse_args()

    if args.dry_run:
        # For testing the parser
        sample_output = sys.stdin.read()
        metrics = parse_metrics(sample_output)
        print(json.dumps(metrics, indent=2))
        return 0

    # Run the tests
    output, return_code = run_crewai_test(args.iterations, args.model)
    print(output)

    if return_code != 0:
        print(f"\nError: crewai test failed with return code {return_code}")
        return 1

    # Parse metrics
    metrics = parse_metrics(output)

    if metrics["average_score"] is None:
        print("\nWarning: Could not parse average score from output")
        print("Raw metrics:", json.dumps(metrics, indent=2))
        return 1

    # Record results
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "iterations": args.iterations,
        "model": args.model,
        "average_score": metrics["average_score"],
        "average_time": metrics["average_time"],
        "task_scores": metrics["task_scores"],
    }

    # Save to history
    history = load_history()
    history.append(record)
    save_history(history)
    print(f"\nMetrics saved to {HISTORY_FILE}")

    # Check threshold
    if metrics["average_score"] < args.threshold:
        print(f"\nFailed: Average score {metrics['average_score']:.2f} is below threshold {args.threshold}")
        return 1

    print(f"\nPassed: Average score {metrics['average_score']:.2f} meets threshold {args.threshold}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
