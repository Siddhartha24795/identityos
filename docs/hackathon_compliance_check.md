# Hackathon compliance self-check

Re-verified after every version against `/home/siddhartha/siddhartha/micro1 - First Hackathon97ce7c5.pdf`.
Last checked: **after v2.6**.

## Judging rubric (100 pts)

| Criterion | Pts | Where addressed | Status |
|---|---|---|---|
| Problem & User Value | 15 | docs/problem_statement.md — real bottleneck (this project's own author reconstructing themself across applications), clearly defined user | Addressed |
| Agent Solution & Engineering | 30 | docs/architecture.md — retrieval + citation + verification + confidence-gated refusal (v1); reused pipeline + polarity-aware bucketing + three evaluated retrieval strategies (v2); section-planned document generation with narrative-state tracking (v2.5); a root-caused corpus authoring correction verified across all three eval suites (v2.6). Purposeful, not "20 agents for the sake of it." | Addressed |
| End to End Quality | 20 | v2.5 produces an actual usable artifact — a generated cover letter, not just a benchmark number (`data/evaluation/results/*/documents/*.md`) | Addressed, no UI polish yet (v5) |
| Measured Improvement | 15 | docs/evaluation.md, docs/evaluation_v2.md, docs/evaluation_documents.md — fair baselines, same task/cases, honest limitations stated at every version, including a fix (v2.6) verified to improve one system while confirming another was correctly never promoted | Addressed |
| Reproducibility | 15 | `make setup && make eval-mock && make eval-v2-mock && make eval-documents` from a clean environment, zero API keys, verified via standalone snapshots after every version (`identityos-v1/` through `-v2.5/`) | Addressed |
| Hot Take / Insights | 5 | docs/hot_take.md — six real findings from actually running the eval or reading the output (relevance, polarity, retrieval/verification coupling, diagnosis-driven fixing, evidence scope, and authoring-correction-vs-classifier), not a generic lesson | Addressed |

## Ground rules (10)

1. Built with known tools (Python, pydantic, pytest, fastembed) — yes.
2. What existed before vs. added — `PROMPT.md` is the unedited brief; everything else in the repo is new. Digital Self *content* (resume, dossier) is the author's own pre-existing document, explicitly labeled as such in every file it appears in.
3. Tool/license terms — pydantic/pytest/openai/anthropic/fastembed used per their standard licenses, no ToS-restricted scraping or reuse. fastembed's BAAI/bge-small-en-v1.5 model is openly licensed and downloaded via its normal public distribution channel.
4. Consequential actions sandboxed/approval-gated — N/A yet: no browser execution or real submission exists until v3. A generated cover letter (v2.5) is a draft artifact, not a submitted one — nothing consequential to gate yet.
5. Qualified human reviewer for anything that could significantly affect someone — N/A yet, same reason as #4; will apply once v3 can submit anything real.
6. Legal/ethical use case, data handled responsibly — yes: the author's own data, used with their own consent, for their own stated bottleneck.
7. Data you're allowed to share — yes: author's own resume/dossier, not a third party's.
8. Credentials outside the submission — yes: `.env.example` has empty placeholders, `.env` gitignored, verified no key ever appears in any committed file.
9. Every claim connected to evidence — yes: every generated claim/section is citation-checked by `services/qa_engine/verification.py`, and every evaluation number in every doc is regenerated from the actual `data/evaluation/results/` JSON, not hand-typed. v2.6's claim (five bullets shared the same authoring defect) was checked by re-reading the source file, not asserted.
10. Judges can reproduce the main result — yes: verified via a from-scratch `make setup` in separate, git/venv-free snapshots after every version. `make eval-v2-semantic` / `make eval-documents` need one-time network access to download the embedding model (~65MB); `make eval-v2-mock` needs none.

## Final deliverables (4)

1. **Complete solution code + improvement changelog** — code in this repo; `docs/improvement_changelog.md` covers all versions, includes removed/partially-fixed/not-promoted/later-superseded/root-caused experiments, closes with failure mode + hot take (per version).
2. **Reproduction guide** — README Quickstart + this file; exact commands, no external data needed beyond what's in the repo, runtime is seconds (or ~1 min including a one-time model download for the semantic/hybrid/document arms), cost is $0.
3. **Solution video** — **not yet produced** (requires an actual screen recording, which is a human action outside this session's tools). `docs/demo_script.md` covers v1 through v2.5 within the 5-minute cap (~4:45 budgeted); a short v2.6 mention (the authoring-correction finding) could be folded in but isn't required to hit the deliverable.
4. **Agent trajectories** — `data/evaluation/results/*/trajectories/` for every agent across all versions (baseline_plain, baseline_rag, identityos_v1, identityos_v2, identityos_v2_semantic, identityos_v2_hybrid, identityos_v2_5's four document sections), covering all 19 v1 questions, all 14 v2 requirements under all three retrieval backends, and all 4 cover-letter sections.

## Open items carried forward

- Demo video: still needs to be recorded by a human — script covers through v2.5 and is ready; a v2.6 line is optional polish, not a blocker.
- `dossier_excerpts.md`'s "SELF-ASSESSED GAP" section has a near-identical conflation to the one fixed in `dossier_narrative.md` (v2.6) — found by re-reading the regenerated letter, named for v2.7, not yet fixed.
- Six requirements (req03/06/07/11/12/14) don't reach an exact bucket match under hybrid — a coarse-3-bucket-scale nuance limitation, not a retrieval or safety problem (docs/roadmap.md v2.7+).
- `identityos_v2_semantic` (standalone) remains unsafe as its own system (dangerous overclaim rate 0.50 as of v2.6, worse than v2.3/v2.4, on different requirements) — expected and not a priority, since it was never the shipped path; `identityos_v2_hybrid` already achieves the safety guarantee.
- req08's dangerous overclaim was resolved in v2.1 via general corpus completion. req13's underclaim was resolved in v2.2 via clause-level negation. v2.3's embedding retrieval was evaluated honestly and not adopted after it reintroduced a dangerous overclaim; v2.4 diagnosed why and built a verified fix. v2.5 found and partially fixed a document-scope substitution; v2.6 traced its root cause to an authoring error and fixed it generally (five bullets, not one), verifying the fix's effect across all three eval suites before calling it done.
