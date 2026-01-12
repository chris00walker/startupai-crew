I am a Lead Developer building an automated venture-building system called 'StartupAI' on the Modal serverless stack (CrewAI OSS for orchestration). I have a rough logic document (attached as: /mnt/data/StartupAI Dynamic Execution Architecture.docx) that describes a 'Spiral Escalation' process based on Strategyzer methodology (Desirability, Feasibility, Viability loops).

Task: Acting as a Senior Systems Architect, convert the attached textual concepts into a Level 4 Technical Implementation Specification. I do not want high-level philosophy or summaries. I need the exact "Assembly Manual" to code this immediately.

Important: In addition to the logical loops, you MUST fully specify all mechanics of Phase 1 (Desirability) execution in production terms: ad creation and split-testing, landing page creation and split-testing, platform selection (which social channels), budget and duration rules, approval/HITL gates, and hosting/deployment for landing pages.

Required Deliverables (ALL are required and must be mutually consistent):

1\) Agent & Crew Manifest  

\- A detailed table of all 18 Agents across the 6 Crews (Sage, Pulse, Forge, Ledger, Guardian, Compass).  

\- For each Agent: role, responsibilities, concrete custom tools (e.g., LearningRetrievalTool, BriefParserTool, CopywritingTool, LandingPageGeneratorTool, LandingPageDeploymentTool, ExperimentDeployTool, AnalyticsTool, GuardianReviewTool), and CrewAI configuration notes (e.g., memory=true, human\_input=true, external\_memory usage).  

\- Explicit mapping from Flow-level steps (e.g., run\_desirability\_experiments) to the Crew \+ Agent \+ Task that actually does the work, including which specific tools are invoked.

2\) State Architecture  

\- Full Python Pydantic code for the StartupValidationState class.  

\- All Enum flags needed for voting and routing (e.g., DesirabilitySignal.WEAK\_INTEREST, FeasibilitySignal.ORANGE\_CONSTRAINED, ViabilitySignal.UNDERWATER, ProblemFit, RiskAxis, PivotType, Phase, HumanApprovalStatus).  

\- Any additional fields required to:

  \- Persist experiment IDs, campaign IDs, and artifact URLs (ads assets, landing pages, MVP URLs).  

  \- Track per-artifact approval status (e.g., ad\_approval\_status, lp\_approval\_status).  

  \- Persist platform selection decisions, budget, duration, and routing for A/B tests.  

  \- Capture human-in-the-loop (HITL) decisions and comments for both creative approval and viability pivots.  

3\) Execution Logic (Flow)  

\- Complete Python code for StartupValidationFlow using crewai.flow.  

\- Implement @router logic for the three feedback loops (Desirability, Feasibility, Viability) as described in the text, including all regression paths (loops back to earlier phases instead of always moving forward).  

\- Every place where the Flow claims that “X runs experiments / builds Y” must be backed by a concrete Crew call that matches the orchestration layer described below (no abstract statements).  

\- The Desirability flow must explicitly:

  \- Generate ad and landing page variants.  

  \- Route these variants through an approval workflow (Guardian \+ HITL where applicable) BEFORE deployment.  

  \- Only after approval, call the experiment deployment tools to launch the campaigns.

4\) Crew & Task Orchestration Layer  

\- Concrete Python implementations for at least:  

  \- PulseCrew: orchestrating generation and deployment of ads, landing pages, and desirability experiments (including metric collection and computation of DesirabilitySignal). This MUST show:

    \- How ad variants are generated (e.g., CopywritingTool.generate\_ads).  

    \- How landing page variants are generated (e.g., LandingPageGeneratorTool.generate\_pages).  

    \- How landing page variants are deployed/hosted (e.g., LandingPageDeploymentTool.deploy\_page\_variants to Netlify/Vercel or similar).  

    \- How ad and LP variants are wired into platform-level A/B tests (e.g., ExperimentDeployTool.deploy mapping variants to platform campaigns/ad sets).  

  \- ForgeCrew: orchestrating generation and deployment of MVP / landing page builds and feasibility assessment (including FeasibilitySignal).  

  \- LedgerCrew: orchestrating unit economics computation and ViabilitySignal.  

\- For each of these Crews:  

  \- Show how kickoff(inputs: dict) calls specific tools in sequence to produce the artifacts described (ads, landing pages, MVP URLs, experiment\_ids, campaign\_ids, metrics).  

  \- Return types must be typed Pydantic models (e.g., PulseDesirabilityResult, ForgeFeasibilityResult, LedgerViabilityResult) whose fields map directly into StartupValidationState.  

