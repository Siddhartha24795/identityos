# Architecture — v1

The original design brief (preserved in full in this repo's root
`PROMPT.md`) describes a much larger system: browser execution,
multi-agent orchestration, opportunity discovery, a graph database, a
learning engine with counterfactual promotion. v1 deliberately builds only
the load-bearing core of that vision — the part the hackathon rubric
actually rewards (a purposeful, verifiable agent solving a real problem) —
and documents the rest as a roadmap (docs/roadmap.md) rather than stubbing
it out with fake integrations.

## v1 pipeline

```
structured markdown sources (data/identity_sources/*.md)
        |
        v
  ingest.py  ---------------------------->  Fact[]  (provenance: file + line)
        |
        v
  seed_beliefs.py  ----------------------->  Belief[] (supporting + counter evidence)
        |
        v
  DigitalSelf v1  (services/identity_engine/store.py, versioned JSON)
        |
        v
  ---------------------- per question ----------------------
  |                                                          |
  v                                                          v
baseline_plain               baseline_rag              identityos_agent
(no context)              (unstructured full dump)    (retrieve -> cite -> verify -> gate)
  |                                                          |
  +--------------------------+-------------------------------+
                             v
                    verification.py (per-sentence grounding check)
                             v
                    scoring.py (Identity Fidelity Score)
                             v
                    data/evaluation/results/<tag>/{answers,summary}.json
                                              + trajectories/*.{md,json}
```

## Design choices and why

**Facts vs. beliefs are separate types (packages/schemas/identity.py).**
A `Fact` is a direct transcription with 0.99 confidence; a `Belief` is an
inference and *must* carry a confidence score plus optional counter-evidence.
`belief:003` and `belief:004` in `seed_beliefs.py` are deliberately
low-confidence with real counter-evidence attached — see docs/evaluation.md
q17 and q13 for what this buys.

**Retrieval is lexical, not embedding-based (v1 simplification).** The
brief calls for hybrid graph + vector + document storage. v1 uses
deterministic word-overlap scoring instead of embeddings, for one concrete
reason: it makes every retrieval decision auditable by a human reading the
trajectory file, with no vector index to trust blindly. This is the
correct trade for a 19-question benchmark; it will not scale semantically
past a few hundred facts, which is exactly why v2 adds a vector store
(docs/roadmap.md).

