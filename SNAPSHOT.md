# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.5**, taken from the live
working directory at `../identityos/` once document generation was built,
evaluated, and independently verified from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 (embedding retrieval, evaluated, not promoted) at `../identityos-v2.3/`.
- v2.4 (hybrid retrieval, promoted) at `../identityos-v2.4/`.
- v2.5 adds `services/document_engine/`: the first real generated artifact,
  a 4-section cover letter with narrative-state evidence tracking. Found a
  genuinely new failure mode by reading the actual letter (grounded, true
  evidence can still be out of scope — strategy narrative for a specific
  prior application, cited as if general). Fixed the whole-fact case
  (`FactCategory.APPLICATION_SPECIFIC`); found and left open a subtler
  sentence-level version of the same issue, named rather than patched
  reactively. See `docs/improvement_changelog.md`, `docs/evaluation_documents.md`,
  `docs/hot_take.md`'s v2.5 addendum.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` / `make eval-documents`
  additionally download the embedding model on first run (~65MB, one time).

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
