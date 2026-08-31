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
`PROVIDER=anthropic` / `PROVIDER=openai` / `PROVIDER=groq` swap in a real
model via env vars (groq is free, no credit card required)
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

## v3.1-v3.2 addendum — Security Policy Engine and Agent Auditor

v3.1 added four heuristic guardrails (anti-bot/CAPTCHA/MFA detection,
prompt-injection detection, a zero-evidence refusal, hidden-field
skipping), each living in whichever module first needed it
(`controller.py`, `field_mapper.py`). v3.2, built against a much larger
security specification the project owner provided in full (preserved
verbatim at docs/security_spec.md), centralizes them: `services/security/
policy_engine.py`'s `SecurityPolicyEngine` independently re-evaluates
every proposed action — regardless of what `field_mapper.py` decided —
against its own risk classification and confidence floor, and
`services/security/auditor.py`'s `AgentAuditor` is a second, genuinely
independent check (fabricated-citation detection, label-leak detection)
that the policy engine does not perform. Neither trusts field_mapper's
own v3.1 checks; a bug there can no longer silently skip the security
layer. Every decision is appended to an audit log, and submission is
blocked if that run's audit trail has any unresolved finding, even with
`approve_submit=True`. Most of the larger spec (identity-provenance
temporal validation, cross-application consistency, self-improvement CI,
domain/phishing validation, credential isolation, rollback) is
deliberately not built — each requires a capability this codebase doesn't
have anywhere else yet (versioned belief history, a multi-application
store, a persistent learning loop, real authenticated browsing, real
credential handling) — see docs/roadmap.md's v3.2 section for the
complete, itemized scoping decision. Full story, including a real bug
found while building the demo the spec itself required:
docs/evaluation_browser.md's v3.2 addendum.

## v4.0 addendum — Orchestrator

`services/orchestrator/router.py`'s `classify_intent()` is a heuristic
keyword/pattern match over free text (documented as such — same
simplification as v1's "classify" stage) that decides which of three
already-built agents a request goes to: QA (v1), application-fit (v2's
hybrid arm), or browser-fill (v3). `route_and_execute()` then actually
dispatches into the real functions — `answer_identityos()`,
`assess_identityos_hybrid()`, `run_application()` — not a fourth
reimplementation of any of them. The orchestrator's own routing decision
is written as its own `Trajectory` (stage `classify_intent`, then
`dispatch`), stored alongside the downstream agent's trajectory so a judge
can audit "why did this go here" independently of "what did the routed
agent do" (`make eval-orchestrator-demo`,
`data/evaluation/results/orchestrator_demo/`).

