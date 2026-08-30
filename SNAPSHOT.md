# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v3.2**, taken from the
live working directory at `../identityos/` once a centralized Security
Policy Engine and independent Agent Auditor were built, tested, and used
to run a combined attack demonstration with real, recorded evidence —
verified from a clean environment that all of it reproduces.

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
- v3.0 (browser automation: Playwright agent, human-approval gate, two
  real bugs found and fixed — a select-field verification mismatch and a
  systemic MockProvider prompt-parsing bug dating to v2.0) at `../identityos-v3.0/`.
- **v3.1** (built in the same working session as v3.2, not separately
  snapshotted) added four heuristic guardrails scattered across
  `controller.py`/`field_mapper.py`: CAPTCHA/anti-bot/MFA detection
  (page-level halt), prompt-injection detection on field labels, a
  zero-evidence refusal for genuinely unanswerable fields, and
  hidden/honeypot field skipping.
- **v3.2** centralizes those checks — built in direct response to a much
  larger "Security, Safety, Identity Integrity, and Autonomy Guardrail
  Specification" the project owner provided in full, preserved verbatim
  at `docs/security_spec.md`:
  - `SecurityPolicyEngine` (`services/security/policy_engine.py`) — every
    proposed browser action passes through `evaluate()` regardless of
    what `field_mapper.py` decided, independently classified into five
    risk levels with configurable per-level confidence floors;
    `evaluate_page()` and `evaluate_submit()` centralize the page-level
    and submit-time gates the same way. Submission is blocked if the
    run's audit trail has any unresolved BLOCK/ESCALATE finding, even
    with `approve_submit=True`.
  - `AgentAuditor` (`services/security/auditor.py`) — a second,
    genuinely independent check: cited evidence ids must actually exist
    in the Digital Self (catches a fabricated citation), and generated
    text must not leak the field's own label verbatim (the v3.0
    MockProvider bug's exact shape, generalized into a permanent check).
  - An append-only audit log (`services/security/audit_log.py`,
    `data/evaluation/results/<tag>/security_audit.jsonl`) with a schema
    that has no field that could hold a secret, by construction.
  - A combined attack demonstration
    (`data/applications/local_demo/adversarial_mixed.html`,
    `scripts/run_security_demo.py`, `make eval-security-demo`) per the
    spec's own requirement to visibly demonstrate detect/explain/
    block-or-escalate/continue in one pass: two legitimate fields filled
    and verified alongside a prompt-injection attempt, an
    identity-verification question, and an off-topic decoy, all three
    halted with an explained rationale, run completing without
    submitting. Real recorded output — see
    `data/evaluation/results/security_demo/security_demo_report.json`.
  - `ApplicationRecord` (`packages/schemas/application_record.py`,
    `services/application_record/`) — a direct, separate request: every
    filled application's questions and answers (with evidence and
    confidence) are saved automatically to `data/applications/history/`
    as both JSON and a human-readable Markdown crib sheet, so a person
    can check what they actually told a specific employer before an
    interview.

  A real bug was found while building the combined-attack demo: the
  first version of the page-level anti-bot check scanned the entire
  visible page body (not just the title), which includes every field's
  own label — so a single field asking "Are you a robot?" among several
  legitimate ones incorrectly halted the *whole task* instead of just
  that field. Fixed by scanning only the page title for page-level
  signals, letting the already-correctly-scoped per-field checks handle
  one suspicious field among several. Caught only by building the
  adversarial fixture and reading what actually happened — the same
  discipline behind every other finding in this project, now applied to
  a security feature.

  **Deliberately not built, and why** (docs/roadmap.md's v3.2 section has
  the complete, itemized list): identity-provenance temporal validation,
  cross-application consistency/deduplication, self-improvement CI and
  anti-promotion, domain/phishing validation, real credential/OTP-channel
  isolation, rollback, and the full 25-item security test suite the spec
  names. Each requires a capability — versioned belief history, a
  multi-application store, a persistent learning loop, real
  authenticated multi-domain browsing, real credential handling — that
  doesn't exist anywhere else in this codebase yet. Building any of it
  now would be untested scaffolding with nothing real to gate; each is
  named explicitly as deferred rather than silently dropped or built
  half-tested.

  See `docs/evaluation_browser.md`'s v3.1 and v3.2 addenda,
  `docs/hackathon_compliance_check.md`'s ground rule 3 section,
  `docs/improvement_changelog.md` (Iteration 18-26), and
  `docs/security_spec.md` (the full spec, verbatim).

- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, or cache directories were copied — `make setup`
  installs Playwright's Chromium binary (~300MB, one time) in addition to
  everything prior versions needed. `make eval-mock` / `make eval-v2-mock`
  need nothing beyond this folder and network access; `make
  eval-v2-semantic` / `make eval-documents` / `make eval-browser` / `make
  eval-security-demo` additionally download the fastembed embedding model
  on first run (~65MB, one time).

## Independent clean-environment verification (this snapshot)

Ran from scratch, inside this frozen folder, in a throwaway venv:

```
make setup && make test && make eval-mock && make eval-v2-mock \
  && make eval-v2-semantic && make eval-documents && make eval-browser \
  && make eval-security-demo
```

All 56 tests passed. Every eval number reproduced byte-identical to the
live directory's numbers documented in `docs/evaluation.md`,
`docs/evaluation_v2.md`, `docs/evaluation_documents.md`, and
`docs/evaluation_browser.md` — including `identityos_v2_semantic`'s
dangerous_overclaim_rate of 0.75, `identityos_v2_5`'s
repeated_evidence_rate of 0.412 (both a disclosed effect of v3.0's
MockProvider fix), and the v3.0/v3.1 browser reference numbers
(`n_fields: 6, n_filled: 6, n_verified: 6, avg_evidence_coverage: 1.0,
avg_confidence: 0.934`), unchanged by v3.2's security-layer refactor.
`make eval-security-demo`'s real output (both legitimate fields filled
and verified, all three attacks halted with an explained rationale, run
completing without submitting) reproduced identically as well. The
verification venv and embedding cache were then removed from this
folder — it is not required for the snapshot to be reproducible, only
for the reproduction to have actually been checked once, which it was.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
