# Demo script (target: under 5 minutes)

v1 has no browser/UI yet (docs/roadmap.md v3/v5), so the demo is a
terminal walkthrough — every number shown is read live from a generated
file, not slides.

1. **Problem (30s).** State the bottleneck from docs/problem_statement.md:
   applications ask factual questions (easy), never-before-answered
   questions (no source sentence exists), and adversarial-shaped questions
   that invite overclaiming. Show `data/evaluation/question_bank.json` and
   point at q13 (patent credit — a real 75%/25% shared inventorship).

2. **Baseline (45s).** Run
   `python scripts/run_eval.py mock demo_baseline_check` isn't needed live —
   instead open `data/evaluation/results/v1_mock/trajectories/q13__baseline_plain.md`
   and `q13__baseline_rag.md` side by side. Read the plain baseline's
   generic non-answer aloud, then the RAG baseline's answer that happens to
   include the right numbers but with zero mechanism forcing it to.

3. **One realistic execution, start to finish (2 min).** Live-run:
   ```
   python scripts/build_digital_self.py
   python scripts/run_eval.py mock live_demo
   ```
   While it runs (seconds), narrate the pipeline stages from
   docs/architecture.md. When it finishes, open
   `data/evaluation/results/live_demo/trajectories/q13__identityos_v1.md`
   and read the five logged stages (classify -> retrieve -> generate ->
   verify -> complete) end to end, pointing at the inline `[dossier_excerpts:002]`
   citation and the "75%" qualifier surviving into the final answer.

4. **Final comparison (45s).** Show the summary table from
   docs/evaluation.md: Identity Fidelity Score 0.95 vs 0.20, evidence
   coverage 0.93 vs 0.00.

5. **Changelog highlight + removed experiment (45s).** From
   docs/improvement_changelog.md: the single biggest driver was Iteration 2
   (citation-forcing), not better prompting or a bigger model. The removed
   experiment: the first hard-case scoring rule was fooled by the mock
   provider's extractive behavior — call this out explicitly as the kind of
   mistake worth showing, not hiding.

6. **Hot take (15s).** One line from docs/hot_take.md: confidence that
   measures "is this true" is not confidence that measures "does this
   answer the question" — refusal never fired even on the hardest
   questions, because v1 only checks the former.
