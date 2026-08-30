# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.9**, taken from the live
working directory at `../identityos/` once a second retrieval-precision
experiment was implemented, tested against the full benchmark, and
correctly rejected — verified from a clean environment that the shipped
behavior is unchanged.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 (embedding retrieval, evaluated, not promoted) at `../identityos-v2.3/`.
- v2.4 (hybrid retrieval, promoted) at `../identityos-v2.4/`.
- v2.5 (document generation, found the evidence-scope substitution) at `../identityos-v2.5/`.
- v2.6 (corpus authoring correction, `dossier_narrative.md`) at `../identityos-v2.6/`.
- v2.7 (corpus authoring correction, `dossier_excerpts.md`) at `../identityos-v2.7/`.
- v2.8 (retrieval-inclusion-bar experiment, rejected) at `../identityos-v2.8/`.
- v2.9 implemented the fix v2.8 pointed to — relevance-weighted polarity
  checking — two ways: IDF-weighted retrieval scoring
  (`build_idf_table()`, `retrieve_idf()`) and a relevance-dominance gate
  on the polarity vote (`bucket_from_signals(..., relevance_scores=...)`).
  Both tested against the full 14-requirement benchmark. IDF reordering
  had no effect (rank isn't inclusion under a generous top-k). The
  dominance gate fixed req12 and turned req14 — the single highest-stakes
  requirement in the benchmark — into a dangerous overclaim. **Not
  adopted; shipped behavior is byte-identical to v2.8.** Conclusion: two
  independent heuristic fixes for req07/req12 have now failed the same
  way — lexical/statistical relevance scoring cannot reliably identify
  which fact actually settles a question. This is a real boundary of the
  lexical-retrieval approach, not a tuning gap; the next real step needs
  semantic judgment (a real LLM call), not a third heuristic. See
  `docs/improvement_changelog.md` (Iteration 14-15), `docs/evaluation_v2.md`,
  `docs/hot_take.md`'s v2.9 addendum.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` / `make eval-documents`
  additionally download the embedding model on first run (~65MB, one time).

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
