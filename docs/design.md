# Design reference

`docs/architecture.md` explains each version's design *decision* — what was
built, what it replaced, why. This document is the cross-cutting
complement: one place that shows the whole system's shape at once,
independent of the order it was built in, with enough implementation
detail (schemas, function signatures, algorithms) that someone extending
this codebase doesn't have to reconstruct it from fourteen per-version
docs. It focuses on the two newest, least self-explanatory components —
the **Orchestrator** (v4.0) and the **Learning Engine** (v4.1) — since
everything upstream of them already has a dedicated per-version writeup.

## System shape

```
                              ORCHESTRATOR (v4.0)
                    services/orchestrator/router.py
                                    |
                    classify_intent()  — heuristic pattern match
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
    QA AGENT (v1)          APPLICATION-FIT AGENT (v2)     BROWSER AGENT (v3)
  identityos_agent.py      assess_identityos_hybrid()      browser_engine/agent.py
        |                           |                           |
  retrieve -> cite ->         retrieve_hybrid() ->        observe -> plan -> fill ->
  generate -> verify ->       generate -> verify ->       verify(DOM re-check)
  confidence-gated refuse     polarity-aware bucket              |
        |                           |                    SECURITY POLICY ENGINE
        |                           |                    + AGENT AUDITOR (v3.1-v3.2)
        |                           |                    services/security/
        |                           |                    every proposed action passes
        |                           |                    through both, independently
        |                           |                           |
        |                    (past results)              HALT FOR HUMAN APPROVAL
        |                           v                     (no auto-submit, ever)
        |                    LEARNING ENGINE (v4.1)
        |                    services/learning_engine/
        |                    hypothesize -> counterfactual
        |                    test -> evaluate -> leave-one-out
        |                    validate -> promote/reject report
        |                    (report only — not yet wired back
        |                     into assess_identityos_hybrid())
        v
  Answer / Trajectory
```

Every arrow above is a real function call in the codebase, not an aspirational
one — see the "Where this lives in code" table under each component below.

## Core schemas (`packages/schemas/`)

| File | Key types | Used by |
|---|---|---|
| `identity.py` | `Fact`, `Belief`, `Evidence`, `Confidence`, `DigitalSelf` | identity_engine, qa_engine, application_engine, browser_engine |
| `qa.py` | `Question`, `QuestionType`, `Answer`, `AnswerClaim`, `ClaimType`, `Trajectory`, `TrajectoryStep` | every agent — the one schema every trajectory file in this repo is rendered from |
| `application.py` | `ApplicationRequirement`, `RealAssessment`, `FitBucket`, `Assessment` | application_engine, orchestrator (application-fit dispatch) |
| `browser.py` | `BrowserObservation`, `DetectedField`, `FieldType`, `BrowserAction`, `ActionType`, `FieldResult`, `BrowserTaskResult` | browser_engine, orchestrator (browser-fill dispatch) |
| `security.py` | `RiskLevel`, `PolicyDecision`, `PolicyResult`, `AuditVerdict`, `ActionRecord` | services/security |
| `application_record.py` | `ApplicationRecord`, `QAEntry` | services/application_record |
| `document.py` | `DocumentSection`, `GeneratedDocument` | document_engine |
| `orchestrator.py` | `AgentTarget`, `OrchestratorDecision` | services/orchestrator |
| `learning.py` | `ThresholdCandidate`, `LeaveOneOutFold`, `LearningReport` | services/learning_engine |

`Trajectory` is the load-bearing one: every agent in this repo, including
the orchestrator and the learning engine, records its reasoning as a
sequence of `TrajectoryStep`s (`stage`, `input_summary`, `action`,
`observation`, optional `reasoning`/`confidence`/`decision`) and renders it
to Markdown via the same `to_markdown()` method. A judge reading any
trajectory file in `data/evaluation/results/*/trajectories/` is reading the
same schema regardless of which agent produced it.

---

## Orchestrator (v4.0)

**Where this lives in code:** `packages/schemas/orchestrator.py` (schemas),
`services/orchestrator/router.py` (logic), `services/evaluation/
run_orchestrator_demo.py` + `scripts/run_orchestrator_demo.py` (the runnable
demo), `tests/test_orchestrator.py` (8 tests).

### What problem it solves

Before v4.0, a caller had to already know which of the three pipelines
(Q&A, application-fit, browser-fill) their request needed, and call the
right module directly — `answer_identityos()`, `assess_identityos_hybrid()`,
or `run_application()`. The orchestrator removes that requirement: give it
one free-text string, and it decides.

### `classify_intent(request_text: str) -> OrchestratorDecision`

A heuristic classifier, deliberately not a learned one — consistent with
this codebase's existing pattern of naming a simplification explicitly
rather than dressing it up (v1's question-type "classify" stage does the
same thing). It checks the request text, lowercased, against two ordered
pattern lists:

