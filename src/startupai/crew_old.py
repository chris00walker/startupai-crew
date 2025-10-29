"""
StartupAI CrewAI Crew Orchestration
Coordinates multiple specialized agents for evidence-led strategic analysis
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
from crewai import Agent, Task, Crew, Process

try:
    from .tools import (
        EvidenceStoreTool,
        VectorSearchTool,
        WebSearchTool,
        ReportGeneratorTool,
    )
except ImportError:
    from startupai.tools import (
        EvidenceStoreTool,
        VectorSearchTool,
        WebSearchTool,
        ReportGeneratorTool,
    )


class StartupAICrew:
    """
    StartupAI Evidence-Led Strategy Crew
    
    Coordinates 6 specialized agents for comprehensive strategic analysis:
    1. Research Agent - Evidence discovery and collection
    2. Analysis Agent - Pattern recognition and insight extraction
    3. Validation Agent - Evidence quality and credibility verification
    4. Synthesis Agent - Insight combination and narrative building
    5. Reporting Agent - Professional report generation
    6. Orchestration Agent - Workflow coordination
    """
    
    # Configuration file paths
    agents_config: str = "config/agents.yaml"
    tasks_config: str = "config/tasks.yaml"
    
    def __init__(self):
        """Initialize the crew with tools and configurations."""
        self.tools = self._initialize_tools()
        self.agents_data = self._load_config(self.agents_config)
        self.tasks_data = self._load_config(self.tasks_config)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        # Try multiple path resolution strategies
        backend_dir = Path(__file__).parent.parent.parent
        full_path = backend_dir / config_path
        
        # If not found, try from current working directory
        if not full_path.exists():
            full_path = Path.cwd() / config_path
        
        # If still not found, try relative to backend directory
        if not full_path.exists():
            # Resolve to absolute path
            backend_dir = Path(__file__).resolve().parent.parent.parent
            full_path = backend_dir / config_path
        
        if not full_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Tried: {full_path}\n"
                f"Current dir: {Path.cwd()}\n"
                f"File location: {Path(__file__)}"
            )
        
        with open(full_path, "r") as f:
            return yaml.safe_load(f)
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all custom tools for the crew."""
        return {
            "evidence_store": EvidenceStoreTool(),
            "vector_search": VectorSearchTool(),
            "web_search": WebSearchTool(),
            "report_generator": ReportGeneratorTool(),
        }
    
    def research_agent(self) -> Agent:
        """Create the Research Coordinator agent."""
        config = self.agents_data["research_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=config.get("llm"),  # Optional: specify model (e.g., "gpt-4", "claude-3-opus")
            tools=[
                self.tools["web_search"],
                self.tools["evidence_store"],
            ],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", True),
            max_iter=config.get("max_iter", 10),
        )
    
    def analysis_agent(self) -> Agent:
        """Create the Strategic Analyst agent."""
        config = self.agents_data["analysis_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[
                self.tools["evidence_store"],
                self.tools["vector_search"],
            ],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", True),
            max_iter=config.get("max_iter", 10),
        )
    
    def validation_agent(self) -> Agent:
        """Create the Evidence Validator agent."""
        config = self.agents_data["validation_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[
                self.tools["web_search"],
                self.tools["evidence_store"],
            ],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 5),
        )
    
    def synthesis_agent(self) -> Agent:
        """Create the Strategic Synthesizer agent."""
        config = self.agents_data["synthesis_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[
                self.tools["evidence_store"],
            ],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 8),
        )
    
    def reporting_agent(self) -> Agent:
        """Create the Report Generator agent."""
        config = self.agents_data["reporting_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[
                self.tools["evidence_store"],
                self.tools["report_generator"],
            ],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 5),
        )
    
    def orchestration_agent(self) -> Agent:
        """Create the Workflow Orchestrator agent."""
        config = self.agents_data["orchestration_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[
                self.tools["evidence_store"],
            ],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", True),
            max_iter=config.get("max_iter", 15),
        )
    
    def evidence_collection_task(self) -> Task:
        """Create the evidence collection task."""
        config = self.tasks_data["evidence_collection"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.research_agent(),
        )
    
    def evidence_analysis_task(self) -> Task:
        """Create the evidence analysis task."""
        config = self.tasks_data["evidence_analysis"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.analysis_agent(),
        )
    
    def evidence_validation_task(self) -> Task:
        """Create the evidence validation task."""
        config = self.tasks_data["evidence_validation"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.validation_agent(),
        )
    
    def insight_synthesis_task(self) -> Task:
        """Create the insight synthesis task."""
        config = self.tasks_data["insight_synthesis"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.synthesis_agent(),
        )
    
    def report_generation_task(self) -> Task:
        """Create the report generation task."""
        config = self.tasks_data["report_generation"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.reporting_agent(),
        )
    
    def workflow_orchestration_task(self) -> Task:
        """Create the workflow orchestration task."""
        config = self.tasks_data["workflow_orchestration"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.orchestration_agent(),
        )
    
    def create_crew(self) -> Crew:
        """
        Create and configure the StartupAI Crew.
        
        Uses sequential process for reliable execution.
        """
        crew = Crew(
            agents=[
                self.research_agent(),
                self.analysis_agent(),
                self.validation_agent(),
                self.synthesis_agent(),
                self.reporting_agent(),
            ],
            tasks=[
                self.evidence_collection_task(),
                self.evidence_analysis_task(),
                self.evidence_validation_task(),
                self.insight_synthesis_task(),
                self.report_generation_task(),
            ],
            process=Process.sequential,  # Use sequential for testing
            verbose=True,
        )
        return crew
    
    def crew(self) -> Crew:
        """
        Get the configured crew (alias for create_crew).
        CrewAI AMP expects this method name.
        
        Returns:
            Configured Crew instance
        """
        return self.create_crew()
    
    def kickoff(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start the crew execution with given inputs.
        
        Args:
            inputs: Dictionary with strategic_question, project_context, etc.
        
        Returns:
            Results from crew execution
        """
        crew = self.create_crew()
        return crew.kickoff(inputs=inputs)
