# IdentityOS — v3.3

**An autonomous representative that answers application questions,
assesses job-requirement fit, generates application documents, and fills
(never submits without a human) real application forms in a browser, on a
person's behalf — with evidence, calibrated confidence, and refusal
instead of fabrication.**

Built for the micro1 Agentic Workflows Hackathon, against the full brief
preserved in `PROMPT.md`. This repo builds v1 (Q&A), v2 (requirement-fit
assessment against a real, adjudicated application, iterated through
v2.4), v2.5-v2.9 (document generation, two corpus authoring corrections,
and two diagnosed-but-rejected retrieval experiments that together
identify a real boundary of lexical retrieval), v3.0 (a Playwright
browser agent that fills and browser-verifies a form, gated by a literal,
unconditional human-approval checkpoint before any submit), and v3.1-v3.2
(anti-bot/MFA/prompt-injection guardrails centralized into an independent
Security Policy Engine + Agent Auditor control plane, built against a
larger security spec the project owner provided — preserved verbatim at
[docs/security_spec.md](docs/security_spec.md) — plus per-application
answer records for interview prep), and v3.3 (a free, no-credit-card real
LLM provider — Groq — and this project's first-ever real-model run,
which found and fixed a third shared-infrastructure bug and honestly
disclosed hitting the provider's free daily quota mid-verification) of
that brief — see [docs/roadmap.md](docs/roadmap.md) for what's deferred
to v3.4-v5 and why. Prior versions frozen at `../identityos-v1/`,
`../identityos-v2/`, `../identityos-v2.1/`, `../identityos-v2.2/`,
`../identityos-v2.3/`, `../identityos-v2.4/`, `../identityos-v2.5/`,
`../identityos-v2.6/`, `../identityos-v2.7/`, `../identityos-v2.8/`,
`../identityos-v2.9/`, `../identityos-v3.0/`, `../identityos-v3.2/`.
(v3.1's guardrails were superseded by v3.2's centralized control plane in
the same work session before a separate snapshot was taken.)

## Who has this problem, and why it's worth solving

Anyone who repeatedly applies for opportunities that ask about *them*
specifically — job seekers, PhD/fellowship applicants, grant applicants.
Every application mixes three kinds of questions: factual ones (easy),
never-before-answered ones like *"what failure taught you the most?"*
(no source sentence exists to retrieve), and adversarial-shaped ones that
invite overclaiming (*"describe your patent"* when the real inventorship is
shared 75/25). A plain LLM call, or an LLM with the resume pasted in,
answers all three the same way: confidently, and without provenance.
Full case: [docs/problem_statement.md](docs/problem_statement.md).

The identity source documents in this repo (`data/identity_sources/`) are
the author's own real resume and CEO-candidacy dossier — including the real
patent with its real 75/25 shared inventorship, and a real, self-admitted
career gap — used with the data owner's own consent, because this project
is solving its own author's actual bottleneck.

## What v1 actually is

```
structured sources -> Facts + Beliefs (provenance + confidence)
        -> lexical retrieval -> citation-tagged context
        -> generation (cite inline) -> per-sentence grounding verification
        -> confidence-gated refusal
        -> scored against two fair baselines on a 19-question benchmark
```

Full architecture and every design trade-off: [docs/architecture.md](docs/architecture.md).

## Quickstart (zero API keys required)

```bash
git clone <this repo> && cd identityos
make setup            # venv + deps
make eval-mock         # v1: builds Digital Self, runs all 3 systems on 19 Q&A questions
make eval-v2-mock      # v2: runs baselines + lexical identityos_v2 on 14 real requirements
make eval-v2-semantic  # v2.3/v2.4: adds the semantic + hybrid retrieval comparison arms
make eval-documents    # v2.5: generates an actual cover letter with each system
make eval-browser      # v3.0: fills + browser-verifies a local synthetic application form, halts before submit
make eval-security-demo # v3.2: combined attack demo (injection/anti-bot/off-topic) alongside legitimate fields
```

Expect each in under 10 seconds, $0 cost — the default `PROVIDER=mock` (LLM)
and `EMBEDDING_PROVIDER=hash` (embeddings) are deterministic, dependency-light
stand-ins built exactly so judges can reproduce the main result from a clean
environment (see docs/evaluation.md, docs/evaluation_v2.md,
docs/evaluation_documents.md, and docs/evaluation_browser.md for what that
does and doesn't prove).
`make eval-v2-semantic` / `make eval-documents` / `make eval-browser`
download a ~65MB ONNX embedding model on first run (fastembed, no API key,
no torch); `make eval-browser` additionally needs a one-time
`playwright install chromium` (~300MB, handled by `make setup`) — still
$0, but does need one-time network access. Output per run:
- `data/evaluation/results/<tag>/summary.json` (v1), `application_summary.json` (v2), `document_summary.json` (v2.5), or `browser_result.json` (v3)
- `data/evaluation/results/<tag>/answers.json` (v1) or `application_answers.json` (v2)
- `data/evaluation/results/<tag>/documents/<system>.md` — the actual generated cover letters (v2.5)
- `data/evaluation/results/<tag>/trajectories/*.md` — one file per
  (question-or-requirement-or-section-or-form-fill, system) pair,
  human-readable, per the hackathon's trajectory deliverable

To get a qualitative read with a real model: copy `.env.example` to `.env`,
set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GROQ_API_KEY`
([free, no credit card](https://console.groq.com/keys) — the easiest way
to try this without paying for anything), then `make eval-real` / `make
eval-v2-real` / `make eval-documents-real-groq` / `make
eval-browser-real-groq` (or swap `groq` into any `make eval-*-real*`
target's `PROVIDER` argument — see `services/providers/groq_provider.py`,
which reuses the `openai` client pointed at Groq's OpenAI-compatible
endpoint, no new dependency).

Run the smoke test suite: `make test` (66 tests, ~6s including several real
Chromium launches for v3's end-to-end regression tests, no keys/downloads
beyond the one-time Chromium install needed).

## Results (reference runs, `PROVIDER=mock`)

**v1 — Q&A (19 questions):**

| Metric | baseline_plain | baseline_rag | identityos_v1 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.95** |
| Unsupported claim rate | 1.00 | 1.00 | **0.05** |
| **Identity Fidelity Score** | 0.20 | 0.20 | **0.96** |

Full breakdown, the four hard cases verbatim, and an honest limitation of
this offline run: [docs/evaluation.md](docs/evaluation.md).

**v2 — requirement-fit assessment (14 real requirements, real human ground truth):**

| Metric | baseline_plain | baseline_rag | identityos_v2 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.83** |
| Assessment agreement rate | 0.07 | 0.07 | **0.43** |
| Dangerous overclaim rate (of 4 non-MET requirements) | 0.00* | 0.00* | **0.00** |

*Trivial — both baselines say "gap" to every requirement regardless of
truth, so they cannot overclaim, but they also can't answer anything
correctly except by accident. identityos_v2's dangerous-overclaim rate
started at 0.25 (the system briefly overclaimed the single most important
requirement — a real, admitted governance gap — because grounding and
polarity got conflated), reached 0.00 after a v2.1 corpus-completion pass
fixed the remaining case as a side effect, and agreement rate improved
further in v2.2 (clause-level negation detection). Full story:
[docs/evaluation_v2.md](docs/evaluation_v2.md).

**v2.3 — embedding retrieval, kept as a comparison arm, not the default:**

| Metric | identityos_v2 (lexical, shipped default) | identityos_v2_semantic (fastembed) |
|---|---|---|
| Evidence coverage | 0.83 | **1.00** |
| Assessment agreement rate | **0.43** | 0.36 |
| Dangerous overclaim rate | **0.00** | 0.25 |

Real semantic retrieval fixed the two requirements it targeted (one fully,
one partially) — and reintroduced a dangerous overclaim elsewhere, because
higher recall pulled in more topically-adjacent (but off-topic) evidence
that the polarity check from v2.2 couldn't tell apart from the real thing.
We did not tune this until it looked better; at the time, lexical retrieval
stayed the default. Full trade-off: [docs/evaluation_v2.md](docs/evaluation_v2.md).

**v2.4-v2.9 — hybrid retrieval, now the recommended strategy:**

| Metric | identityos_v2 (lexical) | identityos_v2_semantic (fastembed) | identityos_v2_hybrid |
|---|---|---|---|
| Evidence coverage | 0.85 | 0.99 | **0.99** |
| Assessment agreement rate | 0.57 | 0.64 | **0.71** |
| Dangerous overclaim rate | **0.00** | 0.75* | **0.00** |

*Re-measured after v3.0 fixed a shared MockProvider bug (below) — was
0.50 before the fix, a previously-masked weakness in a system that was
never the shipped default. Full story: [docs/evaluation_v2.md](docs/evaluation_v2.md).

Diagnosing *why* v2.3 regressed (noise only appeared when semantic
overrode a working lexical answer, never when filling a real gap) led
directly to the fix: lexical first, semantic only as a fallback when
lexical finds nothing. Verified requirement-by-requirement, not assumed —
all 12 requirements lexical could already answer are byte-identical to
pure lexical output. Two consecutive corpus authoring corrections (v2.6,
v2.7 — see below) then raised hybrid's agreement rate from 0.50 to 0.71
while its dangerous-overclaim rate held at 0.00 through both real corpus
changes — the clearest evidence yet the fallback-only design isn't fit to
one snapshot of data. identityos_v2_semantic's dangerous-overclaim rate,
by contrast, *worsened* under the same corpus changes (0.25 -> 0.50, on
different requirements each time), which is why it stays a comparison arm,
never the shipped default. v2.8 then diagnosed and tested the obvious next
fix for two remaining mismatches (require 2+ shared tokens for lexical
retrieval) — it fixed those two and pushed dangerous overclaim rate to
0.50 by breaking two others that relied on the exact same weak-match
mechanism. **Not shipped**, kept as a documented negative result. v2.9
tried the fix v2.8 actually pointed to (weight the polarity vote by
citation relevance, not a blanket exclusion) two different ways — both
tested against the full benchmark, both rejected: one had no effect
(reordering doesn't change what's *included*), the other fixed one
requirement and turned req14, the single highest-stakes case in the whole
benchmark, into a dangerous overclaim. Two independent fixes failing the
same way is itself the finding: lexical relevance scoring has a real
ceiling here, not a tuning problem. Full story: [docs/evaluation_v2.md](docs/evaluation_v2.md).

**v2.5-v2.7 — document generation, the first real generated artifact:**

| Metric | baseline_plain | baseline_rag | identityos_v2_5 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.91** |
| Unsupported claim rate | 1.00 | 1.00 | **0.10** |
| Repeated-evidence rate (narrative diversity across sections) | n/a | n/a | **0.39** |

A 4-section cover letter, generated with the same hybrid retrieval and
verification as v2 plus a simple narrative-state rule (prefer not citing
the same fact twice across sections). Reading the actual generated letter
— not just its passing score — found a genuinely new failure mode: real,
grounded evidence can still be the *wrong scope* for the document (in this
case, strategy narrative written for one specific prior job application,
showing up in what was supposed to be a generic letter). v2.6 traced the
root cause to an actual authoring error (five bullets conflating general
statements with role-specific comparisons in one sentence, not a missing
classifier) and fixed it in one source file — verified it improved v2's
own numbers as a side effect, not just the letter. Re-reading the fixed
letter found a near-identical mistake in a *different* source file; v2.7
applied the identical fix there too, and re-reading again confirmed the
letter is now clean of every flagged phrase across both rounds. Full
story, and the actual generated letters: [docs/evaluation_documents.md](docs/evaluation_documents.md).

**v3.0 — browser automation, halted before submit:**

| Metric | Value |
|---|---|
| Fields detected / filled | 6 / 6 |
| Fields browser-verified (DOM value matches intended fill) | **6 / 6** |
| Avg. evidence coverage (free-text fields) | **1.00** |
| Avg. confidence (fillable fields) | **0.93** |
| Halted for approval / Submitted | **true / false** |

A real Playwright agent (`services/browser_engine/`) opens a local,
offline, synthetic application form, detects all four field types the
brief names (text, textarea, select, checkbox) via DOM inspection —
generalized, not hard-coded to this form's markup — maps each to Digital
Self data (reusing v1/v2's hybrid retrieval and verification unmodified
for free-text fields), fills it, re-observes the live DOM to verify the
value actually stuck, and **halts before any submit**: there is no code
path where the agent can decide on its own to click submit — a human must
explicitly pass `--approve-submit`, which the eval harness never does.
This is ground rule 4 ("sandbox consequential actions, add human approval
before the action happens") implemented literally, not just described.

The first run reported only 4/6 fields verified. Reading the actual
trajectory — the same discipline behind every other finding in this
project — found two real bugs: a select-field verification mismatch
(comparing an option's underlying value against its visible label text),
and a systemic bug in the shared `MockProvider` test harness that had been
silently present since v2.0 (its prompt parser only recognized v1's exact
`"QUESTION:"` header, so v2/v2.5/v3's differently-labeled prompts fell
through to a generic path that could leak label text into generated
answers when retrieval was already weak). Both fixed at the root; every
earlier eval suite was re-run afterward to check for drift, not assumed
side-effect-free — the only real change was `identityos_v2_semantic`'s
already-worst dangerous-overclaim rate getting honestly worse (0.50 ->
0.75), a previously-masked weakness in a system that was never shipped as
the default. Full story: [docs/evaluation_browser.md](docs/evaluation_browser.md).

**v3.1 — anti-bot, MFA/OTP, and prompt-injection guardrails**, built
before the first real-LLM run: the agent now detects a CAPTCHA/anti-bot
widget or MFA/OTP phrasing on the page and halts the entire task before
touching any field; detects a prompt-injection pattern in a field's own
label and halts that field without ever passing the label into an LLM
prompt; refuses to fabricate an answer for a field with zero real
evidence behind it (the general mechanism that also catches an off-topic
decoy question, without hand-coding it); and never fills a hidden
honeypot field. All four are heuristic/pattern-based, not a learned
classifier — disclosed, not hidden — and verified not to change v3.0's
reference numbers. Full story: [docs/evaluation_browser.md](docs/evaluation_browser.md)'s v3.1 addendum.

**v3.2 — Security Policy Engine, Agent Auditor, and per-application
records**, built against a much larger security spec the project owner
provided in full (preserved verbatim at
[docs/security_spec.md](docs/security_spec.md)): v3.1's checks were
scattered across two modules; v3.2 centralizes them into an independent
`SecurityPolicyEngine` that every proposed action passes through
regardless of what the field-mapping logic decided, plus a second,
independent `AgentAuditor` that checks two things the policy engine does
not (fabricated evidence citations, label-leak in generated text), and an
append-only audit log. A single demo form
(`adversarial_mixed.html`) combines two legitimate fields with a
prompt-injection attempt, an identity-verification question, and an
off-topic decoy in one pass — real, recorded output shows both legitimate
fields filled and verified while all three attacks are detected, explained,
and halted, per docs/security_spec.md's own demand for exactly this kind
of demonstration (`make eval-security-demo`). Building that demo surfaced
a real bug — a page-level check that scanned the whole page body would
have halted an entire form over one field's wording — fixed to scan only
the page title. Also added: `ApplicationRecord`, saved automatically for
every filled application, so the questions asked and answers given are
there to check before an interview. Most of the larger spec (self-improvement
CI, cross-application dedup, phishing/domain validation, credential
isolation, rollback) is deliberately not built — each needs a capability
(a persistent learning loop, a multi-application store, real authenticated
browsing) this codebase doesn't have anywhere else yet; named explicitly,
not silently dropped. Full story:
[docs/evaluation_browser.md](docs/evaluation_browser.md)'s v3.2 addendum,
[docs/roadmap.md](docs/roadmap.md)'s v3.2 section.

**v3.3 — the first real-model run this project has ever done**, using a
free, no-credit-card provider (`PROVIDER=groq`, `openai/gpt-oss-120b` via
Groq's OpenAI-compatible endpoint — get a key at
[console.groq.com/keys](https://console.groq.com/keys)):

| Metric | baseline_plain | baseline_rag | identityos_v1 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | 0.78 |
| Unsupported claim rate | 1.00 | 1.00 | 0.22 |
| Refusal count | 0 | 0 | 5 |
| **Identity Fidelity Score** | 0.15 | 0.20 | **0.824** |

The core thesis holds with a real model (0.824 vs. 0.15/0.20), and it
also delivered on exactly what the mock provider always said it
couldn't: given zero context, `baseline_plain` fabricated a complete fake
patent number with four paragraphs of invented technical detail, and a
fake three-year nonprofit leadership role with fabricated growth
statistics — while answering a differently-worded version of that same
underlying fact the *opposite* way in the same run. The hand-authored
hard-case detector (tuned to the mock provider's exact phrasing) missed
both fabrications — a real, previously-only-predicted blind spot, now
measured. And reading `identityos_v1`'s own trajectories found a real,
root-cause bug: the citation-parsing regex only ever matched the mock
provider's exact bracket format, so a real model's `[ id ]`/`[id1;
id2]`/`【id】` formatting silently failed to parse, dragging a **correct,
honestly-hedged** answer to the single highest-stakes question in the
benchmark below the refusal threshold for the wrong reason. Fixed at the
root, every mock-provider suite re-verified byte-identical afterward;
offline re-verification of the same real-model outputs already collected
showed 4 of 5 refusals were pure artifacts of the bug (refusal count 5 ->
1, IFS 0.824 -> 0.838). Also found: the model is a reasoning model
burning most of its token budget on hidden reasoning by default (585 of
600 tokens on one call) — `reasoning_effort="low"` cut that 5-25x with no
quality loss and is now the provider's default, though the *first* (less
efficient) run had already consumed nearly this project's entire Groq
free-tier daily allowance, honestly disclosed rather than hidden. Full
story: [docs/evaluation.md](docs/evaluation.md)'s v3.3 section,
[docs/hot_take.md](docs/hot_take.md)'s v3.3 addendum.

## Improvement changelog

[docs/improvement_changelog.md](docs/improvement_changelog.md) — baseline
through final for every version, including experiments we removed or that
stayed only partially fixed: a scoring rule fooled by the mock provider, a
process mistake where a background research agent overstepped its brief
mid-v1-build, (v2) a bucketing rule that overclaimed a real admitted gap
until a negation check was added, (v3.0) two real bugs — a select-field
verification mismatch and a shared MockProvider parsing bug dating to
v2.0 — both found by reading the browser agent's own trajectory output,
and (v3.2) a page-level security check that would have halted an entire
form over one ordinary field's wording, found by building the combined-attack
demo the security spec itself asked for, and (v3.3) a third shared
citation-parsing bug — tuned to the mock provider's exact bracket format
for nine versions — found on this project's first-ever real-model run
(documented, not hidden).

## Main failure mode / hot take

The same underlying mistake, found three times, independently: grounding
verification checks whether a claim traces to evidence, not what the claim
actually *means*, or how solid the retrieval feeding it really was. v1: a
well-cited, high-confidence answer can still be off-topic (confidence stood
in for relevance it never measured). v2.0-2.1: a well-cited, high-confidence
answer can still be a "no" (confidence stood in for polarity it never
measured) — caught on the single highest-stakes requirement in a real
application. v2.3: "smarter" embedding retrieval made the polarity check
*worse*, because a safety check tuned against one retrieval method's error
profile isn't automatically safe against a different one. v2.4: diagnosing
*why* — the noise only ever overrode working answers, never filled real
gaps — produced a fix (semantic as a fallback only) that beat every other
system and was verified requirement-by-requirement, not assumed. v2.5: the
same substitution once more, at a fourth level — grounded and true isn't
the same as *in scope for this document*; a real, correctly-cited fact can
still be narrative written for a different, specific context. v2.6: the
fix wasn't a smarter classifier, it was correcting an actual authoring
mistake — and doing so consistently (all five affected bullets, not just
the visible one) is what separates a correction from tuning a benchmark.
v2.7: applying the identical correction to a second file, found by
continuing to read the output after already believing the problem was
solved, is what actually demonstrates the fix generalizes rather than
happening to work once. v2.8: the sharpest version of this yet — the same
weakly-relevant evidence that was noise for one requirement was the only
thing keeping a *different* requirement honest, at the same retrieval
threshold. "This match looks noisy" and "matches like this are noise in
general" are different claims, and the difference only shows up when you
test the fix against everything, not just the case that motivated it.
v2.9: tried the actual fix v2.8 called for, twice, both ways rejected on
the same full-benchmark test — a lexical relevance score just isn't the
same signal as "which fact actually settles this question," and no amount
of reweighting changes that. v3.0: the same underlying mistake found one
layer down, in the evaluation harness itself rather than the pipeline — a
mock-provider parser built and validated against one caller's prompt
shape quietly stopped being general the moment a second caller used a
different one, and it took three versions and a browser agent's own field
labels to finally produce a case weak enough to expose it. v3.3: the
identical lesson one layer deeper still — the citation-parsing regex was
validated against exactly one LLM backend (the deterministic mock) for
nine straight versions, and it took this project's first-ever real-model
run to discover that a real model's bracket formatting had been silently
unparseable the entire time, dragging a correct, well-grounded answer to
the single highest-stakes question in the v1 benchmark into an
unnecessary refusal. A codebase's zero-cost, always-green reference path
being green is not the same claim as "this code has actually been
exercised" — the gap between them only shows up the first time something
outside that path runs. Full writeup, including what's still unfixed:
[docs/hot_take.md](docs/hot_take.md).

## Solution video

[docs/media/solution_video.mp4](docs/media/solution_video.mp4) (3:41).
Problem and the real fabricated baseline output from v3.3's real-model run,
Digital Self ingestion, cited-and-verified Q&A, the real v3 browser agent
filling a real form (actual Playwright screenshots from a live run) through
to the human-approval halt, the final comparison table, the single
biggest changelog jump, one rejected experiment (v2.8), and the hot take.
Narration is synthesized speech (espeak-ng) with captions, not a human
recording — every on-screen number and quoted line is pulled verbatim from
a file already in this repo (docs/hackathon_compliance_check.md traces
each one).

## Hackathon compliance self-check

Re-verified against the hackathon PDF's rubric, ground rules, and
deliverables list after every version: [docs/hackathon_compliance_check.md](docs/hackathon_compliance_check.md).

## AI tool use disclosure

Built with Claude Code (Claude Sonnet 5) as the coding agent throughout.
Full disclosure, and what "agent-use evidence" means in this repo:
[docs/agent_disclosure.md](docs/agent_disclosure.md).

## Repository map

```
docs/                  problem statement, architecture, roadmap, evaluation (v1, v2, documents, browser),
                        changelog, research hypotheses, hot take, demo script, agent disclosure,
                        security_spec.md (the full guardrail spec, preserved verbatim)
packages/schemas/      typed Fact / Belief / Evidence / Question / Answer / Trajectory /
                        ApplicationRequirement / Assessment / FitBucket /
                        DocumentSection / GeneratedDocument /
                        BrowserObservation / BrowserAction / FieldResult / BrowserTaskResult /
                        RiskLevel / PolicyDecision / PolicyResult / AuditVerdict / ActionRecord /
                        QAEntry / ApplicationRecord
services/identity_engine/    ingestion + belief seeding + versioned storage
services/providers/          pluggable LLM backend: mock (default) / openai / anthropic / groq (free)
services/embeddings/         pluggable embedding backend: hash (default) / fastembed (v2.3)
services/qa_engine/          v1+: lexical, semantic + hybrid retrieval, the two
                              baselines, the IdentityOS agent, verification
services/application_engine/ v2: requirement-fit assessors (lexical, semantic,
                              hybrid) + polarity-aware bucketing
services/document_engine/    v2.5: section-planned cover-letter generation +
                              narrative-state (avoid repeating evidence)
services/browser_engine/     v3.0-v3.1: Playwright controller + field mapping +
                              human-approval-gated form-fill agent + guardrails
services/security/           v3.2: SecurityPolicyEngine + AgentAuditor + audit log —
                              the centralized control plane every browser action passes through
services/application_record/ v3.2: per-application question/answer records for interview prep
services/evaluation/         scoring + all four eval harnesses + the security demo
data/identity_sources/       the real source documents (owner's own, consented)
data/applications/           the real 14-requirement application + its real human ground truth,
                              local synthetic forms for the v3 browser demo and adversarial tests,
                              history/ — saved per-application answer records (v3.2)
data/evaluation/              question bank + every eval harness's results/trajectories/documents
data/.embedding_cache/        fastembed's downloaded model (gitignored, regenerable)
scripts/               the commands judges actually run
tests/                 smoke tests (make test)
PROMPT.md              the full original design brief, unabridged
```

## Ground-rules compliance (hackathon requirement)

- Consequential actions: the browser agent can fill a form but has no
  code path to submit one on its own — `services/browser_engine/agent.py`
  submits only if the caller explicitly passes `approve_submit=True` AND
  `SecurityPolicyEngine.evaluate_submit()` finds no unresolved BLOCK/
  ESCALATE finding anywhere in the run's audit trail (v3.2 — a caller
  can't override a live security finding just by passing the flag).
  `scripts/run_browser_demo.py`'s `--approve-submit` flag, off by default,
  is the only human-invoked path to it, and the eval harness never sets
  it. Demonstrated against local, offline, synthetic forms the project
  controls, never a real third-party site. v1/v2/v2.5 have no
  consequential actions at all — nothing to sandbox in those versions.
- Anti-bot/MFA/prompt-injection: `services/security/policy_engine.py`
  independently re-checks every action regardless of what field-mapping
  logic proposed — see docs/security_spec.md (provided by the project
  owner, preserved verbatim) and docs/roadmap.md's v3.2 section for what's
  built against it and what's explicitly deferred, and why.
- Data: the author's own resume/dossier and their own real, already-written
  CEO-application self-assessment, used with the data owner's consent
  (the author is both the user and the subject). The v3 demo form is a
  new, self-authored, self-labeled synthetic page, not scraped from
  anywhere.
- No credentials in this submission; `.env.example` documents required
  vars, `.env` is gitignored.
- Every claim in every generated answer/assessment/form field is either
  citation-tagged or flagged unsupported by
  `services/qa_engine/verification.py` — see `data/evaluation/results/v1_mock/`,
  `data/evaluation/results/v2_mock/`, and `data/evaluation/results/browser_mock/`
  for the evidence behind every number in this README.
