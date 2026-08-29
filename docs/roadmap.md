# Roadmap

Built version by version, on request, per the original build instruction:
"Don't build everything. Build things version by version." Each version
below is scoped to be independently demonstrable and independently
evaluable — no version depends on a later one existing to be judged.

## v1 — Digital Self + confidence-gated Q&A  ·  **built, this delivery**

Identity ingestion (structured sources -> Fact/Belief with provenance),
lexical retrieval, citation-grounded generation, per-sentence verification,
confidence-gated refusal, a 19-question Identity Fidelity Benchmark
comparing baseline_plain / baseline_rag / identityos_v1, full trajectory
logging. See docs/architecture.md, docs/evaluation.md.

## v2 — Application compilation + document generation  ·  not started

- Ingest one real, unstructured application (a real job/fellowship posting)
  and build an `ApplicationIntentModel` (what it asks, what it likely
  values).
- `APPLICATION_NARRATIVE_STATE`: answer a full application's question set as
  a coherent set (no contradicting Q1 vs Q3), not independently.
- Automatic belief inference from raw unstructured text (replacing v1's
  hand-seeded beliefs) with an LLM pass plus counter-evidence search.
- Document generators: cover letter, SOP, short-answer set, each claim
  still traceable per docs/architecture.md.
- Embedding-based retrieval (pgvector) alongside the existing lexical
  retrieval, so both can be compared rather than one silently replacing
  the other.

## v3 — Browser execution  ·  not started

- Real browser agent (Playwright): open an application, detect fields, map
  them to Digital Self data, fill and verify entered values.
- Sandboxed by construction: no submission of a real application without an
  explicit human-approval checkpoint (ground rule 4). OTP/MFA is a
  human-in-the-loop pause, never bypassed (ground rule 3, and the original
  brief's own authentication section).
- `BrowserObservation` / `BrowserAction` abstraction, generalized — not
  hard-coded to one site.

## v4 — Multi-agent orchestration + self-improvement  ·  not started

- Orchestrator that decides which specialized agents are actually needed
  per task (not a fixed roster) — Identity, Opportunity, Browser,
  Verification, Contradiction agents from the brief's architecture.
- Learning engine: EXPERIENCE -> FAILURE ANALYSIS -> HYPOTHESIS ->
  COUNTERFACTUAL TEST -> PROMOTE/REJECT, never auto-trusting a successful
  trajectory (docs/research_hypothesis.md #2).
- Contradiction graph made explicit and queryable, not just belief-level
  counter-evidence fields.

## v5 — Graph store + opportunity discovery + web UI  ·  not started

- Migrate Digital Self storage from flat JSON to a proper graph (the brief
  suggests Neo4j) once edge types (SUPPORTED_BY, CONTRADICTS, SUPERSEDES...)
  justify it.
- Opportunity discovery agent + fit scoring.
- Next.js dashboard: Digital Self Explorer, Application Workspace, Agent
  Trajectory View, Identity Diff (before/after Digital Self).

## Explicitly deferred, revisit only if asked
Visa/administrative form support, conference-submission support,
accelerator-specific strategy — the brief's "extensible application types"
list. v1-v3 prove the architecture generalizes before widening the type list.
