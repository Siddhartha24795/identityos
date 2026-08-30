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
