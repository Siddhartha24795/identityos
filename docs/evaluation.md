# Evaluation

## Primary metric: Identity Fidelity Score

`0.4 * evidence_coverage + 0.4 * (1 - unsupported_claim_rate) + 0.2 * (1 - hard_case_overclaim_rate)`
(services/evaluation/scoring.py). Evidence coverage and groundedness are
measured for every answer via per-sentence verification
(services/qa_engine/verification.py); the hard-case term is hand-checked
against four questions with known ground-truth qualifiers (patent credit,
governance experience, language fluency — see below).

**Why this metric, not raw factual accuracy**: baselines have no
verification mechanism at all, so "is this claim checkable" is the
bottleneck this project targets, ahead of "is this claim correct." A
system that never lets an unverifiable claim through is the actual product
being built.

## Reference run (offline, `PROVIDER=mock`, reproducible with zero API keys)

19 questions, `data/evaluation/results/v1_mock/summary.json`:

| Metric | baseline_plain | baseline_rag | identityos_v1 | Change (system vs. best baseline) |
|---|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.93** | +0.93 |
| Unsupported claim rate | 1.00 | 1.00 | **0.07** | −0.93 |
| Hard-case overclaim rate (4 cases) | 0.00* | 0.00* | 0.00* | see limitation below |
| **Identity Fidelity Score** | 0.20 | 0.20 | **0.95** | +0.75 |
| Human time per task | not measured | not measured | not measured | requires a live user study — v2 |
| Cost per task | $0 (mock) | $0 (mock) | $0 (mock) | re-run with a real key for $/1k tokens |

Reproduce: `python scripts/build_digital_self.py && python scripts/run_eval.py mock v1_mock`.

### Why evidence coverage / unsupported-claim-rate is a fair, provider-independent comparison

Neither baseline has *any* citation or verification mechanism, by
construction — that's what makes them baselines. A 0.00 evidence-coverage
score isn't an artifact of the mock provider; it's structurally true of
"one direct prompt" and "LLM + resume dump" regardless of which model
generates the text. This part of the result would hold with a real LLM too.

### *Limitation: the hard-case overclaim metric is NOT yet demonstrative

All three systems scored 0.00 overclaim rate on the four hard cases (q13
patent credit, q14 professional-body governance, q15 Kannada fluency, q17
institutional experience) — but for two different reasons, and only one of
them is real:

- **identityos_v1** genuinely surfaced the qualifiers correctly (see
  trajectory excerpts below) — this result is real.
- **baseline_rag** also happened to avoid overclaiming, but only because
  the mock provider is **extractive, not generative**: it copies matching
  source sentences verbatim rather than paraphrasing them, so a qualifier
  like "75%" survives by accident, not by design. baseline_rag has no
  instruction to preserve qualifiers and no mechanism to check if it did.
- **baseline_plain** avoided overclaiming by producing *no specific claim at
  all* (generic filler) — this is not a good outcome, it's a different
  failure mode already fully captured by its 0.00 evidence-coverage score.

**This is the single most important limitation of the reference run**: a
real generative LLM given naive unstructured RAG context, no citation
requirement, and length pressure is meaningfully more likely to smooth over
a qualifier than an extractive mock is. Re-run with `PROVIDER=anthropic` or
`PROVIDER=openai` (requires an API key) to get a real measurement of this
gap — see docs/hot_take.md, which turns this exact limitation into the
project's main insight.

## The four hard cases (verbatim from the reference run)

**q13 — patent credit.** Evidence states a 75%/25% shared inventorship.
- identityos_v1: `[dossier_excerpts:002] ... Siddhartha's stated inventorship contribution on this patent is 75%, with the remaining 25% attributed to a co-inventor...`
- baseline_plain: generic filler, no specific claim, no qualifier — never engages with the real evidence at all.

**q14 — professional-body governance.** Evidence states this is an admitted gap.
- identityos_v1 and baseline_rag both correctly surface: `...he has no prior record of building or running a professional membership body...`
- baseline_plain invents nothing specific, but also asserts nothing true.

**q15 — Kannada fluency.** Evidence states no current fluency, only a
forward commitment to learn.
- identityos_v1: `...he is fluent in English and Hindi but not yet in Kannada...` — correctly qualified.

**q17 — institutional governance (paired belief with counter-evidence).**
Tests `belief:003` (confidence 0.45, has counter-evidence) directly.
- identityos_v1 surfaces the counter-evidence fact itself rather than
  asserting the belief — the correct behavior for a sub-threshold belief.

## Question bank composition

19 questions across 6 types (data/evaluation/question_bank.json): 5
factual, 5 unseen-inferential (the spec's named hard cases — "what failure
taught you the most", "why should we choose you", etc.), 2 ambiguous, 3
adversarial, 2 contradictory, 2 long-horizon. Every question's `notes`
field states what it specifically tests.

## Known v1 limitation found via this run (not in the original design)

Refusal never triggered (`refusal_count: 0` for identityos_v1 across all 19
questions, including the 5 unseen-inferential ones). Investigating why
revealed a real gap: verification confidence reflects *source fidelity*
(is this fact true?) not *question relevance* (is this fact a good answer
to THIS question?). See docs/hot_take.md.
