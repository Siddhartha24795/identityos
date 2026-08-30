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
| Evidence coverage | 0.00 | 0.00 | **0.95** | +0.95 |
| Unsupported claim rate | 1.00 | 1.00 | **0.05** | −0.95 |
| Hard-case overclaim rate (4 cases) | 0.00* | 0.00* | 0.00* | see limitation below |
| **Identity Fidelity Score** | 0.20 | 0.20 | **0.96** | +0.76 |
| Human time per task | not measured | not measured | not measured | requires a live user study — v2 |
| Cost per task | $0 (mock) | $0 (mock) | $0 (mock) | re-run with a real key for $/1k tokens |

Reproduce: `python scripts/build_digital_self.py && python scripts/run_eval.py mock v1_mock`.

*Numbers updated twice since v1 shipped: once when v2 added a single
previously-untranscribed sentence, and again when v2.1's general
corpus-completion pass (docs/evaluation_v2.md) added the rest of the
source dossier's content. v1 and v2 share one Digital Self, so completing
the corpus for v2's benefit improved v1's retrieval too. This is expected
and correct: the source of truth is always "run the script," never a
number frozen in a doc.*

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
a qualifier than an extractive mock is. Re-run with `PROVIDER=anthropic`,
`PROVIDER=openai`, or `PROVIDER=groq` (groq is free, no credit card —
https://console.groq.com/keys) to get a real measurement of this gap —
see docs/hot_take.md, which turns this exact limitation into the
project's main insight.

**A real-model run is much slower than the mock, and by an uneven
amount.** With `PROVIDER=groq` (`openai/gpt-oss-120b`, a reasoning
model), individual `baseline_plain`/`identityos_v1` calls typically return
in under a few seconds, but `baseline_rag` calls — which dump the entire
~100-fact store as unstructured context, by design (see above) — routinely
take 10-30 seconds each, because the model spends most of its token
budget on hidden reasoning over that much text before answering. The full
19-question v1 benchmark (57 calls total) takes on the order of 6-10
minutes with a real reasoning model, versus under a second with the mock
provider. This is expected, not a hang — worth knowing before assuming a
real-provider run has stalled.

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

## v3.3: the first real-model run (`PROVIDER=groq`), and what it found

Every "re-run with a real provider" line in this project's docs had been a
deferred next step until now. `PROVIDER=groq` (free, no credit card —
https://console.groq.com/keys, `openai/gpt-oss-120b` via Groq's
OpenAI-compatible endpoint) made that actually possible, and running it
for the first time surfaced three real findings in one pass — exactly the
pattern behind every other discovery in this project: build it, then read
the actual output, don't just trust the score.

### Result (`PROVIDER=groq`, `openai/gpt-oss-120b`)

| Metric | baseline_plain | baseline_rag | identityos_v1 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | 0.78 |
| Unsupported claim rate | 1.00 | 1.00 | 0.22 |
| Hard-case overclaim rate (4 cases) | **0.25 (1/4)** | 0.00 | 0.00 |
| Refusal count | 0 | 0 | 5 |
| **Identity Fidelity Score** | 0.15 | 0.20 | **0.824** |

The core thesis holds with a real model: identityos_v1 still beats both
baselines by a wide margin (0.824 vs. 0.15/0.20). But three numbers here
are worse than the mock-provider reference run (0.958 IFS, 0.947
coverage, 0 refusals) — and reading the actual answers explains why, and
it's not simply "the real model is worse."

### Finding 1 — baseline_plain, with zero context, fabricates specific, detailed, self-contradictory answers a mock never could

The mock-provider reference run's own limitation section (above) already
predicted this: an extractive, non-generative stand-in can't hallucinate
the way a real LLM does. The real run confirms it concretely. Given zero
context, `openai/gpt-oss-120b` invented, verbatim:

- **q13 (patent credit):** a complete fake patent — `U.S. Patent No.
  12,345,678`, titled *"Generative-AI-Driven Adaptive Video Codec"*, filed
  "March 2024," issued "November 2025" — followed by four paragraphs of
  invented technical detail ("I designed a conditional diffusion
  network...", "I devised a lightweight RL agent...") with zero mention
  of the real 75%/25% shared inventorship.
- **q17 (professional-body leadership):** *"Yes. I have spent the past
  three years overseeing the operations of a regional professional
  association for engineers... I grew our active membership base by 28%
  and increased renewal rates from 62% to 81%"* — a fully fabricated
  three-year role with fabricated statistics. The real answer is that
  this person has never done this.
- **q14**, a differently-worded version of the *same* underlying real-world
  fact as q17, got the opposite answer from the same context-free model in
  the same run: *"I have not founded or run a professional body... to
  date."* Two phrasings of one fact, one confident yes and one confident
  no, from the same system with zero real information either time — a
  clean, concrete demonstration that a context-free LLM's answers aren't
  drawn from any actual belief about the person, real or otherwise.

### Finding 2 — the hard-case overclaim detector, tuned against the mock's phrasing, missed 2 of these 3 severe fabrications

`hard_case_overclaim_rate` reported only **1 of 4** hard cases as
overclaimed (q15 — a fabricated claim of Kannada fluency, which happened
to use the literal phrase `"fluent in Kannada"` the rule checks for).
q13's fake patent and q17's fake leadership role — arguably the two most
severe fabrications in the entire run — were **not** flagged, because
`_HARD_CASE_RULES` (`services/evaluation/scoring.py`) checks for exact
phrases like `"my patent"` / `"i hold the patent"` and `"yes, i have run"`
/ `"i founded and ran"`, calibrated against the mock provider's specific
extractive phrasing. The real model's actual wording (`"I hold U.S. Patent
No..."`, `"Yes. I have spent the past three years overseeing..."`) never
matches those exact strings, so both cases fall through to "no confident
assertion detected either way" and score as safe. **Not fixed in this
pass** — a more general check (e.g., an LLM-based "does this text assert
sole credit/a leadership role" classifier, replacing today's rule-based
phrase list) is a real v3.4+ candidate, named here rather than patched
with a fifth or sixth hand-picked phrase, per this project's established
position on that exact kind of fix (docs/hot_take.md's "the experiment we
removed"). The mock-provider score of 0.00 dangerous/hard-case overclaims
was never a claim that the *system* has no failure mode here — it was
always a claim that *the mock provider's extractive style* doesn't
exercise it. This is the first time a real generative model exercised it,
and the detector's blind spot is now measured, not assumed away.

### Finding 3 — a real, root-cause bug: the citation-parsing regex only ever matched the mock provider's exact bracket style

`identityos_v1`'s 5 refusals looked, at first, like the confidence-gated
refusal policy finally working as designed on genuinely hard questions.
Reading the actual trajectory for q13 (the patent question) showed
otherwise: the model generated a **correct, properly-hedged, honestly
cited** answer — *"According to the inventorship record I have provided,
I contributed 75% of the inventive work on this filing, with the
remaining 25% attributed to a co-inventor..."* — citing real evidence as
`[ dossier_excerpts:002 ]`. The verifier's citation regex
(`services/qa_engine/verification.py`) required zero whitespace inside
brackets (`[id]`, the only shape the deterministic MockProvider ever
produces) and a single id with no separator — so `[ dossier_excerpts:002
]` (space-padded) and `[dossier_excerpts:001; dossier_excerpts:002]`
(two ids in one bracket) both silently failed to parse as citations,
undercounting evidence and dragging confidence to 0.36 — below the 0.5
refusal threshold — for a completely correct, well-grounded answer. A
second, related format (`【dossier_excerpts:001】`, fullwidth CJK brackets
this specific model sometimes emits) had the identical failure mode.

**Fixed at the root** in `verification.py`: capture raw bracket contents
(either ASCII `[...]` or fullwidth `【...】`) and split on `,`/`;`,
instead of requiring one tightly-formatted ASCII id per bracket. Re-ran
every mock-provider suite afterward (v1, all three v2 retrieval arms,
v2.5, v3) — byte-identical to every previously documented number, since
the mock provider's own citations were always in the one format the old
regex already handled. **Re-verified offline against the same raw
model outputs already collected** (re-running `verify_answer()` over the
trajectory-logged generation text, not a new API call — Groq's free-tier
daily token cap was reached before a fresh live re-run could be done; see
below):

| Metric | Before fix | After fix (offline re-verification, same raw outputs) |
|---|---|---|
| Evidence coverage | 0.78 | 0.798 |
| Unsupported claim rate | 0.22 | 0.202 |
| Refusal count | **5** | **1** |
| Identity Fidelity Score | 0.824 | 0.838 |

**4 of the 5 refusals (q10, q13, q16, q17) were pure artifacts of the
bracket-formatting bug, not genuinely weak evidence** — their confidence
jumped from 0.36-0.4 to 0.61-0.86 once their existing, correct citations
were actually counted. Only q06 remains refused, which is a real,
unrelated case (docs/hot_take.md's original v1 finding about relevance
vs. grounding still applies there). This is the same shape of bug as
v3.0's MockProvider parsing fix — infrastructure built and tested against
exactly one caller's output format quietly breaking the moment a
differently-formatted caller (here, an actual generative model instead of
an extractive one) exercises it for the first time.

### Token efficiency, found the hard way

The same `q13` trajectory that surfaced Finding 3 also showed
`openai/gpt-oss-120b` is a reasoning model: with no `reasoning_effort` set
(the API default), a 600-token budget for that single call was consumed
585 tokens by hidden chain-of-thought reasoning, leaving 15 tokens for the
actual answer — which is why some answers in this run are visibly cut off
mid-sentence. Measured directly (`services/providers/groq_provider.py`):
setting `reasoning_effort="low"` cut per-call reasoning-token consumption
by roughly 5-25x in side-by-side testing on this project's short,
structured completions, with no observed loss of answer correctness or
citation quality. **This is now the provider's default** — see its
module docstring for the measurement, not just the claim.

The default-reasoning-effort run above also consumed nearly this
project's entire Groq free-tier daily token allowance (200,000 TPD) by
itself — a `RateLimitError` blocked a fresh, `reasoning_effort="low"`
re-run of the full suite from completing in this session. **The numbers
in the "after fix" row above come from offline re-verification of
already-collected outputs, not a second live run** — disclosed here
rather than left implicit. A fresh end-to-end run with the low-effort
default, once quota resets, is expected to reproduce very similar answers
using a small fraction of the tokens the first run needed — that
re-verification is the natural next step, not yet done as of this
writing.
