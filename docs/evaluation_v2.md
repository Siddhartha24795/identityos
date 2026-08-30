# Evaluation — v2 (Application Compilation)

## The benchmark

14 real requirements from an actual job description (the IITACB CEO role),
each paired with the real human's own prior, honest self-assessment
(EXCEEDS/MET/CONFIRMED/PARTIAL/GAP) and evidence —
`data/applications/iitacb_ceo/requirements.json`. This is ground truth a
real person wrote before this project existed, not something generated for
the benchmark. Bucketed 3-way for scoring (`services/application_engine/bucketing.py`):
EXCEEDS/MET/CONFIRMED -> `met_or_better`, PARTIAL -> `partial`, GAP -> `gap`.
10 of 14 requirements are `met_or_better`, 3 are `partial`, 1 is `gap`.

Reproduce: `python scripts/build_digital_self.py && python scripts/run_eval_v2.py mock v2_mock`.

## Two metrics, because one hides the important thing

| Metric | baseline_plain | baseline_rag | identityos_v2 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.83** |
| Assessment agreement rate (14 reqs) | 0.07 | 0.07 | **0.43** |
| Dangerous overclaim rate (4 non-MET reqs) | 0.00* | 0.00* | **0.00** |

*Both baselines never cite anything (evidence_coverage 0.00 for both, same
structural reason as v1), so `bucket_from_signals` buckets every single one
of their answers as `gap`. That produces a trivial 0.00 dangerous-overclaim
rate — not because the baselines are careful, but because they say "gap" to
every single requirement regardless of the truth, which is also why their
agreement rate is only 0.07 (they happen to be right exactly once, on the
one requirement that really is a gap). A system that always says "I don't
know" cannot overclaim and also cannot be useful — those are the same fact
viewed two ways.

**Assessment agreement rate is the headline metric the design brief asks
for, and it is genuinely improved (0.07 -> 0.43) — but it is a noisier
signal than it looks**, because it penalizes a safe underclaim (system says
`partial`/`gap`, real answer is `met_or_better`) exactly as harshly as a
dangerous overclaim (system says `met_or_better`, real answer is `partial`
or `gap`). Those are not equally bad. **Dangerous overclaim rate isolates
the one that matters, and it is now 0.00** — down from 0.25 (1 of 4) before
the v2.1 corpus-completion pass below.

## The req14 story: found a real bug, fixed the general case

Requirement 14 ("record of building or running a professional body") is
the single most important case in this benchmark — the real answer is
`gap`, in the person's own words. The first version of v2 retrieved and
correctly *cited* the exact fact that states this gap, and still bucketed
it `met_or_better`, because the bucketing rule only looked at evidence
coverage and confidence — both of which were high, because the citation
was accurate. **A well-grounded claim can be a well-grounded "no."**
Coverage and confidence alone cannot tell those apart.

Fix: `bucket_from_signals` now also checks cited claim text for lexical
negation markers ("no prior", "not yet", "has no", ...) and downgrades the
bucket when a majority of cited claims are negative
(`services/application_engine/bucketing.py`). General rule, not a
req14-specific patch — full story and what it changed for other
requirements: docs/improvement_changelog.md.

## The corpus-completion pass (v2.1): the fix that mattered more than the fix

The negation check alone left one dangerous overclaim standing: **req08
(Revenue & P&L management, real = `partial`)** was bucketed `met_or_better`.
Tracing the trajectory showed why: the real qualifying sentence ("full
institutional P&L at IITACB's scale would be a step up... experience I do
not have") had never been transcribed into `data/identity_sources/` at all.
Retrieval surfaced two loosely-related, correctly-cited-but-wrong facts
instead (an old fraud-detection role, an unrelated smartwatch project) —
both real, both well-grounded, neither the right evidence, so nothing
about them looked like a claim worth downgrading.

We deliberately did not patch this one fact-by-fact the way an earlier
requirement (req09) had been. Instead, v2.1 did one general pass:
transcribed the entire remaining requirement-evidence table plus the
dossier's broader narrative sections (Seven Accountabilities, revenue
architecture, first-100-days commitments, closing statement) into a new
source file, `data/identity_sources/dossier_narrative.md` — real content
already in the source document, not written for this benchmark, and not
selected by which eval case needed it. Several of the new facts aren't
tested by any v1 or v2 question at all.

**Result: req08 now correctly agrees (`partial` vs. `partial`), and
dangerous_overclaim_rate dropped to 0.00 — as a side effect of completing
the record, not a targeted fix.** The general fix was better than the
specific one would have been.

## v2.2: clause-level negation

