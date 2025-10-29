"""
StartupAI CrewAI Backend Package
Evidence-Led Strategy Platform

This package implements the CrewAI orchestration for strategic analysis
using a multi-agent system with specialized roles.
"""

__version__ = "0.1.0"
__author__ = "StartupAI"

try:
    from .crew import StartupAICrew
    from .tools import (
        EvidenceStoreTool,
        VectorSearchTool,
        WebSearchTool,
        ReportGeneratorTool,
    )
except ImportError:
    from startupai.crew import StartupAICrew
    from startupai.tools import (
        EvidenceStoreTool,
        VectorSearchTool,
        WebSearchTool,
        ReportGeneratorTool,
    )

__all__ = [
    "StartupAICrew",
    "EvidenceStoreTool",
    "VectorSearchTool",
    "WebSearchTool",
    "ReportGeneratorTool",
]
