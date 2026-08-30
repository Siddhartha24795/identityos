# Evaluation — v2.5 (Document Generation)

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

## Result

| Metric | baseline_plain | baseline_rag | identityos_v2_5 |
|---|---|---|---|
| Evidence coverage | 0.00 | 0.00 | **0.95** |
| Unsupported claim rate | 1.00 | 1.00 | **0.05** |
| Repeated-evidence rate (narrative diversity) | n/a (no citations) | n/a | **0.32** |

Same structural story as v1/v2: neither baseline has a citation mechanism,
so neither can be scored above the trivial floor regardless of prose
quality. identityos_v2_5 grounds 95% of its sentences and reuses the same
piece of evidence across sections only 32% of the time — real narrative
spread, not four paragraphs built from the same two facts, achieved by
`_prefer_unused()` deprioritizing (not forbidding) evidence already cited
in an earlier section (`services/document_engine/generate.py`).

## A real finding, from reading the actual letter, not just the score

The first version of the generated letter read like it was applying **for
the IITACB CEO role specifically** — "the Secretariat," "the committee,"
"CoE co-investment" — despite the system prompt explicitly asking for a
generic technology-leadership letter. Every cited sentence was real,
true, and correctly grounded. The problem was invisible to every metric
already built: high evidence coverage, low unsupported-claim rate, correct
citations. **Grounded and true is not the same as "the right evidence for
this document."** A fact can correctly describe the person and still be
strategy narrative written for a different, specific prior application.

Root cause: `data/identity_sources/dossier_narrative.md`'s "STRATEGY AND
ACCOUNTABILITY" section is explicitly IITACB-proposal content (see
docs/roadmap.md v2.1's own corpus-completion notes) — real evidence, but
scoped to one specific candidacy, not general capability evidence about
the person.

## The fix, and what it did and didn't solve

Added `FactCategory.APPLICATION_SPECIFIC` (`packages/schemas/identity.py`)
and tagged that one section at ingestion
(`services/identity_engine/ingest.py`); the generic-letter generator now
excludes it (`_exclude_application_specific()`). Verified: 7 facts are
tagged and correctly excluded, and v1/v2's own eval numbers are provably
unaffected (category never affected their scoring) — re-run and confirmed
byte-identical before and after this change.

**This did not fully solve the problem.** The regenerated letter still
contains phrases like "precisely the condition of a Secretariat being
stood up" and "he would apply the same discipline to any institution he
leads" — IITACB-referential framing baked into individual sentences inside
facts that are otherwise general, correctly-categorized capability
evidence (from the "REQUIREMENT EVIDENCE" section, transcribed in v2.1 by
paraphrasing a table whose own framing compared everything to the IITACB
role). Category-level filtering operates on whole facts; the contamination
here is at the sentence level, inside facts that are mostly general.

This is the same granularity lesson as v2.2's negation fix, showing up a
third time at a different level: v2.2 needed clause-level splitting where
sentence-level was too coarse; this needs sentence- or clause-level
*content-scope* classification where fact-level categorization is too
coarse. Deferred to v2.6+ (docs/roadmap.md) — the honest options are
either rewriting the source facts to strip application-specific framing
(a real corpus-quality fix) or LLM-assisted neutral rephrasing at
generation time (needs a real provider key). Not attempted here because
both need their own evaluation, and re-editing source facts specifically
because one eval run looked bad is exactly the reactive-patching pattern
this project has repeatedly declined elsewhere.

## What this run does and doesn't prove

Same mock-provider caveat as v1/v2: extractive generation preserves source
wording (which is why the contamination is visible and traceable at all)
rather than paraphrasing it away, for better and worse. A real LLM run
would likely produce more natural prose while needing the exact same
category-scoping fix to avoid the same leak in different words.
