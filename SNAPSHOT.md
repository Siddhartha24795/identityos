# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.8**, taken from the live
working directory at `../identityos/` once a retrieval-precision experiment
was diagnosed, tested against the full benchmark, and correctly rejected —
verified from a clean environment that the shipped behavior is unchanged.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 (embedding retrieval, evaluated, not promoted) at `../identityos-v2.3/`.
- v2.4 (hybrid retrieval, promoted) at `../identityos-v2.4/`.
- v2.5 (document generation, found the evidence-scope substitution) at `../identityos-v2.5/`.
- v2.6 (corpus authoring correction, `dossier_narrative.md`) at `../identityos-v2.6/`.
- v2.7 (corpus authoring correction, `dossier_excerpts.md`) at `../identityos-v2.7/`.
- v2.8 diagnosed why req07 and req12 still mismatched (a fact sharing one
  token with the requirement can inject an unrelated negation marker),
  added an optional `min_shared_tokens` parameter to
  `retrieve()`/`retrieve_hybrid()` (default unchanged at 1), and tested
  raising it to 2 against the full 14-requirement benchmark. It fixed
  req07/req12 and turned req08/req09 into dangerous overclaims — the same
  weak matches were noise for one pair and load-bearing correct evidence
  for the other. **Not adopted**; shipped retrieval behavior is
  byte-identical to v2.7. See `docs/improvement_changelog.md`
  (Iteration 13), `docs/evaluation_v2.md`, `docs/hot_take.md`'s v2.8
  addendum.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` / `make eval-documents`
  additionally download the embedding model on first run (~65MB, one time).

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
