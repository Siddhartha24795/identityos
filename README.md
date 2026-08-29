# IdentityOS — v2

**An autonomous representative that answers application questions and
assesses job-requirement fit on a person's behalf, with evidence,
calibrated confidence, and refusal instead of fabrication.**

Built for the micro1 Agentic Workflows Hackathon, against the full brief
preserved in `PROMPT.md`. This repo builds v1 (Q&A) and v2 (requirement-fit
assessment against a real, adjudicated application) of that brief — see
[docs/roadmap.md](docs/roadmap.md) for what's deferred to v2.1-v5 and why.
Prior version frozen at `../identityos-v1/`.

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
make eval-mock        # v1: builds Digital Self, runs all 3 systems on 19 Q&A questions
make eval-v2-mock     # v2: runs all 3 systems on 14 real job-requirement assessments
```

Expect each in under 10 seconds, $0 cost — the default `PROVIDER=mock` is a
deterministic, non-LLM stand-in built exactly so judges can reproduce the
main result from a clean environment (see docs/evaluation.md and
docs/evaluation_v2.md for what that does and doesn't prove). Output per run:
- `data/evaluation/results/<tag>/summary.json` (v1) or `application_summary.json` (v2)
- `data/evaluation/results/<tag>/answers.json` (v1) or `application_answers.json` (v2)
- `data/evaluation/results/<tag>/trajectories/*.md` — one file per
  (question-or-requirement, system) pair, human-readable, per the
  hackathon's trajectory deliverable

To get a qualitative read with a real model: copy `.env.example` to `.env`,
set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, then `make eval-real` / `make eval-v2-real`.

Run the smoke test suite: `make test` (10 tests, <1s, no keys needed).

## Results (reference runs, `PROVIDER=mock`)

**v1 — Q&A (19 questions):**

| Metric | baseline_plain | baseline_rag | identityos_v1 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.92** |
| Unsupported claim rate | 1.00 | 1.00 | **0.08** |
| **Identity Fidelity Score** | 0.20 | 0.20 | **0.94** |

Full breakdown, the four hard cases verbatim, and an honest limitation of
this offline run: [docs/evaluation.md](docs/evaluation.md).

**v2 — requirement-fit assessment (14 real requirements, real human ground truth):**

| Metric | baseline_plain | baseline_rag | identityos_v2 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.74** |
| Assessment agreement rate | 0.07 | 0.07 | **0.29** |
| Dangerous overclaim rate (of 4 non-MET requirements) | 0.00* | 0.00* | 0.25 |

*Trivial — both baselines say "gap" to every requirement regardless of
truth, so they cannot overclaim, but they also can't answer anything
correctly except by accident. Full story, including a real bug found and
partially fixed mid-build (the system briefly overclaimed the single
most important requirement — a real, admitted governance gap — because
grounding and polarity got conflated): [docs/evaluation_v2.md](docs/evaluation_v2.md).

## Improvement changelog

[docs/improvement_changelog.md](docs/improvement_changelog.md) — baseline
through final for both versions, including experiments we removed or that
stayed only partially fixed: a scoring rule fooled by the mock provider, a
process mistake where a background research agent overstepped its brief
mid-v1-build, and (v2) a bucketing rule that overclaimed a real admitted
gap until a negation check was added — which itself only partly closes
the gap (documented, not hidden).

## Main failure mode / hot take

The same underlying mistake, found twice, independently: grounding
verification checks whether a claim traces to evidence, not what the claim
actually *means*. v1: a well-cited, high-confidence answer can still be
off-topic (confidence stood in for relevance it never measured). v2: a
well-cited, high-confidence answer can still be a "no" (confidence stood in
for polarity it never measured) — caught on the single highest-stakes
requirement in a real application. Full writeup, including what's still
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
docs/                  problem statement, architecture, roadmap, evaluation (v1 + v2),
                        changelog, research hypotheses, hot take, demo script, agent disclosure
packages/schemas/      typed Fact / Belief / Evidence / Question / Answer / Trajectory /
                        ApplicationRequirement / Assessment / FitBucket
services/identity_engine/    ingestion + belief seeding + versioned storage
services/providers/          pluggable LLM backend: mock (default) / openai / anthropic
services/qa_engine/          v1: retrieval, the two baselines, the IdentityOS agent, verification
services/application_engine/ v2: requirement-fit assessors + polarity-aware bucketing
services/evaluation/         scoring + both eval harnesses
data/identity_sources/       the real source documents (owner's own, consented)
data/applications/           the real 14-requirement application + its real human ground truth
data/evaluation/              question bank + both eval harnesses' results/trajectories
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
