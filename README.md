# IdentityOS — v2.9

**An autonomous representative that answers application questions,
assesses job-requirement fit, and generates application documents on a
person's behalf, with evidence, calibrated confidence, and refusal instead
of fabrication.**

Built for the micro1 Agentic Workflows Hackathon, against the full brief
preserved in `PROMPT.md`. This repo builds v1 (Q&A), v2 (requirement-fit
assessment against a real, adjudicated application, iterated through
v2.4), and v2.5-v2.9 (document generation, two corpus authoring
corrections, and two diagnosed-but-rejected retrieval experiments that
together identify a real boundary of lexical retrieval) of that brief —
see [docs/roadmap.md](docs/roadmap.md) for what's deferred to v2.10-v5 and
why. Prior versions frozen at `../identityos-v1/`, `../identityos-v2/`,
`../identityos-v2.1/`, `../identityos-v2.2/`, `../identityos-v2.3/`,
`../identityos-v2.4/`, `../identityos-v2.5/`, `../identityos-v2.6/`,
`../identityos-v2.7/`, `../identityos-v2.8/`.

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
```

Expect each in under 10 seconds, $0 cost — the default `PROVIDER=mock` (LLM)
and `EMBEDDING_PROVIDER=hash` (embeddings) are deterministic, dependency-light
stand-ins built exactly so judges can reproduce the main result from a clean
environment (see docs/evaluation.md, docs/evaluation_v2.md, and
docs/evaluation_documents.md for what that does and doesn't prove).
`make eval-v2-semantic` / `make eval-documents` download a ~65MB ONNX
embedding model on first run (fastembed, no API key, no torch) — still $0,
but does need one-time network access. Output per run:
- `data/evaluation/results/<tag>/summary.json` (v1), `application_summary.json` (v2), or `document_summary.json` (v2.5)
- `data/evaluation/results/<tag>/answers.json` (v1) or `application_answers.json` (v2)
- `data/evaluation/results/<tag>/documents/<system>.md` — the actual generated cover letters (v2.5)
- `data/evaluation/results/<tag>/trajectories/*.md` — one file per
  (question-or-requirement-or-section, system) pair, human-readable, per
  the hackathon's trajectory deliverable

To get a qualitative read with a real model: copy `.env.example` to `.env`,
set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, then `make eval-real` / `make eval-v2-real`.

Run the smoke test suite: `make test` (26 tests, <1s, no keys/downloads needed).

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
| Dangerous overclaim rate | **0.00** | 0.50 | **0.00** |

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

## Improvement changelog

[docs/improvement_changelog.md](docs/improvement_changelog.md) — baseline
through final for both versions, including experiments we removed or that
stayed only partially fixed: a scoring rule fooled by the mock provider, a
process mistake where a background research agent overstepped its brief
mid-v1-build, and (v2) a bucketing rule that overclaimed a real admitted
gap until a negation check was added — which itself only partly closes
the gap (documented, not hidden).

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
of reweighting changes that. Full writeup, including what's still
unfixed: [docs/hot_take.md](docs/hot_take.md).

## Hackathon compliance self-check

Re-verified against the hackathon PDF's rubric, ground rules, and
deliverables list after every version: [docs/hackathon_compliance_check.md](docs/hackathon_compliance_check.md).

## AI tool use disclosure

Built with Claude Code (Claude Sonnet 5) as the coding agent throughout.
Full disclosure, and what "agent-use evidence" means in this repo:
[docs/agent_disclosure.md](docs/agent_disclosure.md).

## Repository map

```
docs/                  problem statement, architecture, roadmap, evaluation (v1, v2, documents),
                        changelog, research hypotheses, hot take, demo script, agent disclosure
packages/schemas/      typed Fact / Belief / Evidence / Question / Answer / Trajectory /
                        ApplicationRequirement / Assessment / FitBucket /
                        DocumentSection / GeneratedDocument
services/identity_engine/    ingestion + belief seeding + versioned storage
services/providers/          pluggable LLM backend: mock (default) / openai / anthropic
services/embeddings/         pluggable embedding backend: hash (default) / fastembed (v2.3)
services/qa_engine/          v1+: lexical, semantic + hybrid retrieval, the two
                              baselines, the IdentityOS agent, verification
services/application_engine/ v2: requirement-fit assessors (lexical, semantic,
                              hybrid) + polarity-aware bucketing
services/document_engine/    v2.5: section-planned cover-letter generation +
                              narrative-state (avoid repeating evidence)
services/evaluation/         scoring + all three eval harnesses
data/identity_sources/       the real source documents (owner's own, consented)
data/applications/           the real 14-requirement application + its real human ground truth
data/evaluation/              question bank + every eval harness's results/trajectories/documents
data/.embedding_cache/        fastembed's downloaded model (gitignored, regenerable)
scripts/               the commands judges actually run
tests/                 smoke tests (make test)
PROMPT.md              the full original design brief, unabridged
```

## Ground-rules compliance (hackathon requirement)

- Consequential actions: neither v1 nor v2 has any yet — no browser
  execution, no real submission exists until v3 (docs/roadmap.md), so there
  is nothing to sandbox or gate in this version.
- Data: the author's own resume/dossier and their own real, already-written
  CEO-application self-assessment, used with the data owner's consent
  (the author is both the user and the subject).
- No credentials in this submission; `.env.example` documents required
  vars, `.env` is gitignored.
- Every claim in every generated answer/assessment is either citation-tagged
  or flagged unsupported by `services/qa_engine/verification.py` — see
  `data/evaluation/results/v1_mock/` and `data/evaluation/results/v2_mock/`
  for the evidence behind every number in this README.
