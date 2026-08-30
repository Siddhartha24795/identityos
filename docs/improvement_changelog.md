# Improvement changelog

All results below come from the same 19-question bank, scored the same way,
via `python scripts/run_eval.py mock <tag>` (services/evaluation/run_eval.py
+ scoring.py). Numbers in this section are as measured at the time of each
iteration; the corpus grew further during v2/v2.1 (shared Digital Self), so
current reproduced numbers are marginally higher — see docs/evaluation.md
for the up-to-date figures and why they moved.

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| **Baseline** | One direct prompt, no context (`baseline_plain`) — the honest "what does a person get today" starting point. | Identity Fidelity Score **0.20**; evidence coverage 0.00; unsupported-claim rate 1.00. | Established the starting point. Confidently generic on every question — never wrong in a checkable way because it never makes a checkable claim. |
| **Iteration 1** | Added `baseline_rag`: dump the entire fact store as unstructured context, no ranking, no citation requirement. Hypothesis: giving the model the resume would fix fabrication. | Identity Fidelity Score **0.20** — identical to no-context baseline. Evidence coverage still 0.00. | **Kept as baseline, not as the solution.** Context alone doesn't move the metric that matters: without a citation mechanism, a claim is unverifiable whether or not it happens to be true. This is the project's core thesis, confirmed empirically before we'd even built the real system. |
| **Iteration 2** | Structured retrieval: format retrieved facts/beliefs as citation-tagged lines (`[resume:014] ...`) and instruct the model to cite inline. | Evidence coverage jumped **0.00 -> 0.93** on the same question set. | Kept. Largest single driver of the whole result — citation-forcing, not better prompting, is what made claims checkable. |
| **Iteration 3** | Added a sentence-level verification pass independent of citation: lexical-overlap fallback for sentences without an explicit tag, so paraphrased-but-grounded content isn't wrongly flagged unsupported. | Unsupported-claim rate **0.08** (vs. 1.00 for both baselines). | Kept. Necessary because generation doesn't always cite every clause; a pure "must have a bracket tag" rule would have under-counted real grounding. |
| **Iteration 4 — removed** | First version of the hard-case overclaim check used pure lexical-overlap scoring, no hand-authored rules. It scored `baseline_rag` as "safe" on the patent-credit question. | On inspection, `baseline_rag` only avoided overclaiming because the mock provider copies source sentences verbatim — it has no actual safeguard. The metric was measuring the mock provider's extraction style, not the baseline's safety. | **Removed and replaced** with an explicit forbidden-phrase-without-qualifier rule set (services/evaluation/scoring.py `_HARD_CASE_RULES`) so the metric stays meaningful once a real, paraphrasing LLM is plugged in. See docs/hot_take.md. |
| **Iteration 5 — process, removed** | Spawned a background "research-only" agent mid-build to look up industry practice while implementation continued in parallel. | It inherited the full build-instruction context and began independently scaffolding its own copy of the same system in the same repo. One file (`ingest.py`) was overwritten before we noticed; no data was permanently lost, but real conflict occurred. | Killed the fork, consolidated on one implementation, and scoped future background-agent prompts more defensively. A real instance of exactly the "agent should not act beyond its assigned task" failure mode this project is trying to prevent in its own users. |
| **Final** | Structured retrieval + inline citation + sentence-level verification + confidence-gated refusal policy = `identityos_v1`. | Identity Fidelity Score **0.94** vs **0.20** for both baselines. Evidence coverage 0.92 vs 0.00. Unsupported-claim rate 0.08 vs 1.00. | Main contribution: making claims checkable at all is what separates the system from both baselines — this held even on an offline mock provider, before any real LLM quality was involved. |

## Main failure mode, v1 (see docs/hot_take.md for the full writeup)

Refusal never fired, including on the hardest unseen-inferential questions,
because verification confidence measures "is this fact true" (source
fidelity) rather than "is this fact a good answer to this question"
(relevance). A highly-confident, well-cited, off-topic answer currently
looks identical to a correct one.

---

# v2 — Application Compilation (real-ground-truth benchmark)

