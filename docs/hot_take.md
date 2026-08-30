# Hot take

**Grounding metrics only check whether a claim traces to evidence — not
what the claim actually says. Confidence that measures "is this evidence
true" gets silently reused as a stand-in for "is this a good answer" and
for "is this a positive answer," and neither substitution is safe.**

v1 found the first substitution (relevance). v2 found the second
(polarity), independently, by running the same verification machinery
against a real, adjudicated application. Both read as the same underlying
mistake once you see them side by side.

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
eval question needed what, and req08 resolved as a side effect. Two safe
(non-dangerous) failures remain — a sentence-level negation check that
should be clause-level, and a lexical retriever that can't match
"entrepreneurial mindset" against evidence phrased as "comfortable with
ambiguity" — both documented in docs/evaluation_v2.md, neither patched away.

The pattern across both versions: **grounding verification answers "did
this really come from evidence," and every time we've needed it to also
answer "does this evidence mean what the sentence around it implies," it
has silently failed to, in a different way each time.** That looks like a
property of grounding-based verification in general, not a bug specific to
either version — and the more durable fix, twice now, has been making the
underlying representation more complete rather than making the checking
logic cleverer.

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
