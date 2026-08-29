# Problem statement

## Who has this problem?

Anyone who repeatedly applies for opportunities that ask about *them*
specifically: job seekers, PhD/fellowship applicants, grant applicants,
accelerator founders. Concretely, the author of this project: over the same
week as this build, producing one cover letter and one CEO-candidacy dossier
required manually re-reading a resume and an old dossier, re-finding the
same facts, and re-deciding how confidently to state a jointly-held patent
(75% contribution) or an admitted gap (no professional-body governance
experience). That reconstruction is the exact bottleneck this project
targets — and it's why the identity source documents in this repo are the
author's own real resume and dossier, not synthetic filler.

## What bottleneck makes it worth solving?

Every application asks a mix of:
1. **Factual questions** answerable by looking something up (easy, low risk).
2. **Never-before-answered questions** ("what failure taught you the most?")
   that have no source sentence to retrieve — answering them requires
   *reasoning about the person*, not search.
3. **Adversarial-shaped questions** that invite overclaiming (patent credit,
   governance experience, language fluency) where the honest answer is
   qualified or negative, and a generic assistant's instinct to sound
   confident is actively harmful.

A plain LLM call answers all three the same way: confidently, generically,
and without provenance. A copy-paste RAG-over-resume approach fixes some of
(1) but still has no mechanism to *know that it doesn't know* on (2) and (3).
Nobody currently has a way to tell, before submitting, whether a generated
answer is grounded, is a reasonable inference, or is invented.

## Does the agent solve it well?

IdentityOS v1 doesn't answer everything — it answers with **calibrated,
citable confidence**, and refuses rather than fabricates when it can't.
Every claim in every generated answer traces to a specific source line or is
flagged unsupported. See docs/evaluation.md for the measured comparison
against a fair baseline on the same 19 questions, including the four hard
cases the hackathon brief specifically calls for.

## Can another person reproduce the result?

Yes, with zero API keys: the mock provider makes the full pipeline —
ingestion, retrieval, generation, verification, scoring, trajectory logging —
runnable end to end offline. See the root README's Quickstart and
docs/evaluation.md for exact commands and what each produces.
