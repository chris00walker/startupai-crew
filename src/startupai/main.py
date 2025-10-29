#!/usr/bin/env python3
"""
StartupAI CrewAI CLI Entry Point
Command-line interface for running strategic analysis workflows
"""

import sys
import os
import json
import argparse
from typing import Dict, Any
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.startupai.crew import StartupAICrew


def load_environment():
    """Load environment variables from .env file."""
    # Skip loading .env if direnv is already providing environment variables
    if os.getenv('SKIP_DOTENV') or os.getenv('DIRENV_DIR'):
        print("✅ Using system environment variables (direnv detected)")
        return
        
    try:
        from dotenv import load_dotenv
        env_path = backend_dir / ".env"
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
    except Exception as e:
        print(f"⚠️  Failed to load .env: {e}")
        print("Continuing with system environment variables...")


def validate_inputs(inputs: Dict[str, Any]) -> bool:
    """
    Validate required inputs for crew execution.
    
    Args:
        inputs: Input dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "strategic_question",
        "project_context",
        "project_id",
    ]
    
    for field in required_fields:
        if field not in inputs or not inputs[field]:
            print(f"❌ Missing required field: {field}")
            return False
    
    return True


def run_analysis(
    strategic_question: str,
    project_id: str,
    project_context: str = "",
    target_sources: str = "",
    report_format: str = "markdown",
    project_deadline: str = "",
    priority_level: str = "medium",
) -> Dict[str, Any]:
    """
    Run strategic analysis using StartupAI crew.
    
    Args:
        strategic_question: The strategic question to analyze
        project_id: Project UUID for storing evidence
        project_context: Additional context about the project
        target_sources: Comma-separated list of target sources
        report_format: Format for generated report (markdown, html, pdf)
        project_deadline: Target completion date
        priority_level: Analysis priority (low, medium, high)
        
    Returns:
        Dictionary with analysis results
    """
    print("\n" + "=" * 80)
    print("StartupAI Evidence-Led Strategy Analysis")
    print("=" * 80)
    print(f"Question: {strategic_question}")
    print(f"Project ID: {project_id}")
    print(f"Priority: {priority_level}")
    print("=" * 80 + "\n")
    
    # Prepare inputs
    inputs = {
        "strategic_question": strategic_question,
        "project_id": project_id,
        "project_context": project_context or "No additional context provided",
        "target_sources": target_sources or "General web sources",
        "report_format": report_format,
        "project_deadline": project_deadline or "Not specified",
        "priority_level": priority_level,
    }
    
    # Validate inputs
    if not validate_inputs(inputs):
        return {"error": "Invalid inputs", "status": "failed"}
    
    try:
        # Initialize and run crew
        print("🚀 Initializing StartupAI Crew...")
        crew = StartupAICrew()
        
        print("🔄 Starting analysis workflow...")
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "=" * 80)
        print("✅ Analysis Complete!")
        print("=" * 80)
        
        return {
            "status": "success",
            "result": result,
            "inputs": inputs,
        }
    
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "error": str(e),
            "inputs": inputs,
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="StartupAI Evidence-Led Strategy Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic analysis
  python main.py --question "What is our competitive position?" --project-id "abc-123"
  
  # Run with full context
  python main.py \\
    --question "Should we enter the European market?" \\
    --project-id "project-uuid" \\
    --context "B2B SaaS company, $5M ARR" \\
    --sources "G2, Gartner, Forrester" \\
    --format html \\
    --priority high
        """
    )
    
    # Required arguments
    parser.add_argument(
        "-q", "--question",
        required=True,
        help="Strategic question to analyze"
    )
    parser.add_argument(
        "-p", "--project-id",
        required=True,
        help="Project UUID for storing evidence"
    )
    
    # Optional arguments
    parser.add_argument(
        "-c", "--context",
        default="",
        help="Additional project context"
    )
    parser.add_argument(
        "-s", "--sources",
        default="",
        help="Target sources for research (comma-separated)"
    )
    parser.add_argument(
        "-f", "--format",
        default="markdown",
        choices=["markdown", "html", "pdf"],
        help="Report output format"
    )
    parser.add_argument(
        "-d", "--deadline",
        default="",
        help="Project deadline (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--priority",
        default="medium",
        choices=["low", "medium", "high"],
        help="Analysis priority level"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for results (JSON format)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_environment()
    
    # Run analysis
    result = run_analysis(
        strategic_question=args.question,
        project_id=args.project_id,
        project_context=args.context,
        target_sources=args.sources,
        report_format=args.format,
        project_deadline=args.deadline,
        priority_level=args.priority,
    )
    
    # Output results
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_path}")
    
    if args.verbose:
        print("\n📊 Full Results:")
        print(json.dumps(result, indent=2, default=str))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
