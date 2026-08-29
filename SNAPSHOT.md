# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2**, taken from the live
working directory at `../identityos/` once v2 (application-compilation
requirement-fit assessment against a real, adjudicated application) was
complete and independently verified from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- Ongoing development continues in `../identityos/` (the live directory).
- When v2.1/v3 is complete, it will be snapshotted the same way into
  `../identityos-v3/` (or `../identityos-v2.1/`).
- No `.venv`, `.git`, or cache directories were copied — this snapshot is
  reproducible standalone via `make setup` from a clean environment.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
