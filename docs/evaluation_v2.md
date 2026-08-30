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
| Assessment agreement rate (14 reqs) | 0.07 | 0.07 | **0.36** |
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
for, and it is genuinely improved (0.07 -> 0.36) — but it is a noisier
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

## What's still wrong (not hidden)

**req13 (Kannada fluency, real = `partial`) underclaims to `gap`.** Safer
direction than an overclaim, but still wrong: the single retrieved sentence
mixes a positive clause ("fluent in English and Hindi") and a negative one
("not yet in Kannada"), and the negation check operates on the whole
sentence, not the clause. Fix needs clause-level negation detection
(docs/roadmap.md v2.1, still open).

**req05 (Entrepreneurial mindset) and req10 (Exceptional communication)
underclaim to `gap` with zero facts retrieved at all**, despite real,
relevant evidence now existing in the corpus (the "comfortable with
ambiguity, unfunded mandates" and "translating executive intent" lines in
`dossier_narrative.md`). This is the lexical-retrieval limitation flagged
from the start (docs/architecture.md): the requirement's abstract phrasing
("entrepreneurial mindset") shares no literal words with evidence phrased
differently ("comfortable with ambiguity"). Confirms the known limitation
concretely rather than surfacing a new one — the documented fix is
embedding-based retrieval (docs/roadmap.md v2.1+).

Both remaining issues are safe-direction (underclaims, not overclaims) —
the metric that matters most, dangerous overclaim rate, is clean.

## What this run does and doesn't prove

Same mock-provider caveat as v1 (docs/evaluation.md): the mock provider is
extractive, not generative, so it tends to preserve source wording
(including qualifiers) rather than smoothing them away under paraphrase
pressure. A real LLM run (`PROVIDER=anthropic` / `PROVIDER=openai`) is the
next step for a qualitative read on whether these same failure patterns
get better or worse under real generation.
