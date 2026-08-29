# AI tool use disclosure

Required by the hackathon FAQ: "Coding-agent use is required. You must
disclose the tools you use and submit the required trajectories or traces."

## Coding agent

**Claude Code** (Anthropic), running **Claude Sonnet 5**, was used as the
coding agent for the entirety of this repository — architecture decisions,
schema design, ingestion/retrieval/verification logic, the evaluation
harness, the question bank, and all documentation in `docs/`. The full,
unedited design brief the agent was given is preserved verbatim in
`PROMPT.md`.

This is a different thing from the *agents this project itself builds*
(`services/qa_engine/identityos_agent.py`, `baseline_plain.py`,
`baseline_rag.py`) — those are the subject of the Identity Fidelity
Benchmark. This disclosure is about the tool used to build the repository,
not the system the repository evaluates.

## What "agent-use evidence" looks like in this repo

- `data/evaluation/results/v1_mock/trajectories/` — a structured trajectory
  (`.json`) and human-readable rendering (`.md`) for every
  (question, system) pair the *product's own* agents ran, per
  services/qa_engine's Trajectory schema.
- This file plus `docs/improvement_changelog.md`'s "Iteration 5" entry —
  a real, disclosed mistake made *while using* a coding agent: a background
  research subagent was scoped to research only, inherited the full build
  context, and independently began implementing a duplicate scaffold in the
  same repository before being caught and stopped. Left in rather than
  cleaned from the record, per the hackathon's own instruction not to hide
  failed experiments.

## What was not AI-generated

The identity source documents (`data/identity_sources/*.md`) are
transcriptions of the project author's own pre-existing resume and
CEO-candidacy dossier — real documents the author wrote and owns, not
generated for this project.
