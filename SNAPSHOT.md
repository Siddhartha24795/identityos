# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.1**, taken from the live
working directory at `../identityos/` once the general corpus-completion
pass was complete and independently verified from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one known dangerous overclaim still
  open) is frozen separately at `../identityos-v2/`.
- v2.1 adds: a general (not case-targeted) completion of the identity
  source corpus, which resolved the one remaining dangerous overclaim
  (req08) as a side effect rather than a targeted patch. See
  `docs/improvement_changelog.md` (Iteration 6), `docs/evaluation_v2.md`,
  and `docs/hot_take.md`.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — this snapshot is
  reproducible standalone via `make setup` from a clean environment.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
