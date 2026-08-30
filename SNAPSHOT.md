# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.6**, taken from the live
working directory at `../identityos/` once the corpus authoring correction
was made and independently verified across all three eval suites from a
clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 (embedding retrieval, evaluated, not promoted) at `../identityos-v2.3/`.
- v2.4 (hybrid retrieval, promoted) at `../identityos-v2.4/`.
- v2.5 (document generation, found the evidence-scope substitution) at `../identityos-v2.5/`.
- v2.6 traced v2.5's residual finding to an actual authoring error — five
  bullets in `dossier_narrative.md` conflated a general statement with an
  IITACB-specific comparison in one sentence, violating this project's own
  one-fact-per-line rule — and fixed all five, not just the one that had
  been visibly wrong. Verified effect: hybrid retrieval's agreement rate
  0.50 -> 0.57 with dangerous overclaim rate held at 0.00 through a real
  corpus change (req05 now a full exact match); semantic-only got *more*
  unstable (0.25 -> 0.50 dangerous overclaim rate, different requirements),
  reinforcing why it was never promoted. Also found — and left open for
  v2.7 — a near-identical conflation in a different source file. See
  `docs/improvement_changelog.md` (Iteration 10-11), `docs/evaluation_v2.md`,
  `docs/evaluation_documents.md`, `docs/hot_take.md`'s v2.6 addendum.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` / `make eval-documents`
  additionally download the embedding model on first run (~65MB, one time).

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
