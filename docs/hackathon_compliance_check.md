# Hackathon compliance self-check

Re-verified after every version against `/home/siddhartha/siddhartha/micro1 - First Hackathon97ce7c5.pdf`.
Last checked: **post-v4.1** (git history reconstruction, PII redaction,
cross-version reproduction, solution video, Orchestrator, Learning Engine).

**v4.0-v4.1 addition, prompted by re-reading the rubric's tie-break
order** (Agent Solution & Engineering ranked first): the submission's
weakest honest gap against PROMPT.md's fuller vision was "no orchestrator,
no self-improvement loop" (both explicitly named as deferred in
docs/roadmap.md). Built the narrow, defensible version of each rather than
stubbing the full brief: a real 3-way orchestrator (v4.0) and a real,
narrowly-scoped, leave-one-out-validated Learning Engine (v4.1) — see the
Agent Solution & Engineering row below and docs/architecture.md's v4.0/v4.1
addenda for what was and wasn't built, and why.

**Post-v3.3 audit findings, all fixed:**
- The repository had zero git commits despite the README describing 14
  versioned states. Rebuilt as 15 real commits — one per frozen snapshot
  (`../identityos-v1/` through `../identityos-v3.3/`, dated by each
  snapshot's actual filesystem timestamp) plus one final commit for the
  live-directory fixes below — and pushed to
  `github.com/Siddhartha24795/identityos`.
- Cross-version reproduction: `build_digital_self.py` + `run_eval.py` /
  `run_eval_v2.py` re-run inside each frozen snapshot (temporarily sharing
  the live venv, since each snapshot's own requirements are a strict subset).
  Numbers matched the changelog exactly: v2 agreement rate 0.286 -> v2.1
  0.357 -> v2.2 0.429 (documented as 0.29/0.36/0.43), dangerous-overclaim
  0.25 -> 0.0 -> 0.0, v1 IFS stable at 0.947-0.958 as the corpus grew
  75->96 facts. All snapshot directories left unmodified afterward.
- A real personal email was hardcoded in `services/browser_engine/field_mapper.py`
  and had leaked into committed trajectory/history/security-demo artifacts
  — see ground rule 8 below.
- Solution video produced — see Final deliverables #3 below.

## Judging rubric (100 pts)

| Criterion | Pts | Where addressed | Status |
|---|---|---|---|
| Problem & User Value | 15 | docs/problem_statement.md — real bottleneck (this project's own author reconstructing themself across applications), clearly defined user | Addressed |
| Agent Solution & Engineering | 30 | docs/architecture.md — retrieval + citation + verification + confidence-gated refusal (v1); reused pipeline + polarity-aware bucketing + three evaluated retrieval strategies (v2); section-planned document generation with narrative-state tracking (v2.5); two root-caused corpus authoring corrections (v2.6-v2.7); two independent retrieval-precision experiments, each tested against the full benchmark and correctly rejected rather than shipped on partial evidence (v2.8-v2.9); a real Playwright browser agent reusing the same retrieval/verification pipeline for free-text fields, with DOM-level fill verification and a literal, unconditional human-approval gate before submit (v3.0); anti-bot/MFA/prompt-injection guardrails (v3.1) centralized into an independent Security Policy Engine + Agent Auditor control plane that every action passes through, plus per-application answer records for interview prep (v3.2); a real **Orchestrator** (v4.0) that classifies a free-text request and dispatches it into one of the three independent, already-tested agents (not a fourth thing built for the demo), with its own routing decision logged as a first-class trajectory; a real **Learning Engine** (v4.1) implementing EXPERIENCE→HYPOTHESIS→COUNTERFACTUAL TEST→EVALUATION→PROMOTE/REJECT over an already-instrumented decision, validated with leave-one-out cross-validation — the only evaluation in this project checked against data withheld while the rule was chosen, not just measured on the benchmark it was designed against. Purposeful, not "20 agents for the sake of it" — four independent decision-making components (generation agent, browser agent, security policy engine, auditor) plus a real orchestrator and a real (narrowly-scoped) learning engine, each with a stated, verified reason to exist. | Addressed |
| End to End Quality | 20 | v2.5-v2.7 produces an actual usable artifact — a generated cover letter, verified free of scope-contamination across two rounds of fixes (`data/evaluation/results/*/documents/*.md`). v3.0 produces an actual filled, browser-verified application form, halted before submit (`data/evaluation/results/browser_mock/`) | Addressed, no UI polish yet (v5) |
| Measured Improvement | 15 | docs/evaluation.md, docs/evaluation_v2.md, docs/evaluation_documents.md, docs/evaluation_browser.md — fair baselines, same task/cases, honest limitations at every version. Hybrid retrieval's agreement rate rose 0.50 -> 0.57 -> 0.71 across two independent corpus corrections while its safety metric held at 0.00 both times; two further plausible-looking fixes (v2.8, v2.9) were each tested and shown to be net losses before being rejected; v3.0 found and fixed two real bugs (one of them in shared infrastructure dating to v2.0) by reading its own trajectory, then re-verified every earlier eval suite for numeric drift rather than assuming the fix was side-effect-free; v3.3's first-ever real-model run (free `PROVIDER=groq`) found and fixed a third shared-infrastructure bug (citation parsing tuned to only one caller's exact output format) and honestly disclosed hitting the free tier's daily quota mid-verification rather than hiding the gap | Addressed |
| Reproducibility | 15 | `make setup && make eval-mock && make eval-v2-mock && make eval-documents && make eval-browser && make eval-security-demo && make eval-orchestrator-demo && make eval-learning-engine` from a clean environment, zero API keys, verified via standalone snapshots after every version (`identityos-v1/` through `-v3.3/`, all also tagged in git — `github.com/Siddhartha24795/identityos/tags`). A judge who wants a real-model qualitative read no longer needs a paid key either — `PROVIDER=groq` (`services/providers/groq_provider.py`) is free with no credit card, and was actually run, not just offered (docs/evaluation.md's v3.3 section has the real output). Note: the free tier's 200,000-token daily cap is real and was hit mid-session — a judge repeating the full real-model suite in one sitting may hit it too | Addressed |
| Hot Take / Insights | 5 | docs/hot_take.md — ten real findings from actually running the eval or reading the output, culminating in two genuine research conclusions: two independent heuristic fixes failing the same way identifies a real boundary of lexical retrieval (v2.9), and a shared test-harness bug surviving three versions because it was validated against only one caller's prompt shape (v3); v3.2 adds an eleventh, at the security-guardrail layer itself (docs/improvement_changelog.md's v3.2 entries) | Addressed |

## Ground rules (10)

1. Built with known tools (Python, pydantic, pytest, fastembed, Playwright) — yes.
2. What existed before vs. added — `PROMPT.md` is the unedited brief; everything else in the repo is new. Digital Self *content* (resume, dossier) is the author's own pre-existing document, explicitly labeled as such in every file it appears in. The v3 demo form (`data/applications/local_demo/application_form.html`) is new, synthetic, and self-labeled as such in its own header comment.
3. Tool/license terms — pydantic/pytest/openai/anthropic/fastembed/playwright used per their standard licenses, no ToS-restricted scraping or reuse. fastembed's BAAI/bge-small-en-v1.5 model is openly licensed and downloaded via its normal public distribution channel; Playwright's Chromium binary is downloaded via its own standard, documented install step (`make setup`), not scraped or repackaged.
4. Consequential actions sandboxed/approval-gated — **now concretely demonstrated, not just described**: `services/browser_engine/agent.py` has no code path where the agent can decide on its own to submit a filled form — `scripts/run_browser_demo.py`'s `--approve-submit` flag is the only way the demo's submit button is ever clicked, defaults off, and is never set by the eval harness. The reference run halts with `submitted: false` every time (docs/evaluation_browser.md). Demonstrated against a local synthetic form the project itself controls, not a real third party, so the "sandbox" is both the code-level gate and the target itself.
5. Qualified human reviewer for anything that could significantly affect someone — the human-approval checkpoint in #4 *is* this reviewer step, made literal: nothing v3.0 does can affect a real application without a human explicitly invoking the approval flag. No real submission has been made in this project.
6. Legal/ethical use case, data handled responsibly — yes: the author's own data, used with their own consent, for their own stated bottleneck; v3's demo form contains no real third party's data or infrastructure.
7. Data you're allowed to share — yes: author's own resume/dossier, not a third party's; the local demo form is authored by this project, not scraped from anywhere.
8. Credentials outside the submission — yes: `.env.example` has empty placeholders, `.env` gitignored, verified no key ever appears in any committed file. Also caught and fixed: `services/browser_engine/field_mapper.py` had hardcoded the project owner's real personal email as demo profile data, which had propagated into committed trajectory/history/security-demo artifacts — not a credential, but private information the same rule is meant to keep out of a submission the organizer may reuse for training/evaluation. Fixed properly, not just patched: the value now comes from `APPLICANT_EMAIL` (`.env`, gitignored, empty in `.env.example`), falling back to a synthetic placeholder (`identityos.demo@example.com`) when unset — the real address is never hardcoded in committed source at all, and every committed artifact was generated with the placeholder default. Every affected artifact regenerated, full test suite re-verified (66 passed).
9. Every claim connected to evidence — yes: every generated claim/section/form field is citation-checked by `services/qa_engine/verification.py`, and every evaluation number in every doc is regenerated from the actual `data/evaluation/results/` JSON, not hand-typed. Both v2.8 and v2.9's negative results were measured against the full benchmark, not asserted from the cases that motivated them; v3's two bug fixes were verified the same way, including re-running every earlier suite for drift.
10. Judges can reproduce the main result — yes: verified via a from-scratch `make setup` in separate, git/venv-free snapshots after every version. `make eval-v2-semantic` / `make eval-documents` need one-time network access to download the embedding model (~65MB); `make eval-browser` needs a one-time `playwright install chromium` (~300MB, done automatically by `make setup`); `make eval-v2-mock` needs none.

## Ground rule 3 — MFA/CAPTCHA/anti-bot ("never bypass")

**Built and tested (v3.1, centralized in v3.2)**, not just planned:
`controller.py`'s `observe()` detects CAPTCHA/anti-bot widget markup and
MFA/OTP/anti-bot phrasing in the page title, and `SecurityPolicyEngine.
evaluate_page()` (`services/security/policy_engine.py`) halts the entire
task before touching any field on either signal; the same engine's
`evaluate()` additionally halts on a per-field MFA/OTP or
identity-verification question, independently of whatever
`field_mapper.py` proposed. Neither path attempts to solve or answer the
challenge — detect-and-halt is the only behavior ground rule 3 permits, so
there is no "handling" beyond that by design. Also added: a field label
is treated as untrusted content and checked for prompt-injection patterns
before it ever reaches an LLM prompt (now via the policy engine, not just
field_mapper's own first-line check), and hidden/honeypot fields are
never filled. All guardrails are tested (`tests/test_security.py`,
`tests/test_browser_engine.py`, including real fixtures exercising actual
DOM detection and one combined-attack scenario) and verified not to
change v3.0's documented reference numbers. A real bug was found and
fixed while building the combined-attack demo: the page-level check
originally scanned the whole page body (including field labels), which
would have incorrectly halted an entire form over one field's wording —
fixed to scan only the page title. Honestly scoped: detection is
pattern/heuristic-based (known markers and phrasings), not a learned
classifier — a sophisticated real anti-bot system may not trigger any of
these signals. Full story: docs/evaluation_browser.md's v3.1 and v3.2
addenda, docs/roadmap.md's v3.1 and v3.2 sections.

## Ground rule 9 (evidence) and the broader security spec — v3.2

The project owner separately provided a much larger "Security, Safety,
Identity Integrity, and Autonomy Guardrail Specification" (preserved
verbatim, docs/security_spec.md) calling for a centralized
`SECURITY_POLICY_ENGINE` and independent `AGENT_AUDITOR` that no action
can bypass. Built as `services/security/policy_engine.py` and
`services/security/auditor.py`: every proposed browser action is
independently re-evaluated (risk-leveled, confidence-floored,
target-validated) and every decision is written to an append-only audit
log, never trusting field_mapper's own first-line checks. Most of the
spec's other sections (self-improvement CI, cross-application dedup,
phishing/domain validation, credential isolation, rollback) require
capabilities — a persistent learning loop, a multi-application store,
real authenticated browsing — this codebase doesn't have anywhere else
yet; each is named explicitly as deferred in docs/roadmap.md's v3.2
section, with the specific missing prerequisite, rather than built as
untested scaffolding or silently dropped.

## Final deliverables (4)

1. **Complete solution code + improvement changelog** — code in this repo; `docs/improvement_changelog.md` covers all versions, includes removed/partially-fixed/not-promoted/later-superseded/root-caused-twice/tested-and-rejected-twice experiments, closes with failure mode + hot take (per version), through v3.0's two bug fixes.
2. **Reproduction guide** — README Quickstart + this file; exact commands, no external data needed beyond what's in the repo, runtime is seconds (or ~1 min including a one-time model download for the semantic/hybrid/document arms, or a one-time Chromium download for the browser arm), cost is $0.
3. **Solution video** — produced: `docs/media/solution_video.mp4` (4:29,
   1280x720, H.264/AAC). Synthesized narration (SVOX Pico TTS) with burned-in
   captions, not a human screen recording — every on-screen quote, number,
   and citation id is copied verbatim from a real artifact already in this
   repo, not invented for the video:
   - the fabricated patent/leadership quotes are copied verbatim from
     docs/evaluation.md's v3.3 "Finding 1" section (the real
     `openai/gpt-oss-120b` output on q13/q17)
   - the Digital Self build output ("96 facts, 4 beliefs", "0.165s") is
     copied from an actual `python scripts/build_digital_self.py` run
   - the Q&A example (`[dossier_excerpts:008]`, confidence 0.99) is copied
     verbatim from `data/evaluation/results/v1_mock/trajectories/q06__identityos_v1.md`
   - the browser-fill screenshots are real Playwright screenshots from a
     live, unmodified `run_application()` call (video-asset capture script
     hooked `BrowserController`'s existing methods for screenshots only —
     no production code was changed to make the video)
   - the v2 requirement-fit example (req14, the governance-gap citation) is
     copied verbatim from `data/evaluation/results/v2_semantic/trajectories/req14__identityos_v2_hybrid.md`
   - the orchestrator routing table (3 requests, matched signals, targets)
     is copied verbatim from `data/evaluation/results/orchestrator_demo/orchestrator_decisions.json`
   - the Learning Engine table (0.714 agreement / 0.00 dangerous-overclaim,
     full-set and leave-one-out) is copied verbatim from
     `data/evaluation/results/learning_v4_1/learning_report.json`
   - the comparison table and changelog numbers match README/evaluation.md exactly
   `docs/demo_script.md` remains the plan for a human-narrated live
   walkthrough (v1-v2.5) if one is ever recorded; the two are complementary,
   not duplicates — the video additionally covers v3's browser agent, the
   security layer, and v4's orchestrator and learning engine, all of which
   postdate the original script.
4. **Agent trajectories** — `data/evaluation/results/*/trajectories/` for every agent across all versions (baseline_plain, baseline_rag, identityos_v1, identityos_v2, identityos_v2_semantic, identityos_v2_hybrid, identityos_v2_5's four document sections, identityos_browser_v3's single form-fill run, orchestrator_v4's 3 routing decisions plus each one's downstream agent trajectory, learning_engine_v4_1's full hypothesize/counterfactual-test/evaluate/leave-one-out-validate trace), covering all 19 v1 questions, all 14 v2 requirements under all three retrieval backends, all 4 cover-letter sections, all 6 v3 form fields plus the approval checkpoint, all 3 orchestrator routes, and all 11 learning-engine threshold candidates plus 14 leave-one-out folds.

## Open items carried forward

- Demo video: produced (see Final deliverables #3 above). A human-narrated
  recording following docs/demo_script.md remains an option but is no
  longer a gap.
- req07 and req12 remain open with two independently-tried, independently-rejected fixes on record — the honest conclusion is that lexical/statistical relevance scoring cannot reliably solve this class of mismatch; the real fix needs semantic judgment (a real LLM call) and a provider key, named for v2.10.
- req11 (genuinely low retrieval confidence) and req14 (the real gap case, safely under-matched on the shipped default) remain open, both already understood, neither new.
- `identityos_v2_semantic` (standalone) remains unsafe as its own system (dangerous overclaim rate 0.50 as of v2.6-v2.7, re-measured at 0.75 after v3's shared-infrastructure bug fix — docs/evaluation_v2.md's v3 addendum) — expected and not a priority, since it was never the shipped path; `identityos_v2_hybrid` already achieves the safety guarantee, now confirmed stable across three consecutive real corpus changes, two rejected retrieval experiments, and one shared-infrastructure fix.
- req08's dangerous overclaim was resolved in v2.1 via general corpus completion. req13's underclaim was resolved in v2.2 via clause-level negation. v2.3's embedding retrieval was evaluated honestly and not adopted after it reintroduced a dangerous overclaim; v2.4 diagnosed why and built a verified fix. v2.5 found a document-scope substitution; v2.6 and v2.7 traced it to the same authoring error in two different source files and fixed both. v2.8 and v2.9 each diagnosed a further mechanism, tested a fix against the full benchmark, and correctly declined to ship it after the measurement showed a net loss — the same rigor applied to negative results as to every positive one.
- v3.0/v3.1's scope is intentionally narrow (single-page, no file upload) — named explicitly in docs/roadmap.md's v3.2+ section rather than implied as complete. v3.1's anti-bot/MFA/injection guardrails are pattern-based, not a learned classifier — a sophisticated real anti-bot system may not trigger any of the known markers checked; the guarantee is "known, common patterns are caught," not "every mechanism is caught" (docs/evaluation_browser.md's v3.1 addendum).
