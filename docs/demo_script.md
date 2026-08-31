> **A produced solution video now exists**: `docs/media/solution_video.mp4`
> (4:27, well under the 5-minute cap). It covers a different slice than the
> script below — problem, the real fabricated baseline output from v3.3's
> real-model run, Digital Self ingestion, Q&A with citation+verification,
> the actual v3 browser agent filling a real form (real Playwright
> screenshots, not mockups) through to the human-approval halt, the final
> comparison table, changelog highlights (the citation-forcing jump), one
> rejected experiment (v2.8), and the hot take — rather than this script's
> v1/v2/v2.5 terminal walkthrough. Both are kept: this script remains the
> plan for a live, presenter-narrated walkthrough if one is ever recorded;
> the produced video is narrated (synthesized speech, captioned) and can be
> watched standalone. See docs/hackathon_compliance_check.md for how each
> claim in the video traces back to a real, checked artifact in this repo.

# Demo script (target: under 5 minutes, hard cap per hackathon rules)

v1/v2 have no browser/UI yet (docs/roadmap.md v3/v5), so the demo is a
terminal walkthrough — every number shown is read live from a generated
file, not slides. Timings are budgets, not scripts — cut narration, not
the on-screen evidence.

1. **Problem (25s).** State the bottleneck from docs/problem_statement.md:
   applications ask factual questions (easy), never-before-answered
   questions (no source sentence exists), and adversarial-shaped questions
   that invite overclaiming. Show `data/evaluation/question_bank.json`
   pointing at q13 (patent credit — a real 75%/25% shared inventorship).

2. **Baseline vs. system, live (45s).** Run
   `python scripts/build_digital_self.py && python scripts/run_eval.py mock live_demo`.
   While it runs, narrate the pipeline (docs/architecture.md). Open
   `data/evaluation/results/live_demo/trajectories/q13__baseline_rag.md`
   next to `q13__identityos_v1.md` — same question, same evidence
   available, only one of them cites and verifies it.

3. **v1 result (20s).** Show the comparison table from README: Identity
   Fidelity Score 0.96 vs 0.20, evidence coverage 0.95 vs 0.00.

4. **v2: a real application, real ground truth (45s).** State the
   extension: 14 real requirements from an actual job description, scored
   against the person's own real, pre-existing self-assessment — not
   something written for this benchmark. Run
   `python scripts/run_eval_v2.py mock v2_demo` and open
   `data/evaluation/results/v2_demo/trajectories/req14__identityos_v2.md` —
   the single most important requirement, a real admitted governance gap.

5. **The bug, found and fixed (35s).** Show that the system correctly
   retrieved and cited the exact sentence admitting the gap — and initially
   still mislabeled it a match, because grounding and polarity got
   conflated (docs/hot_take.md). State plainly: the fix that actually
   closed the remaining dangerous case (req08) wasn't a smarter rule, it
   was completing the identity corpus with the rest of the real source
   document (v2.1) — resolved as a side effect, not a targeted patch.

6. **The experiment we tried, didn't ship, then fixed properly (50s).**
   State the v2.3 finding directly: embedding-based retrieval (real
   semantic search, no API key, ~65MB local model) genuinely fixed two weak
   spots — and reintroduced a dangerous overclaim elsewhere, because
   higher-recall retrieval fed a noisier signal into the same polarity
   check. We measured it, it wasn't a net win, so it didn't ship. Then:
   diagnosing *why* — the noise only ever overrode a working lexical
   answer, never filled a real gap — led to v2.4's fix: semantic only as a
   fallback when lexical finds nothing. Show the final table: agreement
   rate 0.50, dangerous overclaim rate 0.00 — best of all five systems,
   verified requirement-by-requirement, not assumed.

7. **The first real artifact, and the finding hiding inside it (35s).**
   Run `make eval-documents` and open the generated letter at
   `data/evaluation/results/docs_mock/documents/identityos_v2_5.md`. State
   plainly: it initially read like an application for one specific prior
   role, because real, grounded evidence turned out to be strategy
   narrative written for a different, specific context — not general
   evidence about the person. Fixed the obvious case; name the subtler one
   that's still open (sentence-level framing) rather than claim it's clean.

8. **Close (15s).** One sentence: the same mistake surfaced repeatedly in
   different disguises — grounding tells you a claim is real, not what it
   means, how solid the retrieval behind it was, or whether it's in scope
   — and every time, correctly diagnosing the mechanism beat trusting that
   "smarter" automatically means "better."

Total: ~4:45, leaving minimal headroom — trim narration, not evidence, if recording runs long.
