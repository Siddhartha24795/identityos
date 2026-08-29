# IdentityOS — v1

**An autonomous representative that answers application questions on a
person's behalf, with evidence, calibrated confidence, and refusal instead
of fabrication.**

Built for the micro1 Agentic Workflows Hackathon, against the full brief
preserved in `PROMPT.md`. This repo builds v1 of that brief — see
[docs/roadmap.md](docs/roadmap.md) for what's deferred to v2-v5 and why.

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
make eval-mock        # builds Digital Self v1, runs all 3 systems on 19 questions
```

Expect this in under 10 seconds, $0 cost — the default `PROVIDER=mock` is a
deterministic, non-LLM stand-in built exactly so judges can reproduce the
main result from a clean environment (see
[docs/evaluation.md](docs/evaluation.md) for what that does and doesn't
prove). Output:
- `data/evaluation/results/v1_mock/summary.json` — the scored comparison
- `data/evaluation/results/v1_mock/answers.json` — every generated answer
- `data/evaluation/results/v1_mock/trajectories/*.md` — one file per
  (question, system) pair, human-readable, per the hackathon's trajectory
  deliverable

To get a qualitative read with a real model: copy `.env.example` to `.env`,
set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, then `make eval-real`.

Run the smoke test suite: `make test` (6 tests, <1s, no keys needed).

## Result (reference run, `PROVIDER=mock`)

| Metric | baseline_plain | baseline_rag | identityos_v1 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.93** |
| Unsupported claim rate | 1.00 | 1.00 | **0.07** |
| **Identity Fidelity Score** | 0.20 | 0.20 | **0.95** |

Full breakdown, the four hard cases verbatim, and an honest limitation of
this offline run: [docs/evaluation.md](docs/evaluation.md).

## Improvement changelog

[docs/improvement_changelog.md](docs/improvement_changelog.md) — baseline
through final, including two removed experiments (a scoring rule fooled by
the mock provider, and a process mistake mid-build where a background
research agent overstepped its brief and started duplicating implementation
work in this same repo).

## Main failure mode / hot take

Refusal never fired once across all 19 questions, including the hardest
unseen-inferential ones — not because every question had strong evidence,
but because confidence in v1 measures *"is this fact true"* rather than
*"is this fact a good answer to this specific question."* Full writeup:
[docs/hot_take.md](docs/hot_take.md).

## AI tool use disclosure

Built with Claude Code (Claude Sonnet 5) as the coding agent throughout.
Full disclosure, and what "agent-use evidence" means in this repo:
[docs/agent_disclosure.md](docs/agent_disclosure.md).

## Repository map

```
docs/                  problem statement, architecture, roadmap, evaluation,
                        changelog, research hypotheses, hot take, demo script
packages/schemas/      typed Fact / Belief / Evidence / Question / Answer / Trajectory
services/identity_engine/  ingestion + belief seeding + versioned storage
services/providers/    pluggable LLM backend: mock (default) / openai / anthropic
services/qa_engine/    retrieval, the two baselines, the IdentityOS agent, verification
services/evaluation/   scoring + the eval harness
data/identity_sources/ the real source documents (owner's own, consented)
data/evaluation/       the 19-question bank + every run's results/trajectories
scripts/               the two commands judges actually run
tests/                 smoke tests (make test)
PROMPT.md              the full original design brief, unabridged
```

## Ground-rules compliance (hackathon requirement)

- Consequential actions: v1 has none yet — no browser execution, no real
  submission exists until v3 (docs/roadmap.md), so there is nothing to
  sandbox or gate in this version.
- Data: the author's own resume/dossier, used with the data owner's consent
  (the author is both the user and the subject).
- No credentials in this submission; `.env.example` documents required
  vars, `.env` is gitignored.
- Every claim in every generated answer is either citation-tagged or
  flagged unsupported by `services/qa_engine/verification.py` — see
  `data/evaluation/results/v1_mock/` for the evidence behind every number
  in this README.
