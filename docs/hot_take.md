# Hot take

**Grounding metrics only check whether a claim traces to evidence — not
what the claim actually says. Confidence that measures "is this evidence
true" gets silently reused as a stand-in for "is this a good answer" and
for "is this a positive answer," and neither substitution is safe.**

v1 found the first substitution (relevance). v2 found the second
(polarity), independently, by running the same verification machinery
against a real, adjudicated application. Both read as the same underlying
mistake once you see them side by side. v2.3 then found a third, related
lesson: a verification layer's safety guarantee is coupled to the specific
error profile of whatever retrieval feeds it, so "improving" retrieval in
isolation can make the safety check worse, not better. v2.5 found a fourth:
grounded and true isn't the same as "the right evidence for this
document" — a fact can correctly describe the person and still be
narrative written for a different, specific context entirely.

## What we observed

v1's refusal policy (services/qa_engine/identityos_agent.py) is supposed to
hedge or ask the user when confidence is low on subjective/unseen
questions. Across all 19 questions in the reference run, including the five
hardest unseen-inferential ones ("what failure taught you the most?", "why
should we choose you?"), it never fired once
(`refusal_count: 0` — data/evaluation/results/v1_mock/summary.json).

The instinct is to read that as success: the system always found something
to say. It isn't. Tracing the verification logic
(services/qa_engine/verification.py) shows why: when a generated sentence
carries an explicit citation, its confidence is inherited directly from the
cited fact's *own* stored confidence — 0.99 for anything transcribed
verbatim from a source document. That number answers "did this really
appear in the resume?", which is a completely different question from "does
this actually answer what was asked?" A retrieved fact about smartwatch
battery life is 99% certain to be *true* and still a useless, evasive
answer to "what motivates your research?" — but because it got cited, it
inherited high confidence and sailed past the refusal gate.

## Why this matters beyond this project

This is the general failure mode behind "the agent always sounds
confident even when it's off-topic." A defense-in-depth verification
stack (RAG + citation + confidence scoring) is the current industry
standard for reducing fabrication (see docs/research_hypothesis.md), and it
genuinely reduces *hallucination*. It does nothing, by itself, about
*misdirection* — confidently citing something real that doesn't address the
question. Both look identical in a naive confidence score.

## What we'd build differently next (v1's plan — partially still open)

Confidence needs to be a product of two independently-estimated terms:
`P(evidence is true) x P(evidence actually answers this question)`. The
first is what v1 already measures well (grounding). The second requires
either an explicit relevance-scoring step between retrieval and generation,
or a verifier that checks the *question* against the *claim*, not just the
claim against its source. Neither existed in v1 because the original
design brief's verification-dimension list (docs/architecture.md) doesn't
name this distinction either — we found it by running the eval, not by
reading the spec more carefully. **Still not built** — v2 built the
polarity fix below instead, because it surfaced first and mattered more on
a real, adjudicated application. Relevance-scoring stays open for v2.1+.

## v2 addendum: the same mistake, a different substitution

Running the v1-style verifier against a real 14-requirement application
(docs/evaluation_v2.md) found a second, more dangerous instance of the same
underlying error. Requirement 14 asked whether the person has ever run a
professional membership body; the real, honest answer is no. IdentityOS
retrieved and *correctly cited* the exact sentence stating this gap — full
evidence coverage, 0.89 confidence — and the bucketing rule, which only
checked coverage and confidence, called it `met_or_better`. **A
well-grounded claim can be a well-grounded "no."** Confidence there was
standing in for "is this a positive answer," which it was never designed
to measure.

The fix (a lexical negation check on cited claim text,
`services/application_engine/bucketing.py`) caught this exact case, but
left one dangerous overclaim standing (req08) for a completely different
reason: the right evidence for that requirement had simply never been
transcribed into the Digital Self. **The fix that actually closed it
wasn't a smarter rule — it was completing the record.** A general
corpus-completion pass (docs/improvement_changelog.md, Iteration 6)
transcribed the rest of the same source document, without regard to which
eval question needed what, and req08 resolved as a side effect.

A second, smaller instance of the same "coverage/confidence isn't the
whole story" pattern showed up right after: a claim mixing a positive
clause ("fluent in English and Hindi") and a negative one ("not yet in
Kannada") was scored fully negative by whole-sentence detection, when the
honest read is "mixed" — safely fixed with clause-level splitting
(Iteration 7, v2.2). One safe (non-dangerous) failure remains — a lexical
retriever that can't match "entrepreneurial mindset" against evidence
phrased as "comfortable with ambiguity" — documented in
docs/evaluation_v2.md, not patched away with a keyword-list hack, because
that would be tuning to the two known failing terms rather than fixing the
general problem (embedding-based retrieval, its own version, v2.3).

The pattern across both versions: **grounding verification answers "did
this really come from evidence," and every time we've needed it to also
answer "does this evidence mean what the sentence around it implies," it
has silently failed to, in a different way each time.** That looks like a
property of grounding-based verification in general, not a bug specific to
either version — and the more durable fix, twice now, has been making the
underlying representation more complete rather than making the checking
logic cleverer.

## v2.3 addendum: "smarter" retrieval made the safety check less safe

The obvious next move after finding the polarity bug was to assume better
retrieval would help — embeddings instead of lexical overlap, so the
system stops missing evidence that exists but doesn't share literal words.
It does help, on exactly the two requirements it was built for (req05,
req10). It also **reintroduced a dangerous overclaim** the corpus-completion
pass had already eliminated (req09), and quietly downgraded six other
previously-correct requirements. Full numbers: docs/evaluation_v2.md.

The mechanism is the more interesting part. Embedding retrieval has higher
recall and lower precision than lexical overlap on this corpus of short,
terse fact bullets — it pulls in more *topically adjacent* evidence at the
same top-k, including facts that are semantically nearby but about a
*different* admitted gap entirely. The v2.2 polarity check has no way to
tell "this is a negative claim about the thing being asked" apart from
"this is a negative claim about something the retriever thinks is related."
Better recall made the input to that check noisier, not cleaner.

**The lesson generalizes past this one project**: retrieval quality and
verification quality are not independent variables you can improve one at
a time and expect the system to only get better. A safety check tuned
against one retrieval method's error profile can be actively defeated by
switching to a "better" retrieval method with a *different* error profile.
Anyone building a verification layer on top of a retriever should re-run
the verification's own eval every time the retriever changes — not just
check that retrieval got better on its own terms. We didn't chase a
threshold that would make embeddings look good; we reported the trade-off
and kept lexical retrieval as the shipped default.

## v2.4 addendum: the diagnosis, taken seriously, produced a real fix

Once the mechanism was understood — semantic retrieval's noise appeared
*only* when it overrode requirements lexical retrieval already had
evidence for, never when it was filling a genuine gap — the fix followed
directly: run semantic retrieval *only* as a fallback when lexical finds
nothing. `identityos_v2_hybrid` (docs/evaluation_v2.md) beat every other
arm on agreement rate and matched lexical's dangerous-overclaim rate
exactly, and this was verified requirement-by-requirement, not assumed: all
twelve requirements lexical could already answer produced byte-identical
outputs to pure lexical retrieval, including the one (req09) semantic
retrieval alone had broken.

The general point this adds to the first: **a correctly diagnosed
mechanism — not a bigger model, not a cleverer threshold — produces a fix
that's actually verifiable.** "Embeddings are more semantic, so they should
help" was the intuition behind v2.3, and it was wrong on its own terms.
"Semantic retrieval only ever hurt when it overrode a working answer" was
a mechanism, and building a fix that targets exactly that claim is what
made v2.4 checkable claim-by-claim rather than another number to trust on
faith.

## v2.5 addendum: grounded and true still isn't "the right evidence"

Building the first multi-paragraph artifact (a generic cover letter,
`services/document_engine/`) surfaced a fourth substitution, distinct from
the first three. The generated letter read like an application for one
specific prior role — "the Secretariat," "the committee" — because a
source section written as strategy narrative for that specific candidacy
got cited as if it were general evidence about the person. Every sentence
was real, true, and correctly grounded. No metric already built (evidence
coverage, unsupported-claim rate, polarity) would have caught it, because
none of them ask the question that matters here: is this evidence *in
scope* for what's being written, not just *true* of the person.

The fix — tagging that source section and excluding it from generic
document generation — closed the obvious case and, on inspection, did not
close a subtler one: individual sentences inside otherwise-general facts
still carry the same specific role's framing baked in ("precisely the
condition of a Secretariat being stood up"), because those facts were
transcribed by paraphrasing a table whose own language compared everything
to that one role. Category-level tagging operates on whole facts; this
contamination lives inside a sentence within a mostly-fine fact — the same
granularity mismatch as v2.2's negation fix, appearing a third time at a
different level. At the time this was written, it was an open, named item
rather than a hidden one — see the v2.6 addendum below for what turned out
to actually fix it.

## v2.6 addendum: the fix was correcting an authoring error, not building a classifier

The natural next move after v2.5 would be a sentence-level content-scope
classifier. That's not what fixed it. Tracing the contamination to its
source showed it wasn't a detection problem at all — it was an authoring
error: five bullets in one source file had conflated a general statement
with a role-specific comparison in the same sentence, violating this
project's own one-fact-per-line ingestion rule. Splitting each into a
general fact and a separately-tagged application-specific one is a
correction, not a new mechanism — and it measurably worked: req05 went
from a `partial` match to a full, exact one under hybrid retrieval, with
zero change to the safety metric, verified by re-running all three eval
suites rather than assumed from the diff.

The reason this doesn't collapse into "we edited the data because the eval
looked bad" (the exact pattern declined for req08 and req13): five bullets
were affected by the same authoring mistake, and only one had ever shown
up as a visible symptom. The other four weren't touched *because* some
test needed them fixed — they were touched because they had the identical,
independently-identifiable defect. That's the difference between
correcting a mistake and tuning a benchmark: one generalizes to content
nothing has tested yet, the other doesn't. Re-reading the regenerated
output surfaced a near-identical mistake in a *different* source file,
confirming this is a real authoring pattern worth watching for, not a
one-off.

## v2.7 addendum: applying the same correction where it was actually found

Fixed the near-identical conflation named at the end of v2.6, in the file
where it actually was (`dossier_excerpts.md`), the same way: split each
conflated bullet into a general fact and a separately-tagged
application-specific one. The regenerated letter is now clean of every
flagged phrase across two versions of this fix. The requirement-fit
benchmark moved again — req03 and req06 became exact matches, hybrid's
agreement rate rose from 0.57 to 0.71 — while its dangerous overclaim rate
held at 0.00 through a *second* consecutive real corpus change.

Two fixes of the identical shape, in two different files, both holding the
safety metric steady while measurably improving the accuracy one, is
stronger evidence than either fix alone that the mechanism — not luck, not
a threshold tuned to one snapshot — is what's doing the work. It's also a
concrete answer to "how do you know you're not just overfitting to what
you've already seen": the second fix was found by re-reading output *after
already believing the problem was solved*, and the discipline that caught
it (keep reading, don't declare victory at a passing score) is repeatable,
not a one-time insight.

## v2.8 addendum: the same weak evidence that hurts one requirement is what saves another

Diagnosed why two remaining mismatches (req07, req12) were wrong: a fact
sharing exactly one word with the requirement text ranked into the
retrieved set, carried an unrelated negation marker, and dragged an
otherwise-correct answer down. The obvious fix — require at least two
shared words before a fact counts as retrieved — is the kind of change
that looks safe in isolation and was tested, not assumed, against the full
benchmark before being trusted.

It made the dangerous-overclaim rate five times worse. The same
weak-single-token matching that was noise for req07/req12 turned out to be
the only thing keeping req08 and req09 honest — their correct `partial`
verdicts depended on citing a fact that shared just one word with the
requirement. Tightening precision for two cases silently starved two
others of the evidence that had been keeping them safe.

This is worth stating plainly because it's counterintuitive: **"this
specific match looks noisy" and "matches like this are noise in general"
are different claims, and only one of them is checkable by looking at the
case in front of you.** The same retrieval mechanism was simultaneously
the disease and the cure, for different requirements, at the same
threshold. We didn't ship the fix, and we didn't discover this by
reasoning about it — only by running the one experiment that would have
looked like a strict win if we'd stopped at the two cases we started from.

## v2.9 addendum: the real fix, tried properly, also didn't work — and that's the finding

v2.8 named what should have been the real fix: don't blanket-exclude weak
matches, *weight* the polarity vote by how relevant each citation actually
is. Built it two ways — IDF-weighted retrieval scoring, and a
relevance-dominance gate on the polarity vote — and tested both against
the full benchmark before trusting either, exactly the discipline v2.8
established.

Reordering by IDF correctly ranked the relevant fact above the irrelevant
one for req07, and changed nothing that mattered: with a generous top-k,
a fact ranked second is still retrieved and still cited. Rank isn't
inclusion. The relevance-dominance gate, which does affect inclusion,
fixed req12 — and flipped **req14, the single highest-stakes requirement
in the entire benchmark**, from a safe `partial` into a dangerous
`met_or_better`, because the fact stating the real professional-body gap
scored *lower* by IDF than an unrelated fact retrieved alongside it. The
gate excluded the correct negative vote for exactly the wrong reason.

Two independently-motivated fixes, built two different ways, both failed
on the same structural point: **a lexical or statistical relevance score
is not a reliable stand-in for "is this the fact that actually settles the
question."** A fact can score high by coincidence of vocabulary and score
low for the exact evidence that matters. Neither failure was a tuning
mistake — better thresholds or better weights wouldn't fix this, because
the signal being weighted isn't the signal the decision actually needs.
That's a boundary of what lexical retrieval can do here, not a bug in how
we used it, and it's the strongest argument in this project for why the
next real step is a system that can judge relevance semantically (a real
LLM call, not a token-overlap proxy) rather than a fourth heuristic aimed
at the same two requirements.

## v3 addendum: a fifth substitution, this time in the harness itself, not the pipeline

Every addendum above is about the pipeline substituting one question for
another — grounding for relevance, for polarity, for scope. v3 found the
same *shape* of mistake one level down, in the evaluation infrastructure
those pipelines share. `MockProvider.complete()` (`services/providers/mock_provider.py`)
parsed "where does context end and the question begin" by matching a
literal `"QUESTION:"` string. That was never a general contract — it was
v1's specific label, generalized to "the" label by an implicit assumption
nobody wrote down. v2's `assess.py` prompts with `"REQUIREMENT:"`, v2.5's
`document_engine/generate.py` with `"SECTION PROMPT:"`, and v3's own
`field_mapper.py` with `"FIELD LABEL:"` — every one of them silently fell
through to a fallback that treated the entire prompt, label included, as
its own context. A label can trivially "match itself" under word-overlap
scoring, so in exactly the cases where real retrieval was already weak,
the label text itself became the highest-scoring "evidence" and leaked
into the generated answer.

**This is the same lesson as v1's original finding, aimed at a different
layer**: a mechanism built and validated against one caller's shape
(v1's `"QUESTION:"` prompts) quietly stops being general the moment a
second caller uses a different shape, and nothing forces that gap to
surface — it hides behind whichever cases still have strong-enough
retrieval to outscore the self-match. It survived three versions
(v2.0-v2.5) built on top of it before v3's own field-label prompts finally
produced a case weak enough to make it visible in the actual trajectory
output — the same "read the actual output, not just the score" discipline
that found every other finding in this file, working exactly as intended,
just slower this time because the earlier callers' retrieval was usually
strong enough to mask it.

**The fix generalizes on purpose, not just to the four known callers.**
Rather than teaching the parser a fifth keyword, it now treats the text
after the last blank line as the query regardless of what header precedes
it — correct for any future caller's prompt shape, not just the ones this
bug happened to be caught by. Re-running every existing eval suite
afterward (the same discipline v2.6-v2.9 established for corpus changes,
now applied to a shared-infrastructure change) found the fix was inert for
every arm actually shipped as a default (v1, `identityos_v2` lexical,
`identityos_v2_hybrid`), and made `identityos_v2_semantic`'s already-worst
dangerous-overclaim rate honestly worse (0.50 -> 0.75) — a bug that had
been *partially hiding* a real weakness in a system that was already never
the shipped path. Full numbers: docs/evaluation_v2.md's v3 addendum,
docs/evaluation_documents.md's v3 addendum.

**The general point this adds**: a deterministic offline test harness is
supposed to be the one part of a project where "the answer is knowable
just by reading the code," and this bug shows that isn't automatic —
harness code needs the same "does this generalize past the one case that
motivated it" scrutiny as the pipeline it's testing, and re-running the
full regression suite after fixing shared infrastructure is not optional
paperwork, it's the only way to know a fix that looks purely additive
didn't also change a number three versions upstream.

## v3.3 addendum: the mock provider hid a bug in the pipeline itself, not just in the mock

Every "re-run with a real provider" line in this project's docs, since
v1, was a deferred next step — until v3.3, when `PROVIDER=groq` made a
real run actually free to try. It found the same underlying mistake as
v3's MockProvider bug, one layer deeper: **infrastructure built and
tested against exactly one caller's output shape breaks silently the
moment a differently-shaped caller exercises it, and the difference this
time wasn't between two of this project's own modules — it was between an
extractive stand-in and an actual generative model.**

The citation regex in `services/qa_engine/verification.py` required a
bracket to contain exactly one id with zero internal whitespace
(`[resume:014]`). That was never a documented contract; it was simply the
only shape `MockProvider` — deterministic, extractive, copy-pastes
source text — could ever produce. A real model pads brackets with spaces
(`[ resume:014 ]`), cites two ids in one bracket
(`[resume:014; belief:002]`), and this specific model sometimes uses
fullwidth CJK brackets (`【resume:014】`) instead of ASCII ones — three
real formats, one real run, all silently unparseable. The consequence
wasn't cosmetic: it dragged a **correct, honestly-hedged, properly-cited**
answer about the single highest-stakes question in the benchmark (the
patent-credit question, q13) below the refusal threshold, for a reason
that had nothing to do with the answer's actual quality. Re-verifying the
same generated text after the fix showed 4 of the run's 5 refusals were
pure artifacts of this bug, not genuinely low confidence.

**The general point, stated plainly**: this project's whole verification
and evaluation harness had run, byte-identical, dozens of times across
nine prior versions — and every one of those runs used the one LLM
backend that could never expose this defect. A deterministic mock
provider is exactly what a judge needs to reproduce a result with zero
setup (docs/evaluation.md's stated purpose for it), and it is also, by
construction, incapable of revealing any bug whose trigger condition is
"a real model's actual writing style." Neither property was wrong to
build; the lesson is that a codebase's zero-cost, always-green reference
path is not the same claim as "this code has been exercised," and the
gap between those two only shows up the first time something outside
that path actually runs.

**A second, independent finding from the same run**: the hard-case
overclaim detector (`_HARD_CASE_RULES`, mentioned below) — already
flagged in "the experiment we removed" as calibrated against the mock
provider's phrasing — turned out to have exactly the blind spot that
flag predicted, empirically, for the first time. Given zero context, the
real model fabricated a complete fake patent number and a fake three-year
nonprofit leadership role with fabricated statistics — arguably the two
most severe hallucinations anywhere in this benchmark — and neither
tripped the rule, because neither used the exact hand-picked phrases the
rule checks for. The rule caught the one hard case (Kannada fluency)
where the model's wording happened to match by coincidence. This isn't a
new insight so much as a predicted one finally getting measured: a
rule-based, phrase-matching safety check is exactly as brittle against a
real model's paraphrasing as the mock-provider ceiling always said it
would be — see docs/evaluation.md's v3.3 section for what a general fix
would need to look like (semantic judgment, not a longer phrase list),
the same conclusion v2.9 reached independently for a completely different
metric.

## The experiment we removed

An earlier version of the hard-case scoring (services/evaluation/scoring.py)
tried to infer overclaiming purely from lexical overlap with evidence,
with no hand-authored rule set. It scored baseline_rag as "safe" on the
patent-credit question because the mock provider happened to copy the "75%"
sentence verbatim — which is true here, but only because the mock provider
is extractive, not because the baseline has any actual safeguard. We
replaced it with the explicit `_HARD_CASE_RULES` check
(forbidden-phrase-without-qualifier) specifically so the metric would still
mean something once a real, paraphrasing LLM is plugged in. See
docs/evaluation.md's "Limitation" section for the honest version of this
story — the mock-provider ceiling this created is still there, just
labeled instead of hidden.

## v4.1 addendum — a search converges on the same limit a human found by hand

The Learning Engine (docs/architecture.md's v4.1 addendum) grid-searched
eleven lexical-evidence-coverage thresholds for when semantic retrieval is
worth its known risk, then validated the promoted one with leave-one-out
cross-validation — the first evaluation in this project that checks a
rule against data withheld while the rule was being chosen. It found
nothing better than v2.4's hand-designed hybrid heuristic: every useful
threshold reaches the identical 0.714 agreement / 0.0 dangerous-overclaim
result, both on the full set and under all 14 held-out folds.

The reason is visible in the per-requirement data: req06, req07, and req14
all have lexical evidence_coverage of 1.0 — full, confident grounding —
and still disagree with the real human assessment. No coverage-based
threshold can ever help these, because the failure isn't "not enough
evidence was retrieved," it's "the retrieved evidence doesn't settle the
question the way its coverage score implies." That is exactly v2.9's
conclusion (lexical relevance scoring isn't the same signal as "which fact
actually settles this question"), reached independently months of
project-versions apart, once by a human reading trajectories by hand and
once by an automated search over a hypothesis space the human never fully
enumerated. Two independent methods hitting the identical wall is stronger
evidence the wall is real than either method alone would be.

A smaller, second finding from the same build: comparing a freshly
computed, full-precision agreement rate against a pre-rounded JSON summary
value (`0.714` vs. the true `10/14 = 0.7142857...`) produced a false "the
learned policy beats hybrid" verdict before it was caught and fixed —
caught by manually checking the specific claim against the raw fraction
before writing it into a doc, not by any test. The general lesson: a value
rounded for human-readable display is not safe to reuse in a numeric
comparison, even when the rounding looks negligible. See
docs/improvement_changelog.md's v4.1 entry for the full story.
