# Evaluation — v2.5-v2.6 (Document Generation)

## What this is

The original design brief's "Document Generation" component, scoped to one
document type: a generic cover letter, generated section by section
(opening, technical depth, leadership, closing —
`services/document_engine/sections.py`), each section independently
verified with the same verifier as v1/v2. This is the first component that
produces an actual multi-paragraph artifact rather than a short answer or
a single label, so it's the first real test of the original brief's
`APPLICATION_NARRATIVE_STATE` concept: does the system repeat the same two
facts in every paragraph, or does it spread its evidence out like a person
would?

Reproduce: `python scripts/build_digital_self.py && python scripts/run_eval_documents.py mock docs_mock fastembed`.
Generated letters are saved as plain text at `data/evaluation/results/<tag>/documents/<system>.md` — read them, not just the scores.

## Result (post-v2.6)

| Metric | baseline_plain | baseline_rag | identityos_v2_5 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.95** |
| Unsupported claim rate | 1.00 | 1.00 | **0.05** |
| Repeated-evidence rate (narrative diversity) | n/a (no citations) | n/a | **0.44** |

Same structural story as v1/v2: neither baseline has a citation mechanism,
so neither can be scored above the trivial floor regardless of prose
quality. identityos_v2_5 grounds 95% of its sentences. Repeated-evidence
rate rose from 0.32 (v2.5) to 0.44 here because the v2.6 corpus split
below reduced the pool of distinct general facts available to some
sections — a real, disclosed side effect, not hidden because the other two
numbers didn't move.

## v2.5: a real finding, from reading the actual letter, not just the score

The first version of the generated letter read like it was applying **for
the IITACB CEO role specifically** — "the Secretariat," "the committee,"
"CoE co-investment" — despite the system prompt explicitly asking for a
generic technology-leadership letter. Every cited sentence was real, true,
and correctly grounded. The problem was invisible to every metric already
built. **Grounded and true is not the same as "the right evidence for this
document."** Root cause: `dossier_narrative.md`'s "STRATEGY AND
ACCOUNTABILITY" section is explicitly IITACB-proposal content — real
evidence, scoped to one specific candidacy, not general capability
evidence about the person.

**v2.5's fix** (`FactCategory.APPLICATION_SPECIFIC`, tagged at ingestion,
excluded by the generic-letter generator) caught that whole section. It
did not catch a subtler version of the same problem: role-specific framing
baked into individual sentences *inside* otherwise-general facts (e.g.
"...precisely the condition of a Secretariat being stood up," attached to
an otherwise general statement about comfort with ambiguity).

## v2.6: the fix was an authoring correction, not a smarter classifier

Root-caused the sentence-level leak to an actual authoring error: five
bullets in `dossier_narrative.md`'s "REQUIREMENT EVIDENCE" section violated
this project's own one-fact-per-line ingestion rule, conflating a general
statement with an IITACB-specific comparison in the same sentence. Split
each into a general fact and a separate, correctly-tagged
`APPLICATION_SPECIFIC` fact — a one-time authoring correction applying an
existing rule correctly, not a new classification mechanism, and affecting
five bullets even though only one had been the visible symptom.

**Verified effect, not just on the letter:** re-running all three eval
suites showed req05 (previously stuck at a `partial` match under hybrid
retrieval) became a full, exact `met_or_better` match once the general
capability statement was no longer diluted by the ambiguous role
comparison — hybrid retrieval's agreement rate rose from 0.50 to 0.57 with
zero change to its dangerous-overclaim rate (still 0.00). Full numbers:
docs/evaluation_v2.md's v2.6 section.

**The regenerated letter no longer contains the "Secretariat" comparison.**
Re-reading it surfaced a *different*, distinct instance of the same
authoring pattern in a different source file
(`dossier_excerpts.md`'s "SELF-ASSESSED GAP" section mixes a general
capability-gap admission with "...the committee should not be persuaded
that adjacent experience... is equivalent to that record" — "the
committee" is IITACB's Managing Committee). Named as the next item
(docs/roadmap.md v2.7), not expanded into this version. This is the same
granularity lesson as v2.2's negation fix, now confirmed a third time: the
right fix at this level of the codebase has consistently been "read the
actual output and correct the source," not "build a cleverer filter."

## What this run does and doesn't prove

Same mock-provider caveat as v1/v2: extractive generation preserves source
wording (which is why the contamination was visible and traceable at all,
and why the fix is verifiable by literally reading the diff) rather than
paraphrasing it away. A real LLM run would likely produce more natural
prose while needing the exact same source-correction discipline to avoid
the same leak in different words.
