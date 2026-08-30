# Hackathon compliance self-check

Re-verified after every version against `/home/siddhartha/siddhartha/micro1 - First Hackathon97ce7c5.pdf`.
Last checked: **after v2.9**.

## Judging rubric (100 pts)

| Criterion | Pts | Where addressed | Status |
|---|---|---|---|
| Problem & User Value | 15 | docs/problem_statement.md — real bottleneck (this project's own author reconstructing themself across applications), clearly defined user | Addressed |
| Agent Solution & Engineering | 30 | docs/architecture.md — retrieval + citation + verification + confidence-gated refusal (v1); reused pipeline + polarity-aware bucketing + three evaluated retrieval strategies (v2); section-planned document generation with narrative-state tracking (v2.5); two root-caused corpus authoring corrections (v2.6-v2.7); two independent retrieval-precision experiments, each tested against the full benchmark and correctly rejected rather than shipped on partial evidence (v2.8-v2.9). Purposeful, not "20 agents for the sake of it." | Addressed |
| End to End Quality | 20 | v2.5-v2.7 produces an actual usable artifact — a generated cover letter, verified free of scope-contamination across two rounds of fixes (`data/evaluation/results/*/documents/*.md`) | Addressed, no UI polish yet (v5) |
| Measured Improvement | 15 | docs/evaluation.md, docs/evaluation_v2.md, docs/evaluation_documents.md — fair baselines, same task/cases, honest limitations at every version. Hybrid retrieval's agreement rate rose 0.50 -> 0.57 -> 0.71 across two independent corpus corrections while its safety metric held at 0.00 both times; two further plausible-looking fixes (v2.8, v2.9) were each tested and shown to be net losses before being rejected | Addressed |
| Reproducibility | 15 | `make setup && make eval-mock && make eval-v2-mock && make eval-documents` from a clean environment, zero API keys, verified via standalone snapshots after every version (`identityos-v1/` through `-v2.8/`) | Addressed |
| Hot Take / Insights | 5 | docs/hot_take.md — nine real findings from actually running the eval or reading the output, culminating in a genuine research conclusion: two independent heuristic fixes failing the same way identifies a real boundary of lexical retrieval, not a tuning gap | Addressed |

## Ground rules (10)

1. Built with known tools (Python, pydantic, pytest, fastembed) — yes.
2. What existed before vs. added — `PROMPT.md` is the unedited brief; everything else in the repo is new. Digital Self *content* (resume, dossier) is the author's own pre-existing document, explicitly labeled as such in every file it appears in.
3. Tool/license terms — pydantic/pytest/openai/anthropic/fastembed used per their standard licenses, no ToS-restricted scraping or reuse. fastembed's BAAI/bge-small-en-v1.5 model is openly licensed and downloaded via its normal public distribution channel.
4. Consequential actions sandboxed/approval-gated — N/A yet: no browser execution or real submission exists until v3. A generated cover letter (v2.5-v2.7) is a draft artifact, not a submitted one — nothing consequential to gate yet.
5. Qualified human reviewer for anything that could significantly affect someone — N/A yet, same reason as #4; will apply once v3 can submit anything real.
6. Legal/ethical use case, data handled responsibly — yes: the author's own data, used with their own consent, for their own stated bottleneck.
7. Data you're allowed to share — yes: author's own resume/dossier, not a third party's.
8. Credentials outside the submission — yes: `.env.example` has empty placeholders, `.env` gitignored, verified no key ever appears in any committed file.
9. Every claim connected to evidence — yes: every generated claim/section is citation-checked by `services/qa_engine/verification.py`, and every evaluation number in every doc is regenerated from the actual `data/evaluation/results/` JSON, not hand-typed. Both v2.8 and v2.9's negative results were measured against the full benchmark, not asserted from the cases that motivated them.
10. Judges can reproduce the main result — yes: verified via a from-scratch `make setup` in separate, git/venv-free snapshots after every version. `make eval-v2-semantic` / `make eval-documents` need one-time network access to download the embedding model (~65MB); `make eval-v2-mock` needs none.

## Final deliverables (4)

1. **Complete solution code + improvement changelog** — code in this repo; `docs/improvement_changelog.md` covers all versions, includes removed/partially-fixed/not-promoted/later-superseded/root-caused-twice/tested-and-rejected-twice experiments, closes with failure mode + hot take (per version).
2. **Reproduction guide** — README Quickstart + this file; exact commands, no external data needed beyond what's in the repo, runtime is seconds (or ~1 min including a one-time model download for the semantic/hybrid/document arms), cost is $0.
3. **Solution video** — **not yet produced** (requires an actual screen recording, which is a human action outside this session's tools). `docs/demo_script.md` covers v1 through v2.5 within the 5-minute cap (~4:45 budgeted); v2.6-v2.9 could be mentioned in one line but aren't required to hit the deliverable.
4. **Agent trajectories** — `data/evaluation/results/*/trajectories/` for every agent across all versions (baseline_plain, baseline_rag, identityos_v1, identityos_v2, identityos_v2_semantic, identityos_v2_hybrid, identityos_v2_5's four document sections), covering all 19 v1 questions, all 14 v2 requirements under all three retrieval backends, and all 4 cover-letter sections.

## Open items carried forward

- Demo video: still needs to be recorded by a human — script covers through v2.5 and is ready; v2.6-v2.9 mentions are optional polish, not a blocker.
- req07 and req12 remain open with two independently-tried, independently-rejected fixes on record — the honest conclusion is that lexical/statistical relevance scoring cannot reliably solve this class of mismatch; the real fix needs semantic judgment (a real LLM call) and a provider key, named for v2.10.
- req11 (genuinely low retrieval confidence) and req14 (the real gap case, safely under-matched on the shipped default) remain open, both already understood, neither new.
- `identityos_v2_semantic` (standalone) remains unsafe as its own system (dangerous overclaim rate 0.50 as of v2.6-v2.7) — expected and not a priority, since it was never the shipped path; `identityos_v2_hybrid` already achieves the safety guarantee, now confirmed stable across three consecutive real corpus changes plus two rejected retrieval experiments.
- req08's dangerous overclaim was resolved in v2.1 via general corpus completion. req13's underclaim was resolved in v2.2 via clause-level negation. v2.3's embedding retrieval was evaluated honestly and not adopted after it reintroduced a dangerous overclaim; v2.4 diagnosed why and built a verified fix. v2.5 found a document-scope substitution; v2.6 and v2.7 traced it to the same authoring error in two different source files and fixed both. v2.8 and v2.9 each diagnosed a further mechanism, tested a fix against the full benchmark, and correctly declined to ship it after the measurement showed a net loss — the same rigor applied to negative results as to every positive one.
