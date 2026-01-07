"""
StartupAI Decision Crew - Crew 3 of 3

This crew handles the final decision phase:
1. Synthesize evidence from validation experiments
2. Generate pivot/proceed options with rationale
3. Present to human for final decision (HITL)
4. Document decision with audit trail
5. Update roadmap based on decision

Agents: C1 (ProductPM), C2 (HumanApproval), C3 (RoadmapWriter)
"""

import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class DecisionCrew:
    """StartupAI Decision Crew - Synthesize, decide, document."""

    @agent
    def product_pm_agent(self) -> Agent:
        """C1: Synthesize evidence and propose options."""
        return Agent(
            config=self.agents_config["product_pm_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    @agent
    def human_approval_agent(self) -> Agent:
        """C2: Present options to human and capture decision."""
        return Agent(
            config=self.agents_config["human_approval_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    @agent
    def roadmap_writer_agent(self) -> Agent:
        """C3: Document decisions and update roadmap."""
        return Agent(
            config=self.agents_config["roadmap_writer_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    @task
    def synthesize_evidence(self) -> Task:
        """Analyze all validation signals and synthesize recommendation."""
        return Task(
            config=self.tasks_config["synthesize_evidence"],
            markdown=False,
        )

    @task
    def propose_pivot_proceed_options(self) -> Task:
        """Generate specific options with rationale."""
        return Task(
            config=self.tasks_config["propose_pivot_proceed_options"],
            markdown=False,
        )

    @task
    def request_human_decision(self) -> Task:
        """HITL: Present options to human for final decision."""
        return Task(
            config=self.tasks_config["request_human_decision"],
            markdown=False,
            human_input=True,
        )

    @task
    def document_decision(self) -> Task:
        """Create decision document for audit trail."""
        return Task(
            config=self.tasks_config["document_decision"],
            markdown=False,
        )

    @task
    def update_roadmap(self) -> Task:
        """Translate decision into roadmap updates."""
        return Task(
            config=self.tasks_config["update_roadmap"],
            markdown=False,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StartupAI Decision crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
