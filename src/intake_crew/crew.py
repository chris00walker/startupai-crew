"""
StartupAI Intake Crew - Crew 1 of 3

This crew handles the intake phase of the StartupAI validation pipeline:
1. Parse founder input into structured brief
2. Research customer segments using JTBD methodology
3. Create Value Proposition Canvas
4. QA gate with human approval
5. Trigger Crew 2 (Validation Engine)

Agents: S1 (FounderOnboarding), S2 (CustomerResearch), S3 (ValueDesigner), G1 (QA)
"""

import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import InvokeCrewAIAutomationTool

from intake_crew.tools.web_search import TavilySearchTool, CustomerResearchTool
from intake_crew.tools.methodology_check import MethodologyCheckTool
from intake_crew.schemas import (
    FounderBrief,
    CustomerResearchOutput,
    ValuePropositionCanvas,
    QAGateOutput,
    HumanApprovalInput,
    CrewInvocationResult,
)

# Instantiate research tools for S2 agent
# Requires TAVILY_API_KEY environment variable
tavily_search = TavilySearchTool()
customer_research = CustomerResearchTool()

# Instantiate methodology check tool for G1 agent
# Validates VPC structure against Strategyzer methodology
methodology_check = MethodologyCheckTool()

# Create invoker for Crew 2 (Validation Engine)
# Environment variables must be set in AMP dashboard
validation_crew_invoker = InvokeCrewAIAutomationTool(
    crew_api_url=os.getenv("CREW_2_URL", ""),
    crew_bearer_token=os.getenv("CREW_2_BEARER_TOKEN", ""),
    crew_name="Validation Crew",
    crew_description="12-agent D/F/V validation engine for startup ideas",
)


@CrewBase
class IntakeCrew:
    """StartupAI Intake Crew - Parse input, research, create VPC, QA gate."""

    # Agent definitions
    @agent
    def founder_onboarding_agent(self) -> Agent:
        """S1: Convert raw founder input into structured brief."""
        return Agent(
            config=self.agents_config["founder_onboarding_agent"],
            tools=[],  # Will add InvokeCrewAIAutomationTool for trigger task
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(
                model="openai/gpt-4o",
                temperature=0.7,
            ),
        )

    @agent
    def customer_research_agent(self) -> Agent:
        """S2: Research customer segments using JTBD methodology."""
        return Agent(
            config=self.agents_config["customer_research_agent"],
            tools=[tavily_search, customer_research],  # Web search + customer research
            reasoning=True,  # Enabled for thorough research synthesis
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(
                model="openai/gpt-4o",
                temperature=0.7,
            ),
        )

    @agent
    def value_designer_agent(self) -> Agent:
        """S3: Construct Value Proposition Canvas."""
        return Agent(
            config=self.agents_config["value_designer_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(
                model="openai/gpt-4o",
                temperature=0.7,
            ),
        )

    @agent
    def qa_agent(self) -> Agent:
        """G1: Quality assurance and human approval gate + trigger Crew 2."""
        return Agent(
            config=self.agents_config["qa_agent"],
            tools=[methodology_check, validation_crew_invoker],  # VPC validation + Crew 2 invoke
            reasoning=True,  # Enabled for rigorous QA decisions
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(
                model="openai/gpt-4o",
                temperature=0.7,
            ),
        )

    # Task definitions - each with Pydantic output schema for structured validation
    @task
    def parse_founder_input(self) -> Task:
        """Parse entrepreneur_input into structured brief."""
        return Task(
            config=self.tasks_config["parse_founder_input"],
            output_pydantic=FounderBrief,
            markdown=False,
        )

    @task
    def research_customer_problem(self) -> Task:
        """Research customer segments using JTBD."""
        return Task(
            config=self.tasks_config["research_customer_problem"],
            output_pydantic=CustomerResearchOutput,
            markdown=False,
        )

    @task
    def create_value_proposition_canvas(self) -> Task:
        """Build complete VPC from brief and customer profile."""
        return Task(
            config=self.tasks_config["create_value_proposition_canvas"],
            output_pydantic=ValuePropositionCanvas,
            markdown=False,
        )

    @task
    def qa_gate_intake(self) -> Task:
        """Review all outputs for quality and completeness."""
        return Task(
            config=self.tasks_config["qa_gate_intake"],
            output_pydantic=QAGateOutput,
            markdown=False,
        )

    @task
    def approve_intake_to_validation(self) -> Task:
        """HITL: Present summary to human for approval."""
        return Task(
            config=self.tasks_config["approve_intake_to_validation"],
            output_pydantic=HumanApprovalInput,
            markdown=False,
            human_input=True,  # This triggers HITL in AMP
        )

    @task
    def trigger_validation_crew(self) -> Task:
        """Invoke Crew 2 with intake outputs."""
        return Task(
            config=self.tasks_config["trigger_validation_crew"],
            output_pydantic=CrewInvocationResult,
            markdown=False,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StartupAI Intake crew."""
        return Crew(
            agents=self.agents,  # Automatically created by @agent decorator
            tasks=self.tasks,  # Automatically created by @task decorator
            process=Process.sequential,
            verbose=True,
        )
