# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v2.3**, taken from the live
working directory at `../identityos/` once embedding-based retrieval was
built, evaluated, and independently verified from a clean environment.

- v1 (Q&A only) is frozen separately at `../identityos-v1/`.
- v2.0 (requirement-fit assessment, one dangerous overclaim) at `../identityos-v2/`.
- v2.1 (general corpus completion) at `../identityos-v2.1/`.
- v2.2 (clause-level negation) at `../identityos-v2.2/`.
- v2.3 adds `identityos_v2_semantic` — the same pipeline as `identityos_v2`
  with embedding-based retrieval (fastembed, no API key, ~65MB ONNX model)
  instead of lexical. It genuinely fixed two weak spots (req05, req10) —
  and reintroduced a dangerous overclaim elsewhere (req09), because
  higher-recall retrieval fed a noisier signal into v2.2's polarity check.
  **Decision: lexical retrieval stays the shipped default**; the semantic
  arm is kept running as an honest comparison, not deleted, not promoted.
  See `docs/improvement_changelog.md` (Iteration 8), `docs/evaluation_v2.md`,
  `docs/hot_take.md`.
- Also fixed in this pass: a real bug in `services/identity_engine/ingest.py`
  where a hyphenated section header (`## SELF-ASSESSED GAP`) failed to match
  the header regex and leaked into the fact corpus as literal text —
  predates v2.3, found while calibrating embedding similarity scores.
- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup` +
  `make eval-mock` / `make eval-v2-mock` need nothing beyond this folder
  and network access. `make eval-v2-semantic` additionally downloads the
  embedding model on first run (~65MB, one time).

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
