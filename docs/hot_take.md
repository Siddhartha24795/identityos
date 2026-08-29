# Hot take

**Confidence that measures "is this evidence true" is not the same signal
as confidence that measures "is this evidence a good answer to this
question" — and conflating them silently disables your refusal policy.**

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

## What we'd build differently next (and will, in v2)

Confidence needs to be a product of two independently-estimated terms:
`P(evidence is true) x P(evidence actually answers this question)`. The
first is what v1 already measures well (grounding). The second requires
either an explicit relevance-scoring step between retrieval and generation,
or a verifier that checks the *question* against the *claim*, not just the
claim against its source. Neither existed in v1 because the original
design brief's verification-dimension list (docs/architecture.md) doesn't
name this distinction either — we found it by running the eval, not by
reading the spec more carefully.

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