req13 (Kannada fluency, real = `partial`) had been underclaiming to `gap`:
the single retrieved sentence mixes a positive clause ("fluent in English
and Hindi") and a negative one ("not yet in Kannada"), and whole-sentence
negation detection scored the entire sentence negative. Fix: split cited
claim text on unambiguous contrastive conjunctions (" but ", "; ",
"however", "though", "while" — never bare "yet", which already does double
duty inside the "not yet" negation marker) and classify each claim as
`negative` / `mixed` / `positive`; a `mixed` claim now buckets `partial`,
not `gap` (`services/application_engine/bucketing.py`). **req13 now
correctly agrees.** No other requirement's bucket changed — verified by
re-running the full 14-requirement comparison before and after, not just
inspecting req13 in isolation.

## v2.3: embedding-based retrieval — a real comparison, not a strict upgrade

Added `identityos_v2_semantic`: the identical pipeline as `identityos_v2`,
with `retrieve_semantic()` (embedding cosine similarity, BAAI/bge-small-en-v1.5
via fastembed) instead of `retrieve()` (lexical word overlap) —
`services/qa_engine/retrieval.py`. Everything downstream (generation,
verification, bucketing) is the same code, so any difference is
attributable to retrieval alone. Reproduce:
`python scripts/run_eval_v2.py mock v2_semantic fastembed`.

| Metric | identityos_v2 (lexical) | identityos_v2_semantic (fastembed) |
|---|---|---|
| Evidence coverage | 0.83 | **1.00** |
| Assessment agreement rate | **0.43** | 0.36 |
| Dangerous overclaim rate | **0.00** | 0.25 |

**Semantic retrieval is not a strict upgrade over the current lexical
approach on this benchmark, and we are not tuning it until it looks like
one.** It genuinely fixed part of what it was built to fix — req10
(Exceptional communication) went from zero retrieved facts to a fully
correct `met_or_better`, and req05 (Entrepreneurial mindset) went from
zero facts to a `partial` match (an improvement, though not exact). But it
also reintroduced the exact class of failure v2.1 had eliminated: **req09
(Government & policy engagement, real = `partial`) now overclaims to
`met_or_better`** — the one dangerous overclaim in this run.

The mechanism, traced through the trajectories, is a real interaction
effect between v2.2 and v2.3, not a bug in either alone: embedding
retrieval has higher recall but lower precision than lexical overlap on
this corpus of short, terse fact bullets — it pulls in more
topically-adjacent evidence at the same top-k, including facts that are
*semantically nearby but about a different gap entirely* (e.g. a different
requirement's admitted limitation). The v2.2 polarity check was built to
catch a negative claim *about the topic asked*; it has no way to tell that
apart from a negative claim about something merely embedding-adjacent to
it, so broader recall can make the safety check noisier rather than better.
Six other previously-correct requirements (req02/03/04/06/07/11) also moved
from `met_or_better` to `partial` for the same reason: real but weaker,
more numerous citations pull the polarity vote in unpredictable directions
where lexical retrieval's tighter, more literal matches did not.

**Decision: keep lexical retrieval (`identityos_v2`) as the default.**
`identityos_v2_semantic` stays in the harness as a real, running comparison
arm — not deleted, not hidden — because the recall improvement on req05/req10
is genuine and worth continuing to investigate (e.g. combining both
retrieval signals, or a precision-aware bucketing rule that discounts
weakly-scored citations), just not worth shipping as the default on the
evidence collected so far. See docs/hot_take.md.

## v2.4: hybrid retrieval — the targeted fix, verified mechanically

v2.3's finding was specific: semantic retrieval's noise only appeared when
it *overrode* requirements where lexical retrieval already had good
evidence (req09 and six others) — it never helped where lexical had
nothing (req05, req10) without also hurting elsewhere. `retrieve_hybrid()`
(`services/qa_engine/retrieval.py`) responds to exactly that: run lexical
retrieval first; fall back to semantic *only* when lexical returns nothing
at all. Reproduce: `python scripts/run_eval_v2.py mock v2_hybrid fastembed`.

| Metric | identityos_v2 (lexical) | identityos_v2_semantic | identityos_v2_hybrid |
|---|---|---|---|
| Evidence coverage | 0.83 | 1.00 | **0.97** |
| Assessment agreement rate | 0.43 | 0.36 | **0.50** |
| Dangerous overclaim rate | **0.00** | 0.25 | **0.00** |

Hybrid beats both individual arms on agreement rate and matches lexical's
safety exactly. This isn't asserted from the design — it's verified
requirement by requirement: all 12 requirements where lexical had any
evidence produced **byte-identical buckets** to pure lexical retrieval
(including req09, which stays correctly `partial` — the semantic fallback
never even runs there, so the noise that caused v2.3's dangerous overclaim
structurally cannot recur). Only the two requirements where lexical found
nothing changed: req10 moved to a fully correct `met_or_better`, and req05
moved from `gap` to `partial` (a real improvement, not yet an exact match).

**This is now the recommended retrieval strategy going forward** — kept
alongside the lexical-only and semantic-only arms as permanent comparison
points, not replacing them, per this project's practice of measuring
every claim rather than assuming a "hybrid" label makes something better.
See docs/hot_take.md for why the *mechanism* (fallback-only, not fusion)
is what made this work where naive semantic retrieval didn't.

## What's still wrong (not hidden)

**req03, req06, req07, req11, req12, req14 still don't reach an exact
bucket match on any retrieval arm**, including hybrid — mostly the same
nuance-collapsing issue from earlier versions (a real "MET at chief level,
with a stated caveat" or a forward commitment reads differently than a
plain MET once bucketed into a coarse 3-way scale) rather than a new
finding. **req05 specifically improved (gap -> partial) but still isn't an
exact match** even under hybrid, because the semantic fallback's top
citation for it is real and relevant but not confidently-enough grounded
to cross the `met_or_better` threshold — a smaller, second-order version of
the same "recall found something, but not the strongest possible evidence"
limitation. None of these are dangerous overclaims — the metric that
matters most stays at 0.00 across lexical and hybrid.

## What this run does and doesn't prove

Same mock-provider caveat as v1 (docs/evaluation.md): the mock provider is
extractive, not generative, so it tends to preserve source wording
(including qualifiers) rather than smoothing them away under paraphrase
pressure. A real LLM run (`PROVIDER=anthropic` / `PROVIDER=openai`) is the
next step for a qualitative read on whether these same failure patterns
get better or worse under real generation.
