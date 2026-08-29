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

Reproduce: `python scripts/run_eval_v2.py mock v2_mock` (after
`python scripts/build_digital_self.py`).

## Two metrics, because one hides the important thing

| Metric | baseline_plain | baseline_rag | identityos_v2 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.74** |
| Assessment agreement rate (14 reqs) | 0.07 | 0.07 | **0.29** |
| Dangerous overclaim rate (4 non-MET reqs) | 0.00* | 0.00* | **0.25** |

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
for, and it is genuinely improved (0.07 -> 0.29) — but it is a noisier
signal than it looks**, because it penalizes a safe underclaim (system says
`partial`, real answer is `met_or_better`) exactly as harshly as a
dangerous overclaim (system says `met_or_better`, real answer is `partial`
or `gap`). Those are not equally bad. **Dangerous overclaim rate isolates
the one that matters**: of the 4 requirements where the honest answer was
not a clean MET, identityos_v2 confidently overclaimed on 1 (see below) —
a real number worth investigating further, not a solved problem.

## The req14 story: found a real bug, fixed part of it, documented what's left

Requirement 14 ("record of building or running a professional body") is
the single most important case in this benchmark — the real answer is
`gap`, in the person's own words. The first version of v2 retrieved and
correctly *cited* the exact fact that states this gap
(`data/evaluation/results/v2_mock/trajectories/req14__identityos_v2.md` —
see the earlier version in git history / improvement_changelog.md), and
still bucketed it `met_or_better`, because the bucketing rule only looked
at evidence coverage and confidence — both of which were high, because the
citation was accurate. **A well-grounded claim can be a well-grounded "no."**
Coverage and confidence alone cannot tell those apart.

Fix: `bucket_from_signals` now also checks cited claim text for lexical
negation markers ("no prior", "not yet", "has no", ...) and downgrades the
bucket when a majority of cited claims are negative
(`services/application_engine/bucketing.py`). This is a general rule, not a
req14-specific patch — it changed several other requirements' scores too,
for better (req09 correctly moved from an unmet-because-missing-evidence
gap to a correct `partial`, after also completing a genuine corpus gap —
see docs/improvement_changelog.md) and for worse in one case
(req08 still overclaims — see below).

## What's still wrong (not hidden)

**req08 (Revenue & P&L management, real = `partial`) is a dangerous
overclaim**: the system says `met_or_better`. Tracing the trajectory
(`data/evaluation/results/v2_mock/trajectories/req08__identityos_v2.md`)
shows the real cause is the same one req09 originally had: the actual
qualifying sentence ("full institutional P&L at IITACB's scale would be a
step up... experience I do not have") was never transcribed into
`data/identity_sources/`. Retrieval instead surfaced two loosely-related,
correctly-cited-but-wrong facts (an old fraud-detection/revenue-forecasting
role, and an unrelated smartwatch power-management project) — both real,
both well-grounded, neither the right evidence, and neither containing a
negation marker to catch.

We deliberately did **not** patch this one the way req09 was fixed, even
though the fix is textually identical (transcribe the real missing
sentence). Two corpus completions already happened in this build in direct
response to specific failing eval cases; a third would start to blur into
tuning the corpus until the 14 known cases pass, rather than genuinely
completing it. The honest scope statement is in
docs/roadmap.md v2.1: the identity source files are a curated *subset* of
the two source documents, not a full transcription — and until that's
addressed as a general corpus-completeness pass (not case-by-case), req08
stays a documented, open, real failure.

**req13 (Kannada fluency, real = `partial`) now underclaims to `gap`.**
Safer direction than an overclaim, but still wrong: the single retrieved
sentence mixes a positive clause ("fluent in English and Hindi") and a
negative one ("not yet in Kannada"), and the negation check operates on
the whole sentence, not the clause. See docs/hot_take.md and
docs/roadmap.md v2.1 for the fix this points to (clause-level negation).

## What this run does and doesn't prove

Same mock-provider caveat as v1 (docs/evaluation.md): the mock provider is
extractive, not generative, so it tends to preserve source wording
(including qualifiers) rather than smoothing them away under paraphrase
pressure. A real LLM run (`PROVIDER=anthropic` / `PROVIDER=openai`) is the
next step for a qualitative read on whether these same failure patterns
get better or worse under real generation.
