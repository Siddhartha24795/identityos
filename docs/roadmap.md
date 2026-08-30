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

## v2.2 — clause-level negation  ·  **built**

Fixed req13 (Kannada fluency): a claim mixing a positive and a negative
clause in one sentence was scored fully negative by whole-sentence
detection. Now splits on unambiguous contrastive conjunctions and buckets a
mixed claim as `partial`, not `gap`. Agreement rate 0.36 -> 0.43, no
regressions on the other 13 requirements (re-verified, not just inspected
in isolation), dangerous overclaim rate held at 0.00. See
docs/improvement_changelog.md (Iteration 7), docs/evaluation_v2.md.

## v2.3 — embedding-based retrieval  ·  **built, not promoted to default**

Built `identityos_v2_semantic` (services/embeddings/, fastembed +
BAAI/bge-small-en-v1.5, ~65MB ONNX model, no API key) as a real comparison
arm alongside lexical `identityos_v2`. It genuinely fixed req10 and
improved req05, confirming the lexical-retrieval limitation was real and
addressable. It also reintroduced a dangerous overclaim (req09) and
downgraded six previously-correct requirements, because higher-recall
retrieval interacts badly with v2.2's polarity check — see
docs/hot_take.md's v2.3 addendum. **Decision at the time: keep lexical
retrieval as the shipped default**; the semantic arm stays in the harness,
not deleted, as an honest ongoing comparison. (Superseded by v2.4 below —
kept here because the changelog shouldn't quietly rewrite what was
actually decided at each point.) See docs/improvement_changelog.md
(Iteration 8), docs/evaluation_v2.md.

## v2.4 — hybrid retrieval  ·  **built, promoted**

Diagnosed the exact mechanism behind v2.3's regression — semantic noise
only appeared when it overrode requirements lexical already had evidence
for — and built `retrieve_hybrid()` to target exactly that: lexical first,
semantic fallback only when lexical returns nothing. Verified
requirement-by-requirement, not assumed: all 12 requirements lexical could
already answer are byte-identical to pure lexical output. Result:
agreement rate 0.50 (best of all five systems), dangerous overclaim rate
0.00 (matches lexical). **This supersedes v2.3's decision — hybrid
retrieval is now the recommended strategy**, kept alongside lexical-only
and semantic-only as permanent comparison arms. See
docs/improvement_changelog.md (Iteration 9), docs/evaluation_v2.md,
docs/hot_take.md's v2.4 addendum.

## v2.5 — Document Generation (cover letter)  ·  **built**

First real generated artifact: a 4-section cover letter
(`services/document_engine/`), reusing hybrid retrieval and verification
unmodified, plus `_prefer_unused()` — a concrete, working instance of the
brief's `APPLICATION_NARRATIVE_STATE` (spread evidence across sections
instead of repeating the same two facts). Evidence coverage 0.95,
unsupported-claim rate 0.05, repeated-evidence rate 0.32, vs. the usual
0.00/1.00/n-a for both baselines.

Found a genuinely new failure mode by reading the actual letter, not just
its passing score: real, grounded, true evidence can still be the *wrong
scope* for the document being written (strategy narrative for one specific
prior application, cited as if it were general evidence about the
person). Added `FactCategory.APPLICATION_SPECIFIC` to tag and exclude it.
This closed the obvious case and — found on re-inspection, not hidden —
left a subtler one: the same contamination survives inside individual
sentences of otherwise-general facts, one level more granular than the fix
addresses. See docs/evaluation_documents.md, docs/hot_take.md's v2.5
addendum, docs/improvement_changelog.md.

## v2.6+ — deferred  ·  not started

- Sentence/clause-level content-scope classification, or LLM-assisted
  neutral rephrasing at generation time — the direct follow-up to v2.5's
  residual finding. Needs its own evaluation (the former) or a real
  provider key (the latter); not attempted as a reactive corpus edit.
- Automatic belief inference from raw unstructured text (replacing v1/v2's
  hand-seeded beliefs) with an LLM pass plus counter-evidence search.
- Extend document generation to other types (SOP, research statement,
  short-answer set) and to a *named* target opportunity (a real
  `ApplicationIntentModel`, not just a generic-role system prompt) — would
  also directly address the v2.5 scope-contamination finding, since a
  named target makes "in scope for this document" a checkable fact instead
  of an implicit assumption.
- Six requirements (req03/06/07/11/12/14) still don't reach an exact bucket
  match under any retrieval arm — mostly a coarse-3-bucket-scale nuance
  problem, not a retrieval problem. Would need either a finer-grained real
  assessment scale or a smarter bucketing rule; not attempted yet because
  neither is a quick fix and both need their own evaluation.

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
