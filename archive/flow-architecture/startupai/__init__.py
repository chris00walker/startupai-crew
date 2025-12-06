"""
StartupAI CrewAI Backend Package
Evidence-Led Strategy Platform

This package implements the CrewAI orchestration for Value Proposition Design
using a 6-agent system with specialized roles.

Pure LLM-based implementation - no external tools required.
"""

__version__ = "1.0.0"
__author__ = "StartupAI"

try:
    from .crew import StartupAICrew
except ImportError:
    from startupai.crew import StartupAICrew

__all__ = [
    "StartupAICrew",
]