This is deliberately the narrow reading of PROMPT.md's orchestrator
("decide which agents are actually necessary," not "instantiate N agents
because the brief mentions them") — three real, useful routes, not a
larger roster with nothing yet built for the extra routes to lead to.

## v4.1 addendum — Learning Engine

`services/learning_engine/engine.py` runs a real
EXPERIENCE → HYPOTHESIS → COUNTERFACTUAL TEST → EVALUATION →
PROMOTE/REJECT loop against one already-instrumented question: is there a
lexical-evidence-coverage threshold below which swapping to semantic
retrieval is worth its known risk (the dangerous-overclaim finding from
v2.3/docs/evaluation_v2.md)? It reads the real, already-committed
`v2_semantic` per-requirement results (no new LLM calls), grid-searches
threshold candidates, and — critically — validates the promoted
threshold with **leave-one-out cross-validation**: for each requirement,
the threshold is chosen using only the *other* 13 requirements' outcomes,
then applied to the held-out one. This is the one evaluation in this whole
project that checks a decision rule against data it did not see while
being chosen, rather than measuring a fixed system against the same
benchmark it was designed against (a limitation named honestly in
docs/hot_take.md at nearly every version).

**The real result**: no threshold beats the hand-designed hybrid
heuristic (`retrieve_hybrid()`, v2.4) — every promoted candidate matches
its exact 0.714 agreement / 0.0 dangerous-overclaim rate, both on the
full 14-requirement fit and under leave-one-out validation. This is a
genuine negative-for-improvement result and a positive-for-validation one:
an automated search over a wider hypothesis space than the hand-designed
rule confirms hybrid was already at the ceiling a coverage-only signal can
reach here, rather than silently leaving a better rule undiscovered. A
real bug was caught building this (comparing a full-precision computed
rate against a pre-rounded JSON summary value produced a false "beats
hybrid" verdict) — fixed by deriving every baseline from unrounded
per-requirement counts; see docs/improvement_changelog.md's v4.1 entry.

Honestly scoped: this is a meta-learning policy over one signal and two
existing strategies, not a Digital Self mutation, and not a persistent
loop that keeps running and proposing its own next hypothesis — see
docs/roadmap.md's v4.1 section for exactly where that line is drawn.

## v4.2 addendum — Video Statement Generator

Many real applications ask for a video, not just text — a research-program
"introduce yourself" video, a fellowship pitch, an accelerator application
video. `services/video_engine/generate.py` handles this the same way v2.5
handles a cover letter: the identical section-planning + hybrid-retrieval
+ citation + verification pipeline
(`generate_video_statement_baseline_plain/baseline_rag/identityos`),
applied to a four-section pitch shape (introduction, motivation, key
achievement, closing) instead of a cover letter's shape. Real, measured
numbers (`make eval-video-statement`): evidence coverage 0.70 vs. 0.00 for
both baselines — lower than the cover letter's 0.91, honestly, because the
mock provider's extractive style matches these pitch-shaped prompts less
often; the gap is disclosed, not hidden.

**The scope boundary, stated as plainly as possible**: this module
generates a script, and optionally (`services/video_engine/render.py`,
`make render-video-statement-draft`) a narrated *draft* — generic text
slides plus synthesized narration, every slide carrying a burned-in
disclosure banner ("AI-DRAFTED SCRIPT — READ FOR TIMING ONLY — RECORD
YOURSELF FOR SUBMISSION"). It does not, and will not, generate a synthetic
likeness of the applicant — no cloned voice, no generated face, no
deepfake of any kind. Many programs require a video specifically because
they want to see and hear the real applicant, for the same authenticity
reason this project refuses to fabricate a fact anywhere else (this doc's
ETHICAL CONSTRAINT section). A synthetic stand-in would defeat that
requirement, not satisfy it — so the render step is a timing/content aid
for a human who will record themselves, never a submission-ready output.

The render step needs two optional system tools neither `make setup` nor
`make test` requires: `pico2wave` (`apt-get install libttspico-utils`) and
`ffmpeg`. `render_narrated_draft()` checks for both explicitly and raises
a clear, actionable error if either is missing, rather than failing deep
inside a subprocess call. A real bug was caught building this: the first
version wrote relative paths into ffmpeg's concat list, which ffmpeg
resolves against the list file's own directory, not the caller's cwd —
doubling the path and failing to open every segment. Fixed by writing
resolved absolute paths into the concat list. See
`docs/improvement_changelog.md`'s v4.2 entry.

## v4.3 addendum — first real third-party browser test, and two real bugs it found

Every prior browser-agent demonstration (v3.0-v3.2) ran against a local,
offline, synthetic form this project controls — a deliberate scoping
decision, not an oversight (see "What is explicitly NOT in" below). The
project owner asked directly whether the agent could detect fields on a
real third-party page (a HackerEarth hackathon-registration page) — a
genuine first, and it found two real things immediately:

**Bug 1 — a blocked page read as an empty one.** The target returned an
HTTP 403 (confirmed independently via plain `curl` with a normal
browser user-agent too, so not headless-detection specifically — a
WAF/anti-bot layer blocking the request outright) before any real content
loaded. `observe()` reported "0 fields, 0 errors" — indistinguishable
from "this page genuinely has no form," a real silent-failure mode.
**Fixed**: `controller.py`'s `open()` now keeps the `Response` object;
`observe()` flags any HTTP status >= 400, and, for the class of block page
that returns 200 with a JS challenge instead (e.g. a Cloudflare
interstitial), a title-phrase check
(`services/browser_engine/safety.py`'s `looks_like_blocked_page()` —
"403 forbidden," "just a moment," "attention required," the same
"check the TITLE, not the body" scoping already used for anti-bot/MFA
phrasing, for the same reason). `services/security/policy_engine.py`'s
`evaluate_page()` was updated to BLOCK on either new signal, not just the
three original anti-bot/CAPTCHA/MFA categories. Covered by a new local
fixture (`adversarial_blocked_page.html`, title-phrasing path) plus the
real, live 403 that motivated it (not part of the deterministic test
suite, for the obvious reason that a live third-party response can't be a
committed fixture).

**Bug 2 — a video narration script read `--` aloud as "hyphen hyphen."**
Found by ear in this project's own solution video, which used `--` as an
em-dash substitute in its narration text. **Fixed** in
`services/video_engine/render.py`'s `_clean_for_narration()`: strips
citation brackets and replaces `--`/em-dash/en-dash punctuation with a
comma before any text reaches `pico2wave`. The solution video was
re-rendered with the fix (4:27, down from 4:29 — the corrected punctuation
reads slightly faster, not the cause of the recut).

Neither bug is specific to real third-party sites or to this one video —
both are the same lesson this project keeps re-finding at a new layer
(docs/hot_take.md): a code path that looks correct against everything
it's been tested on can still have a real, silent gap the moment
something genuinely new runs through it.

## What is explicitly NOT in v1-v4.3

- Multi-page navigation, file uploads (docs/roadmap.md v3.3+) — v3.0's
  synthetic form has none of these, so nothing has been built or tested
  against them yet. CAPTCHA/MFA/anti-bot *detection* is built (v3.1-v3.2);
  a real OTP-entry channel or a solved CAPTCHA is out of scope by design
  (ground rule 3 permits detect-and-halt only).
- A real third-party browser target for filling/submitting — v3.0's
  canonical demo still runs against a local, offline, synthetic form the
  project controls, for the same reason v1/v2 use the author's own
  documents rather than a scraped corpus. v4.3 did point `observe()` (read-
  only field detection, nothing filled or submitted) at one real
  third-party page for the first time — see this doc's v4.3 addendum for
  what that found.
- A dynamic multi-agent roster beyond the 3-way orchestrator (v4.0) —
  opportunity discovery and a separate contradiction agent (v5)
- A *persistent* self-improvement loop that keeps running and proposes
  its own next hypothesis — v4.1 built one scoped, one-shot instance of
  the EXPERIENCE→HYPOTHESIS→COUNTERFACTUAL TEST→PROMOTE/REJECT loop,
  not an ongoing one
- A synthetic likeness (cloned voice or generated face) of the applicant
  in any video output — v4.2 deliberately stops at a script and a
  generic-slide narrated draft; see this doc's v4.2 addendum for why
- Graph database, web UI, Next.js frontend (v5)
- Automatic belief inference from unstructured documents (v1/v2 hand-seed
  4 beliefs from already-ingested facts instead; deferred to v2.1)
- Clause-level negation detection (v2's fix is sentence-level — see
  docs/hot_take.md and docs/evaluation_v2.md's req13/req08 discussion)