**Question type is declared, not classified (v1 simplification).** The
brief's "unseen question reasoning" pipeline includes an automatic
QUESTION TYPE CLASSIFICATION step. v1 trusts the question bank's authored
`type` field instead of training/prompting a classifier. This is logged
explicitly in every trajectory ("v1 simplification, not a learned
classifier") rather than silently assumed.

**The provider is swappable and defaults to a non-LLM mock
(services/providers/).** `PROVIDER=mock` (default) runs the entire pipeline
with zero API calls and byte-identical output on every run — required for
judges to reproduce results from a clean environment with no credentials.
`PROVIDER=anthropic` / `PROVIDER=openai` swap in a real model via env vars
with no code changes. See docs/evaluation.md for what changes, and doesn't,
between the two.

**Verification checks one dimension in v1: factual grounding.** The brief
lists seven verification dimensions (identity, contradiction, style,
application, completeness, browser, factual). v1 implements factual
grounding only — the one directly measurable without a browser, a
multi-question application narrative, or a second human's writing sample to
compare style against. The other six require capabilities (application
narrative state, browser execution) that don't exist yet; adding them now
would be exactly the "fake integration presented as working" the ground
rules warn against.

## v2 addendum — Application Compilation

v2 adds one new pipeline (`services/application_engine/`) reusing v1's
retrieval and verification modules unmodified — only the context assembly
and output shape differ:

```
data/applications/iitacb_ceo/requirements.json   (real requirements + real human ground truth)
        |
        v
  intent_model.py  ---->  ApplicationRequirement[]
        |
        v
  assess.py: assess_baseline_plain / assess_baseline_rag / assess_identityos
        (each reuses services/qa_engine/{retrieval,verification}.py directly)
        |
        v
  bucketing.py: derive a FitBucket (met_or_better/partial/gap) from
  evidence_coverage + overall_confidence + cited-claim polarity —
  NOT from asking the provider to self-report a label (see below)
        |
        v
  scoring.py: score_application_system() -> agreement_rate +
  dangerous_overclaim_rate (docs/evaluation_v2.md)
```

**Why the fit label is derived, not self-reported.** An earlier design had
the provider emit its own `ASSESSMENT: MET` line. Two problems: the mock
provider is extractive and cannot follow that instruction at all, and even
with a real LLM, a self-reported label isn't independently checkable the
way a derived one is — the whole point of this project is not trusting an
agent's self-report of its own confidence. `bucket_from_signals()` is the
one place that decides, from signals the verifier already computed.

**Why the bucketing rule also checks claim polarity, not just coverage and
confidence.** Discovered as a real bug during v2's own eval run, not
designed in from the start — see docs/hot_take.md's v2 addendum. A claim
can be fully grounded and still be a "no."

## v3 addendum — Browser Automation

v3 adds one more pipeline (`services/browser_engine/`), reusing v1/v2's
retrieval + generation + verification unmodified for free-text fields —
only field detection, mapping, and the human-approval checkpoint are new:

```
BrowserController.open(url) -> observe()  (DOM inspection: label text +
  input type -> DetectedField[], packages/schemas/browser.py)
        |
        v
  field_mapper.map_field() per field, dispatched on field_type:
    text     -> known-profile lookup (name/email) or HALT
    select   -> lexical overlap between options and Digital Self facts
    textarea -> retrieve_hybrid() -> format_context() -> provider.complete()
                -> verify_answer()   [the exact v1/v2 pipeline, unmodified]
    checkbox -> deferred until every other field's confidence is known
        |
        v
  fill + re-observe -> BROWSER VERIFICATION: compare each field's live DOM
  value to the intended fill value (not just "did fill() raise")
        |
        v
  checkbox decision from aggregate confidence + verification
        |
        v
  agent.py: HALT FOR APPROVAL, always logged — submit only if the CALLER
  passed approve_submit=True; no code path lets the agent submit on its own
```

**Why the human-approval gate lives in `agent.py`, not the CLI script.**
Ground rule 4 ("keep consequential actions controlled through a sandbox or
simulation; add human approval before the action happens") is enforced at
the layer that actually calls `browser.click(submit_selector)`, not at the
UI wrapping it — `scripts/run_browser_demo.py`'s `--approve-submit` flag
is the only way a human ever sets that argument true, and
`services/evaluation/run_eval_browser.py` never does. This mirrors v2's
"derive, don't self-report" principle above: the checkpoint is a hard gate
in code, not a convention a caller is trusted to follow.

Full pipeline, results, and the two bugs found by reading v3's own
trajectory output: docs/evaluation_browser.md.

## What is explicitly NOT in v1, v2, or v3

- Multi-page navigation, file uploads, CAPTCHA/OTP/MFA handling
  (docs/roadmap.md v3.1+) — v3.0's synthetic form has none of these, so
  nothing has been built or tested against them yet.
- A real third-party browser target — v3.0 demonstrates against a local,
  offline, synthetic form the project controls, for the same reason v1/v2
  use the author's own documents rather than a scraped corpus.
- Multi-agent orchestrator, opportunity discovery, application strategy
  narrative planning (v4)
- Self-improvement / learning engine with counterfactual promotion (v4)
- Graph database, web UI, Next.js frontend (v5)
- Automatic belief inference from unstructured documents (v1/v2 hand-seed
  4 beliefs from already-ingested facts instead; deferred to v2.1)
- Clause-level negation detection (v2's fix is sentence-level — see
  docs/hot_take.md and docs/evaluation_v2.md's req13/req08 discussion)
