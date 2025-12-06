"""
StartupAI Validation Crew - Crew 2 of 3

This crew executes the validation pipeline:
- DESIRABILITY: Test customer interest with ads and landing pages
- FEASIBILITY: Assess technical buildability
- VIABILITY: Validate unit economics

Agents (12):
- Pulse: P1 (AdCreative), P2 (Comms), P3 (Analytics)
- Forge: F1 (UXUI), F2 (Frontend), F3 (Backend)
- Ledger: L1 (Financial), L2 (Legal), L3 (Economics)
- Guardian: G1 (QA), G2 (Security), G3 (Audit)

HITL Checkpoints (5):
1. approve_campaign_launch
2. approve_spend_increase
3. approve_desirability_gate
4. approve_feasibility_gate
5. approve_viability_gate
"""

import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class ValidationCrew:
    """StartupAI Validation Crew - Execute D/F/V experiments."""

    # ═══════════════════════════════════════════════════════════════
    # PULSE AGENTS (Growth/Marketing)
    # ═══════════════════════════════════════════════════════════════

    @agent
    def ad_creative_agent(self) -> Agent:
        """P1: Generate ad variants for desirability testing."""
        return Agent(
            config=self.agents_config["ad_creative_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.8),
        )

    @agent
    def comms_agent(self) -> Agent:
        """P2: Write landing page copy."""
        return Agent(
            config=self.agents_config["comms_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.7),
        )

    @agent
    def analytics_agent(self) -> Agent:
        """P3: Deploy experiments and compute metrics."""
        return Agent(
            config=self.agents_config["analytics_agent"],
            tools=[],  # Will add InvokeCrewAIAutomationTool
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    # ═══════════════════════════════════════════════════════════════
    # FORGE AGENTS (Build)
    # ═══════════════════════════════════════════════════════════════

    @agent
    def ux_ui_designer_agent(self) -> Agent:
        """F1: Create layout specs and wireframes."""
        return Agent(
            config=self.agents_config["ux_ui_designer_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.7),
        )

    @agent
    def frontend_dev_agent(self) -> Agent:
        """F2: Generate and deploy landing pages."""
        return Agent(
            config=self.agents_config["frontend_dev_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    @agent
    def backend_dev_agent(self) -> Agent:
        """F3: Assess technical feasibility."""
        return Agent(
            config=self.agents_config["backend_dev_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    # ═══════════════════════════════════════════════════════════════
    # LEDGER AGENTS (Finance)
    # ═══════════════════════════════════════════════════════════════

    @agent
    def financial_controller_agent(self) -> Agent:
        """L1: Compute unit economics."""
        return Agent(
            config=self.agents_config["financial_controller_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),
        )

    @agent
    def legal_compliance_agent(self) -> Agent:
        """L2: Identify regulatory constraints."""
        return Agent(
            config=self.agents_config["legal_compliance_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),
        )

    @agent
    def economics_reviewer_agent(self) -> Agent:
        """L3: Review and stress-test assumptions."""
        return Agent(
            config=self.agents_config["economics_reviewer_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),
        )

    # ═══════════════════════════════════════════════════════════════
    # GUARDIAN AGENTS (Governance)
    # ═══════════════════════════════════════════════════════════════

    @agent
    def qa_agent(self) -> Agent:
        """G1: Quality gate checks and HITL presentation."""
        return Agent(
            config=self.agents_config["qa_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    @agent
    def security_agent(self) -> Agent:
        """G2: PII scrubbing and security checks."""
        return Agent(
            config=self.agents_config["security_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.3),
        )

    @agent
    def audit_agent(self) -> Agent:
        """G3: Capture learnings and audit trail."""
        return Agent(
            config=self.agents_config["audit_agent"],
            tools=[],
            reasoning=False,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0.5),
        )

    # ═══════════════════════════════════════════════════════════════
    # DESIRABILITY TASKS
    # ═══════════════════════════════════════════════════════════════

    @task
    def generate_ad_variants(self) -> Task:
        return Task(config=self.tasks_config["generate_ad_variants"], markdown=False)

    @task
    def generate_landing_page_copy(self) -> Task:
        return Task(config=self.tasks_config["generate_landing_page_copy"], markdown=False)

    @task
    def build_landing_page(self) -> Task:
        return Task(config=self.tasks_config["build_landing_page"], markdown=False)

    @task
    def approve_campaign_launch(self) -> Task:
        """HITL: Human approves creatives."""
        return Task(
            config=self.tasks_config["approve_campaign_launch"],
            markdown=False,
            human_input=True,
        )

    @task
    def approve_spend_increase(self) -> Task:
        """HITL: Human approves budget."""
        return Task(
            config=self.tasks_config["approve_spend_increase"],
            markdown=False,
            human_input=True,
        )

    @task
    def deploy_experiments(self) -> Task:
        return Task(config=self.tasks_config["deploy_experiments"], markdown=False)

    @task
    def compute_desirability_signal(self) -> Task:
        return Task(config=self.tasks_config["compute_desirability_signal"], markdown=False)

    @task
    def approve_desirability_gate(self) -> Task:
        """HITL: Human approves desirability phase."""
        return Task(
            config=self.tasks_config["approve_desirability_gate"],
            markdown=False,
            human_input=True,
        )

    # ═══════════════════════════════════════════════════════════════
    # FEASIBILITY TASKS
    # ═══════════════════════════════════════════════════════════════

    @task
    def design_layout_spec(self) -> Task:
        return Task(config=self.tasks_config["design_layout_spec"], markdown=False)

    @task
    def assess_technical_feasibility(self) -> Task:
        return Task(config=self.tasks_config["assess_technical_feasibility"], markdown=False)

    @task
    def approve_feasibility_gate(self) -> Task:
        """HITL: Human approves feasibility phase."""
        return Task(
            config=self.tasks_config["approve_feasibility_gate"],
            markdown=False,
            human_input=True,
        )

    # ═══════════════════════════════════════════════════════════════
    # VIABILITY TASKS
    # ═══════════════════════════════════════════════════════════════

    @task
    def compute_unit_economics(self) -> Task:
        return Task(config=self.tasks_config["compute_unit_economics"], markdown=False)

    @task
    def flag_compliance_constraints(self) -> Task:
        return Task(config=self.tasks_config["flag_compliance_constraints"], markdown=False)

    @task
    def review_economics_assumptions(self) -> Task:
        return Task(config=self.tasks_config["review_economics_assumptions"], markdown=False)

    @task
    def approve_viability_gate(self) -> Task:
        """HITL: Human approves viability phase."""
        return Task(
            config=self.tasks_config["approve_viability_gate"],
            markdown=False,
            human_input=True,
        )

    # ═══════════════════════════════════════════════════════════════
    # AUDIT TASKS
    # ═══════════════════════════════════════════════════════════════

    @task
    def scrub_pii_from_artifacts(self) -> Task:
        return Task(config=self.tasks_config["scrub_pii_from_artifacts"], markdown=False)

    @task
    def capture_learnings(self) -> Task:
        return Task(config=self.tasks_config["capture_learnings"], markdown=False)

    @task
    def trigger_decision_crew(self) -> Task:
        return Task(config=self.tasks_config["trigger_decision_crew"], markdown=False)

    @crew
    def crew(self) -> Crew:
        """Creates the StartupAI Validation crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
