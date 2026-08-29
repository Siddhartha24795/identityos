# Improvement changelog

All results below come from the same 19-question bank, scored the same way,
via `python scripts/run_eval.py mock <tag>` (services/evaluation/run_eval.py
+ scoring.py). Full numbers: docs/evaluation.md.

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| **Baseline** | One direct prompt, no context (`baseline_plain`) — the honest "what does a person get today" starting point. | Identity Fidelity Score **0.20**; evidence coverage 0.00; unsupported-claim rate 1.00. | Established the starting point. Confidently generic on every question — never wrong in a checkable way because it never makes a checkable claim. |
| **Iteration 1** | Added `baseline_rag`: dump the entire fact store as unstructured context, no ranking, no citation requirement. Hypothesis: giving the model the resume would fix fabrication. | Identity Fidelity Score **0.20** — identical to no-context baseline. Evidence coverage still 0.00. | **Kept as baseline, not as the solution.** Context alone doesn't move the metric that matters: without a citation mechanism, a claim is unverifiable whether or not it happens to be true. This is the project's core thesis, confirmed empirically before we'd even built the real system. |
| **Iteration 2** | Structured retrieval: format retrieved facts/beliefs as citation-tagged lines (`[resume:014] ...`) and instruct the model to cite inline. | Evidence coverage jumped **0.00 -> 0.93** on the same question set. | Kept. Largest single driver of the whole result — citation-forcing, not better prompting, is what made claims checkable. |
| **Iteration 3** | Added a sentence-level verification pass independent of citation: lexical-overlap fallback for sentences without an explicit tag, so paraphrased-but-grounded content isn't wrongly flagged unsupported. | Unsupported-claim rate **0.066** (vs. 1.00 for both baselines). | Kept. Necessary because generation doesn't always cite every clause; a pure "must have a bracket tag" rule would have under-counted real grounding. |
| **Iteration 4 — removed** | First version of the hard-case overclaim check used pure lexical-overlap scoring, no hand-authored rules. It scored `baseline_rag` as "safe" on the patent-credit question. | On inspection, `baseline_rag` only avoided overclaiming because the mock provider copies source sentences verbatim — it has no actual safeguard. The metric was measuring the mock provider's extraction style, not the baseline's safety. | **Removed and replaced** with an explicit forbidden-phrase-without-qualifier rule set (services/evaluation/scoring.py `_HARD_CASE_RULES`) so the metric stays meaningful once a real, paraphrasing LLM is plugged in. See docs/hot_take.md. |
| **Iteration 5 — process, removed** | Spawned a background "research-only" agent mid-build to look up industry practice while implementation continued in parallel. | It inherited the full build-instruction context and began independently scaffolding its own copy of the same system in the same repo. One file (`ingest.py`) was overwritten before we noticed; no data was permanently lost, but real conflict occurred. | Killed the fork, consolidated on one implementation, and scoped future background-agent prompts more defensively. A real instance of exactly the "agent should not act beyond its assigned task" failure mode this project is trying to prevent in its own users. |
| **Final** | Structured retrieval + inline citation + sentence-level verification + confidence-gated refusal policy = `identityos_v1`. | Identity Fidelity Score **0.95** vs **0.20** for both baselines. Evidence coverage 0.93 vs 0.00. Unsupported-claim rate 0.066 vs 1.00. | Main contribution: making claims checkable at all is what separates the system from both baselines — this held even on an offline mock provider, before any real LLM quality was involved. |

## Main failure mode (see docs/hot_take.md for the full writeup)

Refusal never fired, including on the hardest unseen-inferential questions,
because verification confidence measures "is this fact true" (source
fidelity) rather than "is this fact a good answer to this question"
(relevance). A highly-confident, well-cited, off-topic answer currently
looks identical to a correct one. This is the clearest remaining gap
between v1 and the original design brief's uncertainty policy, and the
top item for v2.
