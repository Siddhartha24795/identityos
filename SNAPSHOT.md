# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.2**, taken from the live
working directory at `../identityos/` once clause-level negation detection
was complete and independently verified from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one known dangerous overclaim) is frozen at `../identityos-v2/`.
- v2.1 (general corpus completion, dangerous overclaim resolved) is frozen at `../identityos-v2.1/`.
- v2.2 adds: clause-level negation detection, fixing req13 (a claim mixing
  a positive and negative clause was scored fully negative). Verified not
  to change any of the other 13 requirements' scores. See
  `docs/improvement_changelog.md` (Iteration 7), `docs/evaluation_v2.md`.
- One known, documented, safe-direction (non-dangerous) limitation remains
  open: req05/req10 retrieve zero facts despite real relevant evidence
  existing, because lexical retrieval can't match abstract requirement
  phrasing to differently-worded evidence. Scoped as its own next version,
  v2.3 (embedding-based retrieval) — not patched with a keyword hack.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — this snapshot is
  reproducible standalone via `make setup` from a clean environment.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
