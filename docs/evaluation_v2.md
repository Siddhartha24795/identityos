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

## v2.6: fixing the source, not the classifier

v2.5 found that role-specific framing survives inside individual sentences
of otherwise-general facts, one level more granular than a whole-fact
category filter can reach. Rather than building a sentence-level
classifier, the actual root cause turned out to be an authoring error:
five bullets in `dossier_narrative.md` violated this project's own
one-fact-per-line ingestion rule by conflating a general capability
statement with a comparison drawn specifically to the IITACB Secretariat
role in the same sentence (e.g. "...building the function before
headcount exists — precisely the condition of a Secretariat being stood
up"). Split each into a general fact and a separate, correctly-tagged
`APPLICATION_SPECIFIC` one. This is a one-time authoring correction, not a
new classification mechanism, and not made because one eval case looked
bad — five bullets were affected; only one had been the visible symptom.

| Metric | before (v2.5) | after (v2.6) |
|---|---|---|
| identityos_v2 (lexical) agreement rate | 0.43 | 0.43 (unaffected) |
| identityos_v2_hybrid agreement rate | 0.50 | **0.57** |
| identityos_v2_hybrid dangerous overclaim rate | 0.00 | **0.00** (held) |
| identityos_v2_semantic agreement rate | 0.36 | 0.64 |
| identityos_v2_semantic dangerous overclaim rate | 0.25 | **0.50** |

req05 (Entrepreneurial mindset) is now a full, exact `met_or_better` match
under hybrid — up from a `partial` — because the general capability
statement is no longer diluted by an ambiguous role comparison. Hybrid's
dangerous overclaim rate held at 0.00 through a real corpus change, which
is itself evidence the fallback-only design is robust, not a threshold
tuned to one snapshot of data.

**identityos_v2_semantic's dangerous overclaim rate got worse (0.25 ->
0.50), on a *different* pair of requirements than before (req08 and req14
now, req09 previously).** This is not a regression to fix — it's further
confirmation of the v2.3 finding: semantic-only retrieval's precision
problem is inherent to the approach, not tied to one corpus snapshot, which
is exactly why it was never promoted to default and why hybrid's
fallback-only design (not raw semantic quality) is what makes the shipped
system safe.

## v2.5's document-generation letter, re-checked