All results from `python scripts/run_eval_v2.py mock v2_mock`, scored
against the IITACB CEO dossier's real 14-requirement fit table
(docs/evaluation_v2.md has full numbers).

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| **Baseline (v2)** | Reused v1's `baseline_plain`/`baseline_rag` structure unmodified, applied to requirement-fit assessment instead of Q&A. | Agreement rate 0.07 for both; evidence coverage 0.00 for both. | Confirms the same v1 finding on a completely different task shape: no citation mechanism = unverifiable, regardless of task. |
| **Iteration 1 (v2)** | First `identityos_v2` pass: reuse v1's retrieval + verification, derive a fit bucket purely from evidence_coverage + overall_confidence thresholds. | Agreement rate 0.43 — looked like a strong result. | **Not trusted at face value.** Inspected the highest-stakes case (req14, the one real `gap`) before accepting the number. |
| **Iteration 2 (v2) — the req14 bug** | Inspection found req14 (real = `gap`) was bucketed `met_or_better`, despite the system correctly retrieving and citing the exact sentence stating the gap. | The cited claim had full evidence coverage and 0.89 confidence — both high, because the *citation* was accurate, even though the *content* was a "no." | Root cause: coverage/confidence measure groundedness, not polarity. Confirmed this wasn't a one-off by design, not by luck. |
| **Iteration 3 (v2)** | Added a lexical negation check on cited claim text (`_NEGATION_MARKERS` in `services/application_engine/bucketing.py`), general — not keyed to req14's id. | req14 moved from the dangerous `met_or_better` to `partial` (still not an exact match, but no longer a confident overclaim). Overall agreement rate dropped to 0.29 — the fix also correctly downgraded other confident-but-imperfect answers. | Kept, despite the lower headline number. A lower agreement rate that removes a dangerous overclaim is a better result than a higher one that hides it — see docs/hot_take.md. |
| **Iteration 4 (v2)** | Investigated req09 (government/policy engagement) scoring wrong for a different reason: the ideal evidence sentence had never been transcribed into the Digital Self's source documents at all. Added it — real text from the source dossier, not fabricated. | req09 moved from wrong to a correct `partial` match. | Kept. A genuine corpus-completeness gap, not a scoring bug — distinguishing the two mattered before "fixing" anything. |
| **Iteration 5 (v2) — added, not removed** | Added a second metric, `dangerous_overclaim_rate` (of the 4 real non-MET requirements, how often does the system confidently claim full credit anyway), after realizing agreement_rate alone treats a safe underclaim and a dangerous overclaim as equally wrong. | identityos_v2: 0.25 (1 of 4). Both baselines: 0.00 — but only because they never claim `met_or_better` on anything, which is a degenerate kind of "safe." | Kept as a permanent second metric. Explained clearly in docs/evaluation_v2.md so the 0.00 baseline number isn't misread as baselines being careful. |
| **Final (v2.0)** | Combined structured retrieval + citation + verification + negation-aware bucketing + two eval-triggered corpus patches = `identityos_v2`. | Evidence coverage 0.74 vs 0.00 (both baselines). Agreement rate 0.29 vs 0.07. Dangerous overclaim rate 0.25 — one real, undismissed remaining failure (req08). | Shipped honestly with one known dangerous overclaim rather than tuning bucketing thresholds until the number looked clean. |
| **Iteration 6 (v2.1)** | Instead of patching req08's specific missing sentence (the same shape of fix as req09, which risked "tuning until the 14 known cases pass"), did one general pass: transcribed the *entire* remaining requirement-evidence table plus the dossier's broader narrative (accountabilities, revenue architecture, first-100-days, closing) into `data/identity_sources/dossier_narrative.md` — real source content, not selected by which eval case needed it, and mostly untested by any current question. | Digital Self grew 76 -> 92 facts. Evidence coverage 0.74 -> 0.83. Agreement rate 0.29 -> 0.36. **Dangerous overclaim rate 0.25 -> 0.00** — req08 fixed as a side effect. v1's own score also improved slightly (0.939 -> 0.958 Identity Fidelity Score), since both versions share one Digital Self. | Kept. The general fix (complete the record) resolved the specific problem (req08) better than a targeted patch would have, without touching bucketing logic at all. |

| **Iteration 7 (v2.2)** | Split cited claim text on unambiguous contrastive conjunctions (" but ", "; ", "however", "though", "while") and classified each claim as negative/mixed/positive, so a claim mixing a positive and a negative clause buckets `partial` instead of the old whole-sentence-negative `gap`. Added a regression test for the mixed-clause case before touching the eval. | req13 now correctly agrees (`partial` vs `partial`). Agreement rate 0.36 -> 0.43. No other requirement's bucket changed — re-ran the full comparison, not just req13. Dangerous overclaim rate stayed 0.00. | Kept. A precise fix to one diagnosed gap, verified not to have side effects — the opposite failure mode from the negation-rule iteration that first fixed req14 and briefly regressed other requirements. |

| **Iteration 8 (v2.3) — kept as a comparison arm, not promoted to default** | Built `identityos_v2_semantic`: identical pipeline to `identityos_v2`, with embedding-cosine retrieval (fastembed, BAAI/bge-small-en-v1.5, chosen for zero API key + ~65MB ONNX footprint) instead of lexical word-overlap. Hypothesis: this fixes req05/req10 (real evidence exists, zero lexical overlap). | It did — req10 moved to a fully correct `met_or_better`, req05 to a `partial` (real improvement). But agreement rate fell 0.43 -> 0.36 and **dangerous overclaim rate rose 0.00 -> 0.25**: req09 (a real, admitted government-engagement gap) started overclaiming, because semantic retrieval's higher recall / lower precision pulled in more topically-adjacent facts, and the v2.2 polarity check can't distinguish "negative claim about this topic" from "negative claim about something merely embedding-adjacent." | **Not promoted to default.** Kept running in the harness as an honest, ongoing comparison arm. Fixing part of a known limitation while reintroducing a worse one elsewhere is not a net improvement — see docs/hot_take.md and docs/evaluation_v2.md for the full trade-off, not just the number that improved. |

