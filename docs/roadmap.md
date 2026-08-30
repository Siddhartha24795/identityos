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

## v2.0 — Application compilation + real-ground-truth benchmark  ·  **built**

Requirement-fit assessment against a real, already-adjudicated application:
the IITACB CEO dossier's own 14-requirement fit table, where a real human
had already written both the requirement and their own honest
self-assessment (MET/EXCEEDS/PARTIAL/GAP) with evidence. This is the
"REAL HUMAN ANSWER vs IDENTITYOS ANSWER" comparison the original brief
calls for and v1's benchmark did not have. See docs/evaluation_v2.md,
docs/improvement_changelog.md (v2 entries), docs/hot_take.md (v2 addendum).

Found and fixed one real bug in the process (system confidently overclaiming
a requirement the person had honestly marked as a gap, because "well-cited"
and "positive" got conflated) — documented, not hidden, per the hackathon's
own instruction not to hide failures.

## v2.1 — general corpus completion  ·  **built**

Full, general corpus completion — `data/identity_sources/` was a curated
subset of the two source documents, not a full transcription. Rather than
patching the one remaining known failure (req08) reactively, transcribed
the entire remaining requirement-evidence table plus the dossier's broader
narrative sections in one general pass
(`data/identity_sources/dossier_narrative.md`), independent of which eval
question needed what. Result: dangerous_overclaim_rate 0.25 -> 0.00, and
v1's own score also improved as a side effect. See
docs/improvement_changelog.md (Iteration 6) and docs/evaluation_v2.md.

## v2.2+ — deferred from the original v2 scope  ·  not started

- Automatic belief inference from raw unstructured text (replacing v1/v2's
  hand-seeded beliefs) with an LLM pass plus counter-evidence search.
- `APPLICATION_NARRATIVE_STATE`: answer a full application's question set as
  a coherent set (no contradicting Q1 vs Q3), not independently.
- Document generators: cover letter, SOP, short-answer set, each claim
  still traceable per docs/architecture.md.
- Embedding-based retrieval (pgvector) alongside the existing lexical
  retrieval. Confirmed necessary, not just theoretical, by v2.1's own eval
  run: req05/req10 have real, relevant evidence in the corpus now and still
  retrieve zero facts, because "entrepreneurial mindset" shares no literal
  words with "comfortable with ambiguity, unfunded mandates."
- Clause-level (not sentence-level) negation detection — v2.0's fix
  operates on whole generated sentences, so a single sentence mixing a
  positive and a negative clause ("fluent in English and Hindi but not yet
  in Kannada") gets treated as fully negative (req13). Known limitation,
  see docs/hot_take.md.

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