The specific "Secretariat" comparison flagged in docs/hot_take.md's v2.5
addendum no longer appears in the generated cover letter. **A related,
distinct conflation of the same shape still exists in a different source
file** (`dossier_excerpts.md`'s "SELF-ASSESSED GAP" section mixes a
general capability-gap admission with "...the committee should not be
persuaded that adjacent experience... is equivalent to that record," where
"the committee" is IITACB's Managing Committee) — found by re-reading the
regenerated letter, not fixed in this pass. Named as the next item
(docs/roadmap.md v2.7) rather than expanded into this version, matching
this project's practice of shipping one diagnosed fix at a time.

## v2.7: the same authoring correction, applied to the file it was found in

The v2.6 fix was made in `dossier_narrative.md`. Re-reading the
regenerated letter (docs/evaluation_documents.md) found the identical
authoring pattern in a different file, `dossier_excerpts.md`'s
"SELF-ASSESSED GAP" section: a general capability-gap admission mixed with
"...the committee should not be persuaded that adjacent experience... is
equivalent to that record" (IITACB's Managing Committee), and a general
language-fluency fact mixed with a relocation commitment made specifically
for the IITACB role. Same fix as v2.6, same file-audit method, applied to
the file where it was actually found.

| Metric | before (v2.6) | after (v2.7) |
|---|---|---|
| identityos_v2 (lexical) agreement rate | 0.43 | **0.57** |
| identityos_v2_hybrid agreement rate | 0.57 | **0.71** |
| identityos_v2_hybrid dangerous overclaim rate | 0.00 | **0.00** (held) |
| identityos_v2_semantic agreement rate / dangerous overclaim rate | 0.64 / 0.50 | 0.64 / 0.50 (unchanged) |

req03 and req06 both moved from `partial` to a full, exact `met_or_better`
match under both lexical and hybrid retrieval — general leadership and
strategy facts that were previously diluted by an adjacent
application-specific clause are now clean, standalone citations. Hybrid's
dangerous overclaim rate held at 0.00 through a second real corpus change
in a row — two independent confirmations the fallback-only design doesn't
depend on the specific shape of any one corpus snapshot.
identityos_v2_semantic (standalone) was unaffected, consistent with it not
relying heavily on these two specific facts either way.

**The generated cover letter (docs/evaluation_documents.md) is now clean
of every application-specific phrase flagged across v2.5-v2.6** — no
"Secretariat" comparison, no "the committee," no relocation commitment.
Evidence coverage dipped slightly (0.95 -> 0.91) as a minor, disclosed side
effect of the corpus split changing which facts a couple of sections
retrieve — not chased further, since the qualitative goal (no scope
contamination) was achieved and verified by reading the output, the same
standard applied throughout this project.

## v2.8: an experiment that didn't pan out, kept in the record

Investigated the four remaining mismatches (req07, req11, req12, req14)
before assuming they were all the same coarse-3-bucket-scale issue. Two of
them (req07, req12) turned out to share a distinct, diagnosable mechanism:
lexical retrieval's inclusion bar is "at least one shared non-stopword
token," which is noisy — a fact can rank into the top-k on a single
incidental word overlap, and if that weakly-relevant fact happens to
contain a negation marker unrelated to the actual requirement, it wrongly
drags an otherwise strong, clearly-grounded answer down to `partial`. For
req07 ("Stakeholder management"), a fact about P&L management ("...this is
experience not yet held") got cited alongside the genuinely relevant one,
purely because "management" is a shared token. For req12 (relocation), an
unrelated government-relations fact containing "no prior" did the same.

The obvious general fix — raise the lexical inclusion bar to require 2+
shared tokens (`retrieve(..., min_shared_tokens=2)`, added as an optional
parameter, default unchanged at 1) — **was tested against the full
14-requirement benchmark, not assumed, and made things worse overall**:

| Metric | shipped default (min_shared_tokens=1) | tested (min_shared_tokens=2) |
|---|---|---|
| Agreement rate | **0.71** | 0.64 |
| Dangerous overclaim rate | **0.00** | **0.50** |

req07 and req12 did become exact matches. But req08 and req09 (both real
`partial`) flipped to dangerous `met_or_better` overclaims, because the
same weakly-shared-token facts that were noise for req07/req12 were the
*load-bearing correct evidence* for req08/req09's qualifiers — raising the
precision bar cut recall for cases that needed it. This is the same
retrieval-precision/recall tension as v2.3, appearing inside lexical
retrieval itself, not just at the lexical-vs-semantic boundary.

**Not adopted.** The parameter stays in the codebase (default=1, i.e. no
behavior change) because it's a legitimate, tested knob for future work —
see docs/roadmap.md v2.9 for the fix this actually points to
(relevance-weighted polarity checking, not a blanket inclusion-bar change).

## v2.9: the "real fix" from v2.8, tried, and also rejected

v2.8 named the fix that should work: weight the polarity vote by how
relevant each citation actually is, instead of a blanket inclusion-bar
change. Implemented it two ways, both tested against the full benchmark
before trusting either:

1. **IDF-weighted retrieval ranking** (`build_idf_table()`,
   `retrieve_idf()`, `services/qa_engine/retrieval.py`) — down-weight
   common tokens ("management," appears in many facts) relative to
   distinctive ones ("stakeholder," appears in one). This changed *rank
   order* correctly (the genuinely relevant fact for req07 does score
   higher than the irrelevant one) but didn't change what gets *included*:
   with a generous top-k, a fact ranked #2 is still retrieved and still
   cited, so reordering alone doesn't stop the noise.

2. **Relevance-dominance gating** (`bucket_from_signals(...,
   relevance_scores=...)`, optional parameter, backward compatible) — a
   negative/mixed citation only votes toward a downgrade if its IDF score
   is at least half the strongest citation's score in that context.

| Metric | shipped default | tested (relevance-dominance gating) |
|---|---|---|
| Agreement rate | **0.71** | 0.71 (unchanged) |
| Dangerous overclaim rate | **0.00** | **0.14** (2 of 14) |

req12 became a full exact match — the gate worked as intended there. But
**req14 — the single highest-stakes case in the whole benchmark — flipped
from a safe `partial` to a dangerous `met_or_better`**, because the fact
correctly stating the professional-body gap scored *lower* by IDF than
another, less central fact retrieved alongside it, so the gate excluded
the correct negative vote. req09 broke the same way. req07 wasn't even
fixed. **Not adopted** — shipped behavior is unaffected (verified via the
same eval harness, not just unit tests).

**The conclusion this points to, stated plainly: two independent,
reasonably-motivated heuristic fixes (v2.8's inclusion threshold, v2.9's
relevance weighting) both failed for a structurally similar reason** — a
purely lexical/statistical relevance signal is not a reliable proxy for
"is this the semantically central evidence for this specific
requirement." A fact can score highly by coincidence and score low for
the right reasons. This isn't a case of picking the wrong threshold or
weighting formula; it's evidence that the fix these two cases actually
need is semantic judgment, which lexical scoring cannot provide by
construction. See docs/hot_take.md for the full argument.

## What's still wrong (not hidden)

**req07, req11, req12, req14 still don't reach an exact bucket match under
the shipped default** (4 of 14, down from 6, unchanged since v2.7).
**req03, req05, and req06 are now fully fixed** (v2.6-v2.7, above) — no
longer on this list. Of the remaining four, three now have a specific,
understood cause rather than a generic "nuance" label:

- **req07, req12**: diagnosed in v2.8 — a weakly-relevant fact with an
  unrelated negation marker gets cited alongside the real evidence. Two
  independent fixes were tested against the full benchmark (v2.8: raise
  the lexical inclusion bar; v2.9: relevance-weighted polarity gating) and
  both rejected — each fixed part of this pair while introducing a *new*
  dangerous overclaim elsewhere (req08/req09 in v2.8; req09/req14 in
  v2.9). Left unfixed deliberately, with the conclusion this points to
  (lexical relevance scoring has hit a real ceiling here) recorded in
  docs/hot_take.md rather than patched around a third time.
- **req11**: genuinely low retrieval confidence (0.51, just under the 0.6
  threshold) rather than a negation false-positive — the honest "weak but
  real evidence" case the confidence threshold exists to catch.
- **req14**: the real `gap` case; system says `partial` (safe underclaim,
  not a match) — already understood since v2.1, and confirmed twice more
  fragile than it looks: both v2.8 and v2.9's rejected fixes broke it in
  different ways when tested, which is exactly why testing every claim
  against the full benchmark before shipping anything matters most on the
  cases that matter most.

None of the remaining four are dangerous overclaims *on the shipped
default* — the metric that matters most stays at 0.00 under both lexical
and hybrid, through three consecutive real corpus changes and two rejected
retrieval experiments now.

## What this run does and doesn't prove

Same mock-provider caveat as v1 (docs/evaluation.md): the mock provider is
extractive, not generative, so it tends to preserve source wording
(including qualifiers) rather than smoothing them away under paraphrase
pressure. A real LLM run (`PROVIDER=anthropic` / `PROVIDER=openai`) is the
next step for a qualitative read on whether these same failure patterns
get better or worse under real generation.

## v3 addendum: a shared-infrastructure bug in MockProvider, and what re-verifying it changed

Building v3 (browser automation, docs/evaluation_browser.md) surfaced a bug
in `services/providers/mock_provider.py` itself, not in anything v2-specific:
its prompt parser hardcoded the literal string `"QUESTION:"` to find where
context ends and the question begins. v1's prompts use that label; v2's
`assess.py` uses `"REQUIREMENT:"` instead — a label the old parser never
matched. When it failed to match, it silently fell back to treating the
*entire prompt*, including the requirement text itself, as both context and
question, so the requirement's own wording could be extracted as
"evidence" for itself. This was invisible in most cases because real
matching facts usually outscore a line that trivially matches itself; it
only became visible once v3's own field labels made the effect concrete
enough to trace (docs/hot_take.md's v3 addendum has the full mechanism).

Fixed generally in `mock_provider.py` only (no caller changed) — treats the
text after the last blank line as the query regardless of what header
precedes it. Per this project's standing practice, re-ran every existing
eval suite afterward rather than assuming a shared-infrastructure fix was
side-effect-free:

| System | Metric | Before fix | After fix |
|---|---|---|---|
| identityos_v2 (lexical) | agreement rate | 0.57 | **0.57 (unchanged)** |
| identityos_v2_hybrid | agreement rate / dangerous overclaim rate | 0.71 / 0.00 | **0.71 / 0.00 (unchanged)** |
| identityos_v2_semantic | agreement rate | 0.64 | **0.64 (unchanged)** |
| identityos_v2_semantic | dangerous overclaim rate | 0.50 (2/4) | **0.75 (3/4) — worse** |

The shipped default (hybrid) and the lexical arm were completely
unaffected — expected, since the bug's effect only shows up when retrieval
is already weak enough that the label text can out-rank real evidence, and
hybrid's fallback design keeps it out of that regime for every requirement
lexical can already answer. `identityos_v2_semantic`, which was never the
shipped path specifically *because* its dangerous-overclaim rate was
already the worst of the three arms, got measurably worse once the bug
that had been partially masking it was removed — a third real requirement
now overclaims under semantic-only retrieval. **This is not a new problem
introduced by the fix; it's the bug that was previously hiding part of an
existing one.** Not investigated further here, for the same reason as
before: `identityos_v2_semantic` standalone was already not the shipped
system, and this makes the case for keeping it that way stronger, not
weaker. Full mechanism and the parallel effect on v2.5's document
generation: docs/hot_take.md's v3 addendum, docs/evaluation_documents.md's
v3 addendum.