| **Iteration 9 (v2.4) — promoted, the targeted fix worked** | Diagnosed the exact mechanism behind Iteration 8's regression: semantic noise only appeared when it overrode requirements lexical already had evidence for, never when filling a genuine gap. Built `retrieve_hybrid()`: lexical first, semantic fallback *only* when lexical returns nothing. | Agreement rate **0.50** (best of all five systems, vs. 0.43 lexical / 0.36 semantic). Dangerous overclaim rate **0.00** (matches lexical). Verified requirement-by-requirement, not assumed: all 12 requirements lexical could already answer are byte-identical to pure lexical output, including req09 (semantic alone had broken it; hybrid never touches it). Only req05/req10 (lexical's real gaps) changed, one fully fixed. | **Promoted as the recommended retrieval strategy**, kept alongside lexical-only and semantic-only as permanent comparison arms — not deleting the data that led here. |

## Main failure mode, v2.4 (see docs/hot_take.md for the full writeup)

Six requirements (req03, req06, req07, req11, req12, req14) still don't
reach an exact bucket match on any retrieval arm, including hybrid — mostly
a coarse-3-bucket-scale nuance problem ("MET with a stated caveat", or a
forward commitment, doesn't cleanly fit met_or_better/partial/gap) rather
than a new finding. req05 improved (`gap` -> `partial`) under hybrid but
isn't an exact match yet, because the semantic fallback's citation is real
but not confidently grounded enough to cross the met_or_better threshold.
None of these are dangerous — the safety metric stays at 0.00.

---

# v2.5 — Document Generation (cover letter)

All results from `python scripts/run_eval_documents.py mock docs_mock fastembed`
(docs/evaluation_documents.md has full numbers and the actual generated letters).

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| **Baseline (v2.5)** | `baseline_plain` / `baseline_rag`, same structure as v1/v2, applied to a 4-section cover letter instead of short answers. | Evidence coverage 0.00, unsupported-claim rate 1.00 for both — identical structural story to v1/v2 on a new task shape. | Confirms the core thesis generalizes to full-document generation, not just short answers. |
| **Iteration 1 (v2.5)** | `identityos_v2_5`: section-by-section generation reusing hybrid retrieval + verification unmodified, plus `_prefer_unused()` to deprioritize (not forbid) re-citing evidence already used in an earlier section — a concrete test of the brief's `APPLICATION_NARRATIVE_STATE` concept. | Evidence coverage 0.95-1.00, unsupported-claim rate 0.00-0.05, repeated-evidence rate ~0.28-0.32 (most citations are fresh per section, not the same two facts four times). | Kept. First working multi-paragraph artifact, not just a short answer or a label. |
| **Iteration 2 (v2.5) — found by reading the letter, not the score** | Inspected the actual generated letter (not just its passing metrics) before calling it done. | It read like an application for one specific prior role ("the Secretariat," "the committee") — every cited sentence real and grounded, none of it appropriate for a generic letter. No existing metric (coverage, unsupported-claim rate, polarity) flagged this. | Root-caused to one identity-source section written as strategy narrative for a specific prior candidacy, not general evidence about the person. |
| **Iteration 3 (v2.5)** | Added `FactCategory.APPLICATION_SPECIFIC`, tagged the offending source section at ingestion, excluded it from generic document generation. Verified v1/v2's own scores were unaffected (category never fed their scoring) before trusting the fix. | 7 facts tagged and excluded; the most egregious IITACB-strategy sentences no longer appear. | Kept, but **not treated as fully solved** — see next row. |
| **Iteration 4 (v2.5) — diagnosed, not patched further** | Re-inspected the letter after Iteration 3. | Residual role-specific framing survives inside individual sentences of otherwise-general, correctly-categorized facts ("precisely the condition of a Secretariat being stood up") — a sentence-level leak inside a whole-fact-level filter. | **Not fixed here.** Rewriting the source facts to strip this framing, having just seen it look bad in an eval run, is the same reactive-corpus-editing pattern already declined for req08/req13. Named as an open v2.6+ item instead (docs/roadmap.md). |
| **Final (v2.5)** | Section-based generation + hybrid retrieval + narrative-state deprioritization + category-scoped exclusion = `identityos_v2_5`. | Evidence coverage 0.95, unsupported-claim rate 0.05, repeated-evidence rate 0.32, vs. 0.00/1.00/n-a for both baselines. | Main contribution: the first real generated artifact, with a genuinely new finding (evidence can be true, grounded, *and* out of scope) that no prior verification dimension caught. |

## Main failure mode, v2.5 (see docs/hot_take.md for the full writeup)

The application-specific exclusion fix operates at the whole-fact level;
the contamination it was built to catch also exists at the sentence level,
inside facts that are otherwise correctly scoped as general. This is the
same granularity mismatch as v2.2's negation fix (sentence vs. clause),
now appearing a third time (fact vs. sentence). The honest fix — rewrite
source facts to strip role-specific framing, or LLM-assisted neutral
rephrasing at generation time — needs its own evaluation and a real
provider key respectively; neither was attempted reactively here.
