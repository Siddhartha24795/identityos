# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.4**, taken from the live
working directory at `../identityos/` once hybrid retrieval was built,
evaluated, and independently verified from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 (embedding retrieval, evaluated, not promoted) at `../identityos-v2.3/`.
- v2.4 adds `identityos_v2_hybrid`: lexical retrieval first, semantic
  fallback only when lexical finds nothing. Directly diagnosed from v2.3's
  regression (noise only appeared when semantic overrode a working lexical
  answer, never when filling a real gap). Result: agreement rate 0.50
  (best of all five systems), dangerous overclaim rate 0.00 (matches
  lexical) — verified requirement-by-requirement, not assumed: all 12
  requirements lexical could already answer are byte-identical to pure
  lexical output. **Hybrid is now the recommended retrieval strategy**,
  kept alongside lexical-only and semantic-only as permanent comparison
  arms. See `docs/improvement_changelog.md` (Iteration 9),
  `docs/evaluation_v2.md`, `docs/hot_take.md`.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` additionally downloads the
  embedding model on first run (~65MB, one time) and now also computes the
  hybrid arm.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
