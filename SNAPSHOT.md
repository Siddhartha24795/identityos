# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.7**, taken from the live
working directory at `../identityos/` once the second corpus authoring
correction was made and independently verified across all three eval
suites from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 (embedding retrieval, evaluated, not promoted) at `../identityos-v2.3/`.
- v2.4 (hybrid retrieval, promoted) at `../identityos-v2.4/`.
- v2.5 (document generation, found the evidence-scope substitution) at `../identityos-v2.5/`.
- v2.6 (corpus authoring correction, `dossier_narrative.md`) at `../identityos-v2.6/`.
- v2.7 applies the identical correction to the second file where the same
  conflation pattern was found (`dossier_excerpts.md`'s "SELF-ASSESSED
  GAP" section: a general capability-gap fact mixed with "the committee
  should not be persuaded..." [IITACB's Managing Committee], and a general
  language-fluency fact mixed with a relocation commitment made
  specifically for the IITACB role). Result: hybrid retrieval's agreement
  rate 0.57 -> 0.71 (req03 and req06 now exact matches), dangerous
  overclaim rate held at 0.00 through a *second* consecutive real corpus
  change. Generated cover letter re-verified clean of every
  application-specific phrase flagged across both correction rounds. See
  `docs/improvement_changelog.md` (Iteration 12), `docs/evaluation_v2.md`,
  `docs/evaluation_documents.md`, `docs/hot_take.md`'s v2.7 addendum.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` / `make eval-documents`
  additionally download the embedding model on first run (~65MB, one time).

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
