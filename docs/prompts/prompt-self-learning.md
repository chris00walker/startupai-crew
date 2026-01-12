You are the next Lead Developer working on the StartupAI venture-building platform, implemented on the Modal serverless stack with Supabase (Postgres \+ pgvector) as the primary persistence and learning layer.

Your mission is to extend the existing architecture into a \*\*self-learning, self-improving system\*\*, analogous in spirit to how Google’s Vertex AI continuously improves through data, feedback, and configuration loops.

\====================================================

1\. CONTEXT & EXISTING ARCHITECTURE

\====================================================

You are inheriting an existing codebase and architecture with these key components:

\- A Strategyzer-inspired validation pipeline implemented as:

  \- \`StartupValidationFlow\` (crewai.flow) with phases:

    \- IDEA → DESIRABILITY → FEASIBILITY → VIABILITY → VALIDATED / KILLED

  \- Explicit routing and regression:

    \- Desirability loop: \`run\_desirability\_experiments\` \+ signal-based router.

    \- Feasibility loop: \`run\_feasibility\_assessment\` \+ regression on constraints.

    \- Viability loop: \`run\_viability\_analysis\` \+ HITL price/cost/kill decisions.

\- State layer:

  \- \`StartupValidationState\` (Pydantic) with:

    \- \`Phase\`, \`DesirabilitySignal\`, \`FeasibilitySignal\`, \`ViabilitySignal\`, \`PivotType\`, \`HumanApprovalStatus\`, etc.

    \- Desirability artifacts:

      \- \`DesirabilityExperimentRun\`

      \- \`AdVariant\`, \`LandingPageVariant\`

      \- \`DesirabilityMetrics\`, \`ExperimentRoutingConfig\`, \`PlatformBudgetConfig\`.

    \- Feasibility artifacts: \`FeasibilityArtifact\`.

    \- Viability metrics: \`ViabilityMetrics\`.

    \- Full experiment history (\`desirability\_experiments\`) and pivot history.

\- Core crews and responsibilities:

  \- \*\*SageCrew\*\*: intake, customer research, VPC/BMC creation and updates.

  \- \*\*PulseCrew\*\*: desirability experiments:

    \- Ad \+ landing page generation.

    \- Guardian review \+ HITL creative approval.

    \- Experiment deployment (ads \+ LPs) and metric collection.

  \- \*\*ForgeCrew\*\*: feasibility assessment, scope downgrade, and MVP builds.

  \- \*\*LedgerCrew\*\*: unit economics \+ viability signal.

  \- \*\*GuardianCrew\*\*: QA, policy/gov checks, and final audits.

  \- \*\*CompassCrew\*\*: HITL orchestration (approvals, price/cost/kill decisions).

\- Tools (Python stubs exist, to be implemented):

  \- \`CopywritingTool.generate\_ads\`

  \- \`LandingPageGeneratorTool.generate\_pages\`

  \- \`LandingPageDeploymentTool.deploy\_page\_variants\`

  \- \`ExperimentDeployTool.deploy\`

  \- \`AnalyticsTool.collect\_desirability\_metrics\`

  \- \`ComponentLibraryScraper\`, \`TechStackValidator\`, \`PythonREPLTool\`, \`GuardianReviewTool\`, etc.

\- Learning \+ ETL (skeleton):

  \- Supabase Postgres \+ pgvector:

    \- \`experiment\_outcomes\` table (aggregated metrics per experiment/platform/variant).

    \- \`startupai\_learning\` table (vector store of “playbook entries” / learnings).

  \- ETL job:

    \- Reads \`experiment\_outcomes\`.

    \- Computes a per-context success score.

    \- Embeds and upserts rows into \`startupai\_learning\` with \`type="experiment\_config"\`.

  \- \`RetrievalAwareExperimentConfigResolver\`:

    \- Combines YAML defaults with nearest-neighbor experiment configs from \`startupai\_learning\` to adapt platform selection, budgets and durations per project.

You should assume that:

\- These models, enums, and flows already exist.

\- Many parts are stubbed (NotImplementedError) and need concrete implementation.

\- Supabase, OpenAI embeddings, and Modal webhooks are already wired at basic levels.

\====================================================

2\. HIGH-LEVEL GOAL FOR YOU

\====================================================

Transform the current architecture into a \*\*production-grade, self-improving platform\*\* that:

1\. \*\*Collects\*\* structured evidence from all experiments (ads/LPs/MVPs/unit economics).

2\. \*\*Learns\*\* from past experiments across projects via ETL and vector search.

3\. \*\*Adapts\*\* future experiment configs and creative generation based on that learning.

4\. \*\*Monitors & governs\*\* this learning (safeguards, explainability, reproducibility).

Think of StartupAI as a “Vertex AI for startup validation”: data-in → experiments → signals → learning → better future experiments.

\====================================================

3\. CONCRETE OBJECTIVES

\====================================================

Your job is to implement the following \*\*5 pillars\*\*:

1\. \*\*Data & Metrics Pipeline\*\*

2\. \*\*Learning ETL & Playbooks (Configs \+ Creatives)\*\*

3\. \*\*Retrieval-Enhanced Decision Policies\*\*

4\. \*\*Dynamic Thresholds & Auto-Tuning\*\*

5\. \*\*Monitoring, Governance, & Developer Ergonomics\*\*

Each objective below MUST result in concrete code, configuration, or queries (no conceptual-only work).

\====================================================

4\. OBJECTIVE 1 – DATA & METRICS PIPELINE

\====================================================

Goal: Ensure \*\*every experiment\*\* produces structured, queryable data that feeds learning.

You must:

1\. Implement persistence from \`StartupValidationState\` → Supabase:

   \- For each \`DesirabilityExperimentRun\`, write rows into:

     \- \`experiment\_outcomes\`:

       \- Required fields:

         \- project\_id

         \- experiment\_id

         \- segment\_type

         \- vertical (if available)

         \- platform

         \- variant\_tag

         \- downgrade\_active

         \- impressions, clicks, signups, spend\_usd, ctr, conversion\_rate, cpa

         \- timestamps (started\_at, ended\_at)

   \- Ensure these writes happen \*\*after\*\* metrics are collected in \`PulseCrew\`.

2\. Add “config snapshotting”:

   \- For each experiment, persist a JSON snapshot of:

     \- Platform configs (budgets, durations, audience\_spec).

     \- Price points, offer details, and any VPC attributes relevant for analysis.

   \- Either:

     \- Inline in \`experiment\_outcomes\` as a \`config\_json\` column, or

     \- Separate table \`experiment\_configs\` linked by \`experiment\_id\`.

   \- This will allow ETL to later learn not just “what worked” but also “which config produced it”.

3\. Make sure all write operations:

   \- Are idempotent (safe to re-run ETL).

   \- Are resilient to transient Supabase errors (simple retry or failure logging).

Deliverables you must produce:

\- Python functions in a \`startupai/persistence/\` module that:

  \- \`save\_experiment\_outcome(experiment\_run: DesirabilityExperimentRun, vpc: dict) \-\> None\`

  \- \`save\_experiment\_config(experiment\_run: DesirabilityExperimentRun, config: ProjectExperimentConfig) \-\> None\`

\====================================================

5\. OBJECTIVE 2 – LEARNING ETL & PLAYBOOKS (CONFIGS \+ CREATIVES)

\====================================================

Goal: Extend the ETL to create \*\*two\*\* categories of playbooks in \`startupai\_learning\`:

\- \`type \= "experiment\_config"\` – what platforms/budgets/targeting work for which segments.

\- \`type \= "creative\_example"\` – what hooks/headlines/LP structures produce strong responses for which segments.

You must:

1\. Complete and harden the \*\*config ETL\*\*:

   \- Implement \`ExperimentETL\` from the existing skeleton:

     \- Robust error handling and logging.

     \- Parameterize time windows, min volume filters (e.g. require a minimum signups).

   \- Adjust \`success\_score\` calculation:

     \- Incorporate CTR, conversion rate, volume, and cost (CPA).

     \- Make weights configurable (YAML or environment).

   \- Implement the Postgres \`search\_startupai\_learning\` function and test it.

2\. Add a \*\*creative ETL\*\*:

   \- Define a Supabase table \`creative\_outcomes\` OR derive it from \`experiment\_outcomes\` and stored copies of:

     \- Ad text (headline/body/CTA).

     \- LP variant metadata (hero headline, key bullets, etc.).

   \- Extract for each strong-performing variant:

     \- A “creative recipe”:

       \- segment\_type, vertical, platform, variant\_tag, hook type, promise type.

       \- raw text and structural features (e.g., “short headline with X, Y, Z”).

   \- Write ETL logic:

     \- Compute a creative success score (similar to experiment but more focused on CTR and CVR).

     \- Embed text description of the creative recipe.

     \- Upsert into \`startupai\_learning\` with \`type="creative\_example"\`.

3\. Align embedding usage:

   \- Use the same embedding model across:

     \- \`experiment\_config\` and \`creative\_example\` entries.

   \- Ensure that the text you embed:

     \- Contains both \*\*context\*\* (segment/vertical/platform/offer) and \*\*outcome\*\* (score metrics).

     \- Is deterministic enough for reproducibility.

Deliverables:

\- \`startupai/learning/etl\_experiments.py\` – finalized and production-ready.

\- \`startupai/learning/etl\_creatives.py\` – new ETL for creative playbooks.

\- SQL migrations for any new tables/columns you introduce.

\====================================================

6\. OBJECTIVE 3 – RETRIEVAL-ENHANCED DECISION POLICIES

\====================================================

Goal: Make \*\*core decisions\*\* retrieval-aware, not just platform configurations:

1\. Finalize and integrate \`RetrievalAwareExperimentConfigResolver\`:

   \- Use \`experiment\_config\` entries to adapt:

     \- \`platform\_budgets\` (platform mix, budget, duration, min\_impressions).

   \- Implement blending:

     \- Base YAML defaults \+ historical winners.

   \- Ensure safe fallbacks when:

     \- No relevant history exists.

     \- History is too noisy (low similarity or low volume).

2\. Implement \*\*creative retrieval\*\* for:

   \- \`CopywritingTool.generate\_ads\`:

     \- Before generating ad variants, query \`startupai\_learning\` for:

       \- \`type="creative\_example"\` entries matching current segment/vertical/platform.

     \- Use the retrieved creative examples as:

       \- Few-shot prompts / structured patterns for ad generation.

   \- \`LandingPageGeneratorTool.generate\_pages\`:

     \- Retrieve best historical LP patterns for similar context.

     \- Parameterize hero layouts, CTA structures, and section ordering based on these.

3\. Wire retrieval into tools:

   \- Add a \`LearningRetrievalTool\` (or equivalent) that:

     \- Wraps calls to Supabase RPC \`search\_startupai\_learning\`.

   \- In your tool implementations:

     \- Accept \`context\` objects (segment\_type, vertical, platform, price, goal).

     \- Call the retrieval tool to fetch:

       \- \`experiment\_config\` and/or \`creative\_example\` entries.

     \- Use them deterministically when generating:

       \- Platform selection (config resolver).

       \- Ad copy / hooks / LP structure (creative tools).

Deliverables:

\- Completed \`RetrievalAwareExperimentConfigResolver\` integrated into \`PulseCrew\`.

\- Updated \`CopywritingTool\` and \`LandingPageGeneratorTool\` that:

  \- Accept retrieved examples.

  \- Use them in generation (e.g., structured prompt templates).

\====================================================

7\. OBJECTIVE 4 – DYNAMIC THRESHOLDS & AUTO-TUNING

\====================================================

Goal: Remove hard-coded decision thresholds and make them \*\*data-driven\*\* and \*\*adaptive\*\*.

You must:

1\. Replace hard-coded thresholds in Pulse:

   \- \`\_compute\_desirability\_signal\` currently uses static values for CTR/CVR.

   \- Replace with a \*\*threshold repository\*\*, loaded from Supabase:

     \- \`desirability\_thresholds\` table with columns:

       \- segment\_type, vertical, platform

       \- min\_ctr\_for\_interest, min\_cvr\_for\_commitment, min\_signups\_for\_commitment, updated\_at.

   \- Add a maintenance job:

     \- Periodically update these thresholds based on historical distributions.

2\. Make viability decisions adaptive:

   \- Instead of fixed CAC/LTV rules, maintain a \`viability\_thresholds\` table:

     \- Vertical-specific CAC/LTV acceptable ratios.

     \- Minimum TAM thresholds per vertical.

   \- Ledger uses this table to classify:

     \- \`PROFITABLE\`, \`UNDERWATER\`, \`ZOMBIE\_MARKET\`.

3\. Add simple \*\*auto-tuning\*\*:

   \- For each vertical/segment, run an offline job that:

     \- Adjusts thresholds based on hitting target false-negative/false-positive rates (e.g. using quantiles).

   \- Persist those updated thresholds and ensure \`PulseCrew\` and \`LedgerCrew\` read them at runtime.

Deliverables:

\- New Supabase tables and migrations:

  \- \`desirability\_thresholds\`, \`viability\_thresholds\`.

\- Threshold loader functions:

  \- \`load\_desirability\_thresholds(segment\_type, vertical, platform)\`.

  \- \`load\_viability\_thresholds(vertical)\`.

\- Updated routing logic in \`StartupValidationFlow\` that uses these dynamic thresholds indirectly via Pulse/Ledger.

\====================================================

8\. OBJECTIVE 5 – MONITORING, GOVERNANCE & DX

\====================================================

Goal: Treat the learning system as a \*\*continuous experiment platform\*\*. Make it observable, safe, and developer-friendly.

You must:

1\. Implement \*\*experiment and learning dashboards\*\*:

   \- Use Supabase or a simple dashboard app to display:

     \- Per-segment/per-vertical:

       \- CTR, CVR, CAC, LTV distributions.

       \- Platform performance ranking.

       \- Top playbook entries (configs \+ creatives).

   \- Provide dev-facing views of:

     \- Latest thresholds used.

     \- Changes in budgets/durations over time.

2\. Add \*\*governance and safety checks\*\*:

   \- Ensure Guardian/QA layer logs:

     \- When retrieved configs or creatives are used.

     \- When overrides are applied (manual adjustments).

   \- Introduce basic guardrails:

     \- Do not automatically scale budgets beyond configured max limits.

     \- Allow kill-switch flags per vertical or platform in config.

3\. Improve developer ergonomics:

   \- Add \*\*integration tests\*\* for retrieval-aware behavior:

     \- Example: given a synthetic historical dataset, confirm resolver:

       \- Adds or removes platforms as expected.

       \- Adjusts budgets in the direction of historical winners.

   \- Provide seed scripts:

     \- To create minimal demo data in Supabase (experiments, learning entries, thresholds).

   \- Document:

     \- Data model (tables \+ RPCs).

     \- ETL jobs (how/when they run).

     \- Retrieval patterns (how tools call learning retrieval).

Deliverables:

\- A small \`/docs/learning-system.md\` that explains:

  \- Data flow from experiments → ETL → learning store → retrieval → adjusted configs.

\- Integration tests within the repo that validate:

  \- Resolver \+ creative retrieval behavior.

\====================================================

9\. IMPLEMENTATION PRINCIPLES

\====================================================

While working, adhere to these principles:

1\. \*\*Deterministic and Reproducible\*\*

   \- Every decision should be explainable:

     \- Which experiments informed it?

     \- Which thresholds were used?

     \- Which playbook entries were retrieved?

2\. \*\*Safe Defaults First, Learning on Top\*\*

   \- If retrieval fails or ETL hasn’t run yet:

     \- System must still function correctly with YAML defaults.

   \- Learning should bias behavior, not break it.

3\. \*\*Incremental Rollout\*\*

   \- For new retrieval-aware behavior:

     \- Start with “advisory mode” (log what would have changed, without enforcing).

     \- Then move to “enforced mode” after validation.

4\. \*\*Tight Coupling to Current Schemas\*\*

   \- All code must respect and extend:

     \- \`StartupValidationState\` models and enums.

     \- Existing crews (\`PulseCrew\`, \`ForgeCrew\`, etc.).

   \- Do not redesign the flow; extend it.

\====================================================

10\. WHAT TO DELIVER

\====================================================

By the time you are finished, StartupAI should:

\- Persist structured experiment and creative outcome data into Supabase.

\- Run ETL jobs that convert outcomes into:

  \- \`experiment\_config\` playbooks.

  \- \`creative\_example\` playbooks.

\- Use retrieval-aware resolvers for:

  \- Platform selection and budgeting.

  \- Creative generation (ads \+ landing pages).

\- Use dynamic thresholds for:

  \- Desirability (CTR/CVR/signups).

  \- Viability (CAC/LTV/TAM).

\- Offer a basic but functional monitoring surface and documentation.

The net effect should be that \*\*each new startup project benefits from the accumulated experience of all prior projects\*\*, with behavior improving over time while remaining governed, explainable, and safe.  