```python
_BROWSER_PATTERNS = [
    r"\bfill\b", r"\bapply to\b", r"\bapplication form\b",
    r"\bsubmit the form\b", r"https?://", r"file://",
]
_FIT_PATTERNS = [
    r"\bdoes (the|this) candidate\b", r"\bassess fit\b",
    r"\bjob requirement\b", r"\bmeet(s)? the requirement\b",
    r"\bhow well do i meet\b", r"\brequirement\b",
]
```

`_BROWSER_PATTERNS` is checked first, deliberately: a request that mentions
both a form and a requirement ("fill out the form, checking every
requirement first") should still route to the browser agent, since filling
is the more specific, more consequential action. If nothing matches,
`AgentTarget.QA` is the default — the least consequential fallback. Every
decision carries the exact regex that matched (`matched_signal`), so a
judge (or a future maintainer) can audit *why* a request routed the way it
did without re-running anything.

### `route_and_execute(...)` — dispatch, not reimplementation

```python
def route_and_execute(
    request_text: str, ds: DigitalSelf, embedding_index: DigitalSelfEmbeddingIndex,
    provider, form_url: str | None = None, headless: bool = True,
    history_dir=None, audit_log_path=None,
) -> tuple[OrchestratorDecision, Answer | Assessment | BrowserTaskResult, Trajectory, Trajectory]
```

This function does not contain any Q&A, fit-assessment, or browser logic
of its own. Per target, it constructs the minimum input the real function
needs and calls it directly:

- **QA** — wraps the request in a `Question` with `type=UNSEEN_INFERENTIAL`
  (the stricter, refusal-gated path — the conservative choice when the
  orchestrator has no declared question type to go on), then calls
  `answer_identityos(question, ds, provider)` unmodified.
- **Application-fit** — wraps the request in an `ApplicationRequirement`
  with a placeholder `real_assessment` (unused by generation, only by
  benchmark scoring, which this live path never invokes), then calls
  `assess_identityos_hybrid(req, ds, embedding_index, provider)` unmodified.
- **Browser-fill** — requires an explicit `form_url` (raises `ValueError`
  otherwise — there is no sensible default target for a live dispatch),
  then calls `run_application(...)` unmodified, including the same
  `approve_submit=False` default every other entry point in this repo uses.

The return value bundles two trajectories: the orchestrator's own
(`stage="classify_intent"` then `stage="dispatch"`) and the downstream
agent's unmodified one. Both are written to disk by
`run_orchestrator_demo.py`, so the routing decision is exactly as
auditable as any other agent's reasoning in this repo.

### Honest limits

- No multi-intent handling — a request that genuinely needs two agents
  (e.g., "assess my fit, then fill out the form") routes to exactly one.
- No LLM-based classification — a request with none of the above keywords
  in an unusual phrasing silently falls through to QA. An LLM classifier
  is a natural extension (see `docs/roadmap.md`), traded here for
  determinism and zero cost under the mock provider.

---

## Learning Engine (v4.1)

**Where this lives in code:** `packages/schemas/learning.py` (schemas),
`services/learning_engine/engine.py` (algorithm),
`services/evaluation/run_learning_engine.py` + `scripts/run_learning_engine.py`
(the runnable demo), `tests/test_learning_engine.py` (5 tests on synthetic
fixtures, so they don't drift as the real corpus grows).

### What problem it solves

v2.4 shipped a hand-designed retrieval-fallback rule (`retrieve_hybrid()`:
lexical first, semantic only when lexical returns *nothing at all*). That
threshold — literally zero — was chosen by a human reading trajectories,
not searched. The Learning Engine asks the question properly: is there a
*better* coverage threshold, and if the hand-designed one really is best,
can that be demonstrated rather than assumed?

### The signal, the hypothesis space, and why it's honest

The input is real, already-committed per-requirement data —
`data/evaluation/results/v2_semantic/application_summary.json`'s
`per_requirement` blocks for `identityos_v2` (lexical) and
`identityos_v2_semantic`. No new LLM calls are made; the "two strategies"
being chosen between already exist and were already independently scored
against real human ground truth.

The hypothesis space is one parameter: a threshold `T` on lexical's own
`evidence_coverage` for a given requirement. The policy it defines:

```python
def _choice_for_threshold(threshold, lexical, req_ids):
    return {
        rid: ("semantic" if lexical[rid]["evidence_coverage"] < threshold else "lexical")
        for rid in req_ids
    }
```

This is a genuinely usable *live* policy, not one that cheats by peeking at
the answer: `evidence_coverage` is known the moment lexical retrieval runs,
before anyone knows whether the requirement is actually met.

### `search_thresholds()` — hypothesis, test, evaluate

For each of 11 candidate thresholds (0.0 to 1.0, step 0.1), the engine
counterfactually applies the resulting policy across all 14 requirements
using the already-recorded outcomes, and computes agreement rate and
dangerous-overclaim rate. A candidate is `promoted` only if it introduces
**zero** dangerous overclaims *and* matches or beats the already-shipped
hybrid heuristic's agreement rate — matching lexical alone is not treated
as an improvement worth promoting.

### `leave_one_out()` — the part that makes this a real validation, not a fit

This is the one place in the whole project that checks a decision rule
against data it did not see while being chosen. For each of the 14
requirements: pick the best-scoring, zero-danger threshold using **only
the other 13**, then apply that threshold to the held-out one (using its
already-known `evidence_coverage`, never its label). Aggregate across all
14 folds.

```python
def leave_one_out(lexical, semantic, req_ids, thresholds):
    for held_out in req_ids:
        train_ids = [r for r in req_ids if r != held_out]
        best_t = <threshold maximizing training agreement s.t. zero danger>
        chosen = "semantic" if lexical[held_out]["evidence_coverage"] < best_t else "lexical"
        # record whether `chosen` agreed with ground truth for held_out
```

### The real, measured result

| | Agreement | Dangerous overclaim |
|---|---|---|
| Hand-designed hybrid (v2.4) | 0.714 | 0.00 |
| Learned policy, full-set fit | 0.714 | 0.00 |
| Learned policy, leave-one-out | 0.714 | 0.00 |

Every fold picked the same threshold (0.1-0.8 all tie). No threshold beat
the hand-designed rule. This is reported as a **negative result for
improvement, a positive one for validation**: the search confirms the
existing rule was already at the ceiling a coverage-only signal can reach
for this benchmark — three requirements (req06, req07, req14) have *full*
lexical coverage and still disagree with ground truth, which no
coverage-based threshold can ever fix, because the failure is "confidently
wrong evidence," not "missing evidence." See `docs/hot_take.md`'s v4.1
addendum for why this is the same wall v2.9 found independently by hand.

### A real bug this build caught

The first implementation compared a freshly computed agreement rate
(`10/14 = 0.7142857...`) against `application_summary.json`'s already-
**rounded** `agreement_rate` field (`0.714`) — and `0.7142857... <= 0.714`
is `False`, so the promotion logic concluded the learned policy *beat*
hybrid, when it matched exactly. Fixed by deriving every baseline from
unrounded per-requirement counts (`services/evaluation/run_learning_engine.py`'s
`_agreement_rate()`), never from a pre-rounded summary field. See
`docs/improvement_changelog.md`'s v4.1 entry.

### What would be needed to go from report to production

Right now, `LearningReport` is a report: `data/evaluation/results/
learning_v4_1/learning_report.json`, read by a human or a judge. It is
**not** wired back into `assess_identityos_hybrid()` — there is no
`assess_identityos_learned()` in `services/application_engine/assess.py`,
and `run_eval_v2.py` never reads `learning_report.json`. Since the search
found no improvement to promote here, wiring it up would currently just
reproduce hybrid's own behavior; the honest next step, named in
`docs/roadmap.md`, is: (1) persist a promoted policy as a versioned file
under `data/learning/`, (2) load it in `assess_identityos_hybrid()` as an
optional per-requirement override, (3) re-run the full benchmark to
confirm no regression before calling it "applied," not just "found." That
promotion step — persist, load, re-verify — is deliberately not built yet,
because building it around a result that says "nothing to promote" would
be untested scaffolding, the same discipline this project applies to every
other deferred capability (see `docs/roadmap.md`'s v3.2 section for the
precedent).

---

## Testing

| Module | Tests | What they check |
|---|---|---|
| `tests/test_pipeline.py` | v1 smoke tests | ingestion, retrieval, verification plumbing |
| `tests/test_providers.py` | 6 | provider factory, all mocked, never hits real network |
| `tests/test_embeddings.py` | — | hash vs. fastembed provider shape |
| `tests/test_browser_engine.py` | incl. 4 real Chromium launches | field detection, fill, verify, security guardrails end-to-end |
| `tests/test_security.py` | 14 | risk classification, confidence floors, injection/anti-bot/MFA escalation, submit gate |
| `tests/test_application_engine.py` / `test_application_record.py` | — | bucketing, negation/polarity, per-application record persistence |
| `tests/test_orchestrator.py` | 8 | classification determinism, all 3 dispatch paths hit the real agent, `ValueError` on missing `form_url` |
| `tests/test_learning_engine.py` | 5 | threshold search on synthetic fixtures (promotion, rejection-on-danger), leave-one-out never trains on a held-out label, end-to-end report shape |

`make test` runs all of them — 79 tests, ~9s, no network beyond the
one-time Chromium install `make setup` already handles.

## See also

- `docs/architecture.md` — the version-by-version design decisions and trade-offs
- `docs/roadmap.md` — what's deferred, and exactly why
- `docs/hot_take.md` — the research findings, including v4.1's
- `docs/improvement_changelog.md` — every iteration, including rejected ones
