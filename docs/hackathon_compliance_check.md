# Hackathon compliance self-check

Re-verified after every version against `/home/siddhartha/siddhartha/micro1 - First Hackathon97ce7c5.pdf`.
Last checked: **after v2.1**.

## Judging rubric (100 pts)

| Criterion | Pts | Where addressed | Status |
|---|---|---|---|
| Problem & User Value | 15 | docs/problem_statement.md — real bottleneck (this project's own author reconstructing themself across applications), clearly defined user | Addressed |
| Agent Solution & Engineering | 30 | docs/architecture.md — retrieval + citation + verification + confidence-gated refusal (v1); reused pipeline + polarity-aware bucketing (v2). Purposeful, not "20 agents for the sake of it." | Addressed |
| End to End Quality | 20 | Both eval harnesses run end to end and produce a usable result (scored comparison + trajectories) from one command each | Addressed, no UI polish yet (v5) |
| Measured Improvement | 15 | docs/evaluation.md, docs/evaluation_v2.md — fair baselines, same task/cases, honest limitations stated, including a metric (dangerous_overclaim_rate) fixed by a general corpus pass rather than a targeted patch | Addressed |
| Reproducibility | 15 | `make setup && make eval-mock && make eval-v2-mock` from a clean environment, zero API keys, verified via `identityos-v1/` standalone snapshot | Addressed |
| Hot Take / Insights | 5 | docs/hot_take.md — a real bug found by running the eval (v1: relevance; v2: polarity), not a generic lesson | Addressed |

## Ground rules (10)

1. Built with known tools (Python, pydantic, pytest) — yes.
2. What existed before vs. added — `PROMPT.md` is the unedited brief; everything else in the repo is new. Digital Self *content* (resume, dossier) is the author's own pre-existing document, explicitly labeled as such in every file it appears in.
3. Tool/license terms — pydantic/pytest/openai/anthropic SDKs used per their standard licenses, no ToS-restricted scraping or reuse.
4. Consequential actions sandboxed/approval-gated — N/A yet: no browser execution or real submission exists until v3. Nothing consequential to gate in v1/v2.
5. Qualified human reviewer for anything that could significantly affect someone — N/A yet, same reason as #4; will apply once v3 can submit anything real.
6. Legal/ethical use case, data handled responsibly — yes: the author's own data, used with their own consent, for their own stated bottleneck.
7. Data you're allowed to share — yes: author's own resume/dossier, not a third party's.
8. Credentials outside the submission — yes: `.env.example` has empty placeholders, `.env` gitignored, verified no key ever appears in any committed file.
9. Every claim connected to evidence — yes: every generated claim is citation-checked by `services/qa_engine/verification.py`, and every evaluation number in every doc is regenerated from the actual `data/evaluation/results/` JSON, not hand-typed.
10. Judges can reproduce the main result — yes: verified via a from-scratch `make setup` in a separate, git/venv-free snapshot (`identityos-v1/`, and `identityos-v2` will get the same check).

## Final deliverables (4)

1. **Complete solution code + improvement changelog** — code in this repo; `docs/improvement_changelog.md` covers both versions, includes removed/partially-fixed experiments, closes with failure mode + hot take (per version).
2. **Reproduction guide** — README Quickstart + this file; exact commands, no external data needed beyond what's in the repo, runtime is seconds, cost is $0 on the mock provider.
3. **Solution video** — **not yet produced** (requires an actual screen recording, which is a human action outside this session's tools). `docs/demo_script.md` is the ready-to-record script; needs updating with a v2 walkthrough segment before recording.
4. **Agent trajectories** — `data/evaluation/results/*/trajectories/` for every agent in both versions (baseline_plain, baseline_rag, identityos_v1, identityos_v2), covering all 19 v1 questions and all 14 v2 requirements.

## Open items carried forward

- Demo video: still needs to be recorded by a human. `docs/demo_script.md` has a v2 segment; a v2.1 update (the corpus-completion story) is the next small addition before recording.
- Two known safe-direction (non-dangerous) cases remain open: req13 (clause-level negation, not yet built) and req05/req10 (lexical retrieval can't match abstract requirement phrasing to differently-worded evidence — embedding retrieval, not yet built). Neither is hidden; both are in docs/evaluation_v2.md and docs/roadmap.md v2.2+.
- req08's dangerous overclaim was resolved in v2.1 via general corpus completion, not a targeted patch.