\- Provide minimal but concrete Python stubs for the key tools, including but not limited to:  

  \- CopywritingTool.generate\_ads (with inputs/outputs for multiple ad variants).  

  \- LandingPageGeneratorTool.generate\_pages (supporting multiple LP variants for split-testing).  

  \- LandingPageDeploymentTool.deploy\_page\_variants (including hosting details, base\_url, routing\_map, provider like Netlify/Vercel).  

  \- ExperimentDeployTool.deploy (with inputs for ad\_variants, LP URLs, platform selection, budget, duration; outputs including experiment\_id and per-platform campaign\_ids).  

  \- AnalyticsTool.collect\_desirability\_metrics (with concrete metric fields such as impressions, clicks, signups, spend\_usd, CTR, conversion\_rate).  

5\) Phase 1 Experiment Configuration & Platform Selection  

\- A concrete configuration scheme (Python or YAML) that defines:

  \- How social / ad platforms are selected per project (e.g., B2B → LinkedIn/Google, B2C → Meta/TikTok), based on fields from the brief/BMC.  

  \- How experiment duration and budget are determined (e.g., duration\_days, total\_budget\_usd, min\_impressions).  

  \- How budget is allocated per platform and per variant.  

\- Show how PulseCrew and ExperimentDeployTool read this configuration and translate it into real deployment parameters (e.g., budget\_per\_platform, duration\_days, targeting spec).

6\) Creative Approval Workflow (Guardian \+ HITL)  

\- A concrete design for the approval flow of ad concepts and landing pages before deployment:

  \- State fields and Enums for artifact approval status (e.g., DRAFT, PENDING\_REVIEW, APPROVED, REJECTED).  

  \- A GuardianCrew review method that performs automatic checks (policy, banned terms, basic QA) and either:

    \- auto-approves safe assets, or  

    \- raises a HITL decision via Compass/HumanApprovalAgent using human\_input=true.  

  \- Example Python methods showing:

    \- How PulseCrew passes ad/LP drafts to GuardianCrew for review.  

    \- How approved assets are then passed to ExperimentDeployTool.  

    \- How rejected assets cause regeneration or manual edits before re-review.  

\- Example Modal HITL approval payloads (`/hitl/approve`) for creative approval decisions (approve/reject) and how these are written back into StartupValidationState and used to either proceed to deployment or regenerate assets.

7\) Modal + CrewAI Configuration Artifacts  

\- Example agents.yaml and tasks.yaml snippets for at least the Pulse and Forge crews, showing:  

  \- How agents are configured with tools and memory.  

  \- How tasks are defined to use human\_input (where applicable), including:

    \- Creative approval tasks (e.g., guardian\_creative\_review, compass\_creative\_approval).  

    \- Viability pivot tasks.  

  \- How tasks relate to the Crew orchestration methods (e.g., generate\_ad\_concepts, generate\_landing\_page\_copy, deploy\_landing\_pages, deploy\_experiments, collect\_experiment\_metrics).  

\- crewai\_config.yaml example:  

  \- Webhook configuration for human-in-the-loop pivots and approvals (humanInputWebhook, taskWebhookUrl, stepWebhookUrl, crewWebhookUrl).  

  \- Memory configuration using Supabase pgvector (URL, table, embedding model) and how this is wired into crews via external\_memory.  

8\) Human-in-the-Loop (HITL) Integration for Viability  

\- Exact HTTP payload examples for Modal HITL approvals (`/hitl/approve`) when a human decides:  

  \- price\_pivot vs cost\_pivot vs kill in the Viability loop.  

\- Show how the Flow reads these decisions back into StartupValidationState and uses them to route:  

  \- price\_pivot → regression to Desirability (with updated pricing configuration used in subsequent experiments).  

  \- cost\_pivot → regression to Feasibility (with updated cost/feature constraints for ForgeCrew to apply).  

  \- kill → terminal KILLED phase (with Guardian logging and learning capture).

Tone & Format:

\- Strictly technical.  

\- Use code blocks for all logic, schemas, and configuration examples.  

\- Use tables for agent and crew configurations.  

\- Treat this as a document I will hand directly to a developer to start coding: no philosophy, no high-level summaries, no hand-wavy “this agent would probably do X” — every capability you describe must appear either as code, a tool signature, or a concrete YAML/config example.  

\- Any behavior you describe around ads, landing pages, platform selection, budget/duration, approvals, or hosting MUST be expressed as explicit code, configuration, or tool interfaces, not as conceptual prose.  
