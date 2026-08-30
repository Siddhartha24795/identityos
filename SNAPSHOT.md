# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v3.0**, taken from the
live working directory at `../identityos/` once the browser-automation
agent was built, two real bugs found by reading its own trajectory output
were fixed at the root, and every earlier eval suite was re-run to confirm
what did and didn't change — verified from a clean environment that all
of it reproduces.

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
- v2.9 (relevance-weighted polarity, tried two ways, both rejected) at `../identityos-v2.9/`.
- **v3.0** adds a real Playwright browser agent (`services/browser_engine/`)
  that opens a local, offline, synthetic application form
  (`data/applications/local_demo/`), detects all four field types the
  original brief names (text, textarea, select, checkbox) via generalized
  DOM inspection, maps each to Digital Self data (reusing v1/v2's hybrid
  retrieval + generation + verification unmodified for free-text fields),
  fills it, re-observes the live DOM to verify each value actually
  stuck, decides the accuracy-confirmation checkbox from aggregate
  confidence + verification, and **halts for human approval before any
  submit** — there is no code path where the agent can decide on its own
  to submit (ground rule 4, implemented literally). Reference run:
  `n_fields: 6, n_filled: 6, n_verified: 6, avg_evidence_coverage: 1.0,
  avg_confidence: 0.934, halted_for_approval: true, submitted: false`.

  The first run only verified 4/6 fields. Reading the actual trajectory
  output — not just trusting the score — found two real bugs:
  1. `BrowserController.observe()` compared a `<select>` field's
     underlying option `value` attribute against the visible label text
     used everywhere else for fill/compare. Fixed by reading the selected
     option's own `inner_text()` instead.
  2. A systemic bug in `services/providers/mock_provider.py`, present
     since v2.0 but never caught: its prompt parser hardcoded v1's exact
     `"QUESTION:"` header, so v2's `"REQUIREMENT:"` and v2.5's
     `"SECTION PROMPT:"` prompts (and v3's own `"FIELD LABEL:"`) silently
     fell through to a fallback that could leak the label text itself
     into a generated answer when retrieval was already weak. Fixed at
     the root, in `mock_provider.py` only, with a general parser that
     doesn't require a specific keyword.

  Every earlier eval suite was re-run after both fixes, not assumed
  side-effect-free: v1, `identityos_v2` (lexical), and
  `identityos_v2_hybrid` were completely unaffected.
  `identityos_v2_semantic`'s dangerous-overclaim rate — already the worst
  of the three retrieval arms and never the shipped default — got
  honestly worse (0.50 -> 0.75), because the bug had been partially
  masking an existing weakness rather than causing a new one. Added 7
  regression tests (`tests/test_browser_engine.py`), including one
  end-to-end test that launches real Chromium and would fail again if
  either bug regressed. See `docs/evaluation_browser.md`,
  `docs/evaluation_v2.md`'s v3 addendum, `docs/evaluation_documents.md`'s
  v3 addendum, `docs/hot_take.md`'s v3 addendum, and
  `docs/improvement_changelog.md` (Iteration 16-17).

- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup`
  installs Playwright's Chromium binary (~300MB, one time) in addition to
  everything prior versions needed. `make eval-mock` / `make eval-v2-mock`
  need nothing beyond this folder and network access; `make
  eval-v2-semantic` / `make eval-documents` / `make eval-browser`
  additionally download the fastembed embedding model on first run
  (~65MB, one time).

## Independent clean-environment verification (this snapshot)

Ran from scratch, inside this frozen folder, in a throwaway venv:

```
make setup && make test && make eval-mock && make eval-v2-mock \
  && make eval-v2-semantic && make eval-documents && make eval-browser
```

All 33 tests passed. Every eval number reproduced byte-identical to the
live directory's numbers documented in `docs/evaluation.md`,
`docs/evaluation_v2.md`, `docs/evaluation_documents.md`, and
`docs/evaluation_browser.md` — including `identityos_v2_semantic`'s
dangerous_overclaim_rate of 0.75 and `identityos_v2_5`'s
repeated_evidence_rate of 0.412, both of which moved from their
previously-documented values as a direct, disclosed effect of the
MockProvider fix above. The verification venv and embedding cache were
then removed from this folder — it is not required for the snapshot to be
reproducible, only for the reproduction to have actually been checked
once, which it was.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
