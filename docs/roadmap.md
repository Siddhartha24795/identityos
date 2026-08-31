# Roadmap

Built version by version, on request, per the original build instruction:
"Don't build everything. Build things version by version." Each version
below is scoped to be independently demonstrable and independently
evaluable — no version depends on a later one existing to be judged.

## v1 — Digital Self + confidence-gated Q&A  ·  **built, this delivery**

Identity ingestion (structured sources -> Fact/Belief with provenance),
lexical retrieval, citation-grounded generation, per-sentence verification,
confidence-gated refusal, a 19-question Identity Fidelity Benchmark
comparing baseline_plain / baseline_rag / identityos_v1, full trajectory
logging. See docs/architecture.md, docs/evaluation.md.

## v2.0 — Application compilation + real-ground-truth benchmark  ·  **built**

Requirement-fit assessment against a real, already-adjudicated application:
the IITACB CEO dossier's own 14-requirement fit table, where a real human
had already written both the requirement and their own honest
self-assessment (MET/EXCEEDS/PARTIAL/GAP) with evidence. This is the
"REAL HUMAN ANSWER vs IDENTITYOS ANSWER" comparison the original brief
calls for and v1's benchmark did not have. See docs/evaluation_v2.md,
docs/improvement_changelog.md (v2 entries), docs/hot_take.md (v2 addendum).

Found and fixed one real bug in the process (system confidently overclaiming
a requirement the person had honestly marked as a gap, because "well-cited"
and "positive" got conflated) — documented, not hidden, per the hackathon's
own instruction not to hide failures.

## v2.1 — general corpus completion  ·  **built**

Full, general corpus completion — `data/identity_sources/` was a curated
subset of the two source documents, not a full transcription. Rather than
patching the one remaining known failure (req08) reactively, transcribed
the entire remaining requirement-evidence table plus the dossier's broader
narrative sections in one general pass
(`data/identity_sources/dossier_narrative.md`), independent of which eval
question needed what. Result: dangerous_overclaim_rate 0.25 -> 0.00, and
v1's own score also improved as a side effect. See
docs/improvement_changelog.md (Iteration 6) and docs/evaluation_v2.md.

## v2.2 — clause-level negation  ·  **built**

Fixed req13 (Kannada fluency): a claim mixing a positive and a negative
clause in one sentence was scored fully negative by whole-sentence
detection. Now splits on unambiguous contrastive conjunctions and buckets a
mixed claim as `partial`, not `gap`. Agreement rate 0.36 -> 0.43, no
regressions on the other 13 requirements (re-verified, not just inspected
in isolation), dangerous overclaim rate held at 0.00. See
docs/improvement_changelog.md (Iteration 7), docs/evaluation_v2.md.

## v2.3 — embedding-based retrieval  ·  **built, not promoted to default**

Built `identityos_v2_semantic` (services/embeddings/, fastembed +
BAAI/bge-small-en-v1.5, ~65MB ONNX model, no API key) as a real comparison
arm alongside lexical `identityos_v2`. It genuinely fixed req10 and
improved req05, confirming the lexical-retrieval limitation was real and
addressable. It also reintroduced a dangerous overclaim (req09) and
downgraded six previously-correct requirements, because higher-recall
retrieval interacts badly with v2.2's polarity check — see
docs/hot_take.md's v2.3 addendum. **Decision at the time: keep lexical
retrieval as the shipped default**; the semantic arm stays in the harness,
not deleted, as an honest ongoing comparison. (Superseded by v2.4 below —
kept here because the changelog shouldn't quietly rewrite what was
actually decided at each point.) See docs/improvement_changelog.md
(Iteration 8), docs/evaluation_v2.md.

## v2.4 — hybrid retrieval  ·  **built, promoted**

Diagnosed the exact mechanism behind v2.3's regression — semantic noise
only appeared when it overrode requirements lexical already had evidence
for — and built `retrieve_hybrid()` to target exactly that: lexical first,
semantic fallback only when lexical returns nothing. Verified
requirement-by-requirement, not assumed: all 12 requirements lexical could
already answer are byte-identical to pure lexical output. Result:
agreement rate 0.50 (best of all five systems), dangerous overclaim rate
0.00 (matches lexical). **This supersedes v2.3's decision — hybrid
retrieval is now the recommended strategy**, kept alongside lexical-only
and semantic-only as permanent comparison arms. See
docs/improvement_changelog.md (Iteration 9), docs/evaluation_v2.md,
docs/hot_take.md's v2.4 addendum.

## v2.5 — Document Generation (cover letter)  ·  **built**

First real generated artifact: a 4-section cover letter
(`services/document_engine/`), reusing hybrid retrieval and verification
unmodified, plus `_prefer_unused()` — a concrete, working instance of the
brief's `APPLICATION_NARRATIVE_STATE` (spread evidence across sections
instead of repeating the same two facts). Evidence coverage 0.95,
unsupported-claim rate 0.05, repeated-evidence rate 0.32, vs. the usual
0.00/1.00/n-a for both baselines.

Found a genuinely new failure mode by reading the actual letter, not just
its passing score: real, grounded, true evidence can still be the *wrong
scope* for the document being written (strategy narrative for one specific
prior application, cited as if it were general evidence about the
person). Added `FactCategory.APPLICATION_SPECIFIC` to tag and exclude it.
This closed the obvious case and — found on re-inspection, not hidden —
left a subtler one: the same contamination survives inside individual
sentences of otherwise-general facts, one level more granular than the fix
addresses. See docs/evaluation_documents.md, docs/hot_take.md's v2.5
addendum, docs/improvement_changelog.md.

## v2.6 — corpus authoring correction  ·  **built**

Root-caused v2.5's sentence-level leak to an actual authoring error, not a
missing classifier: five bullets in `dossier_narrative.md` conflated a
general statement with an IITACB-specific comparison in one sentence,
violating this project's own one-fact-per-line rule. Split all five, not
just the one that had been visibly wrong, into general + separately-tagged
`APPLICATION_SPECIFIC` facts. Result: hybrid retrieval's agreement rate
0.50 -> 0.57 with dangerous overclaim rate held at 0.00 through a real
corpus change; req05 now a full exact match. Also found — and left open —
a near-identical conflation in a different source file. See
docs/improvement_changelog.md (Iteration 10-11), docs/evaluation_v2.md,
docs/evaluation_documents.md, docs/hot_take.md's v2.6 addendum.

## v2.7 — corpus authoring correction, second file  ·  **built**

Applied the exact v2.6 audit to `dossier_excerpts.md`'s "SELF-ASSESSED
GAP" section — the file where v2.6 itself had found a near-identical
conflation on re-reading the regenerated letter. Split a general
capability-gap fact from "the committee should not be persuaded..."
(IITACB's Managing Committee), and a general language-fluency fact from a
relocation commitment made specifically for the IITACB role. Result:
hybrid retrieval's agreement rate 0.57 -> 0.71 (req03 and req06 now exact
matches), dangerous overclaim rate held at 0.00 through a *second*
consecutive real corpus change. Generated letter re-verified clean of
every application-specific phrase flagged across v2.5-v2.6. See
docs/improvement_changelog.md (Iteration 12), docs/evaluation_v2.md,
docs/evaluation_documents.md, docs/hot_take.md's v2.7 addendum.

## v2.8 — investigated req07/req12, tested a fix, rejected it  ·  **built**

Diagnosed the cause of two of the four remaining mismatches: a fact
sharing exactly one token with the requirement can rank into the retrieved
set and contribute an unrelated negation marker, wrongly downgrading an
otherwise-correct answer. Added `min_shared_tokens` as an optional,
backward-compatible parameter to `retrieve()`/`retrieve_hybrid()` and
tested the obvious fix (require 2+ shared tokens) against the full
benchmark. It fixed req07/req12 and broke req08/req09 — the same weak
single-token matches were noise for one pair and load-bearing correct
evidence for the other. **Not adopted**; shipped retrieval behavior is
unchanged. See docs/improvement_changelog.md (Iteration 13),
docs/evaluation_v2.md, docs/hot_take.md's v2.8 addendum.

## v2.9 — relevance-weighted polarity, tried two ways, both rejected  ·  **built**

Implemented the fix v2.8 pointed to: IDF-weighted retrieval scoring
(`build_idf_table()`, `retrieve_idf()`) and a relevance-dominance gate on
the polarity vote (`bucket_from_signals(..., relevance_scores=...)`).
Tested both against the full benchmark. IDF reordering changed rank but
not inclusion (a fact ranked #2 is still retrieved and cited under a
generous top-k) — no effect. The dominance gate fixed req12, and flipped
req14 — the single highest-stakes requirement in the benchmark — into a
dangerous overclaim, because the correct gap-stating fact scored lower by
IDF than an unrelated fact cited alongside it. **Not adopted.** Both
tools stay in the codebase at safe, unused-by-default configurations.
**Conclusion**: two independent heuristic fixes for req07/req12 have now
failed for the same structural reason — lexical/statistical relevance
scoring cannot reliably identify "the fact that actually settles this
question." This is a real ceiling on the lexical-retrieval approach, not a
tuning problem; the next real step needs semantic judgment (a real LLM
call), not a third heuristic. See docs/improvement_changelog.md
(Iteration 14-15), docs/evaluation_v2.md, docs/hot_take.md's v2.9 addendum.

## v2.10+ — deferred  ·  not started

- req07/req12 stay open pending real semantic relevance judgment (a real
  LLM call scoring "does this fact actually address this requirement"),
  which needs a provider API key — not another lexical heuristic. This is
  now a well-evidenced architectural boundary (v2.8-v2.9), not an
  unexplored option.
- Automatic belief inference from raw unstructured text (replacing v1/v2's
  hand-seeded beliefs) with an LLM pass plus counter-evidence search — the
  same missing ingredient (real semantic judgment) as the item above.
- Extend document generation to other types (SOP, research statement,
  short-answer set) and to a *named* target opportunity (a real
  `ApplicationIntentModel`, not just a generic-role system prompt).
- identityos_v2_semantic (standalone) remains unsafe as its own system
  (dangerous overclaim rate 0.50 as of v2.6-v2.7, re-measured at 0.75 as of
  v3's MockProvider fix — see docs/evaluation_v2.md's v3 addendum) — not a
  priority to fix directly, since it was never the shipped path; hybrid
  already achieves the safety guarantee semantic-alone doesn't.
- req11 (genuinely low retrieval confidence, 0.51) and req14 (the real gap
  case, system says `partial` on the shipped default, a safe underclaim)
  remain open — both already understood, neither a new finding.
- `resume.md` was checked for the same conflation pattern (grepped for
  IITACB/committee/secretariat/role-specific framing) and found clean —
  its one "Secretariat" mention is the same legitimate "Cabinet
  Secretariat" government body already distinguished in v2.6's test. No
  further audit needed there; both files that actually had the defect
  (from the IITACB dossier) are now fixed.

## v3.0 — Browser execution  ·  **built**

Real browser agent (Playwright, `services/browser_engine/`): opens a form,
detects fields via DOM inspection (label text + input type, generalized —
not hard-coded to one page's markup), maps each to Digital Self data
(direct/known-profile for name/email, lexical option-match for selects,
the full v1/v2 hybrid-retrieval + generation + verification pipeline reused
unmodified for free-text fields), fills, re-observes and verifies each
value against the live DOM (the brief's `BROWSER VERIFICATION` dimension),
decides the accuracy-confirmation checkbox from aggregate confidence +
verification, then **halts for human approval before any submit** — there
is no code path where the agent can decide on its own to submit
(`services/browser_engine/agent.py`; ground rule 4, implemented literally,
not just described). Demonstrated against a local, offline, synthetic
application form (`data/applications/local_demo/`) rather than a real
third-party site, for the same ToS/safety/generalization reasons v1/v2 use
the author's own real documents instead of scraping anything. Result:
`n_fields: 6, n_filled: 6, n_verified: 6, avg_evidence_coverage: 1.0,
avg_confidence: 0.934, halted_for_approval: true, submitted: false`. Found
and fixed two real bugs by reading the actual trajectory output (a
select-field verification mismatch, and a systemic MockProvider
prompt-parsing bug that turned out to predate v3 and affect v2/v2.5 too)
— documented, not hidden, per the hackathon's own instruction. See
docs/evaluation_browser.md, docs/improvement_changelog.md (Iteration
16-17), docs/hot_take.md's v3 addendum.

## v3.1 — Anti-bot, MFA/OTP, and prompt-injection guardrails  ·  **built**

Built in direct response to a question asked before the first real-LLM
run: does this agent detect an "are you a robot?" check, a CAPTCHA, an
MFA/OTP step, or an injected instruction hidden in a field label, rather
than confidently answering through it? Four independent guardrails, each
tested (`tests/test_browser_engine.py`), each ending the same way —
HALT_FOR_APPROVAL, never a silent skip and never an automated bypass:

1. **CAPTCHA/anti-bot widgets** (`controller.py`'s `observe()`): detects
   common widget markup (`iframe[src*=captcha]`, `[class*=captcha]`,
   `[id*=captcha]`) and anti-bot phrasing in the page TITLE
   (`services/browser_engine/safety.py`). Either signal halts the entire
   task before any field is touched — ground rule 3 ("never bypass
   MFA/CAPTCHA/anti-bot protections") implemented as detect-and-stop, the
   only compliant behavior, not detect-and-solve.
2. **MFA/OTP challenges**: the same page-level halt, plus a per-field halt
   if an individual field asks for a one-time code — a human must enter
   this, never the agent.
3. **Prompt injection in a field's own label** ("ignore all previous
   instructions and select..."): a field label is untrusted content from
   a page this agent doesn't control and must never be treated as an
   instruction. Checked in `field_mapper.map_field()` before any label
   text is assembled into an LLM prompt — the flagged field halts, others
   are unaffected.
4. **Zero-evidence refusal for genuinely unanswerable fields**
   (`field_mapper._map_textarea_field()`): if `retrieve_hybrid()` finds
   nothing at all — lexically or semantically — the field halts instead
   of letting the mock provider's hallucination fallback (or a real LLM's
   own confident-sounding guess) produce an ungrounded answer. Gates on
   evidence_coverage, not citation-inherited confidence — the latter is
   the exact signal docs/hot_take.md already showed is unreliable for
   this. This is the general mechanism that also catches an off-topic
   decoy question ("what's your favorite biryani recipe?") without
   hand-coding that example.

Also added: hidden/invisible fields (a classic spam-bot "honeypot" trap)
are now excluded from `observe()`'s field list entirely — never filled,
the same way a sighted human filling the form by hand never would.

None of this changes v3.0's documented reference-run numbers — re-verified
byte-identical (`n_fields: 6, n_filled: 6, n_verified: 6`, etc.) after
every change, since the local demo form has no adversarial content for
these guardrails to fire on. Two new local, offline test fixtures
(`data/applications/local_demo/adversarial_captcha.html`,
`adversarial_honeypot.html`) exercise the DOM-detection paths that fake
`DetectedField` objects can't reach; neither is used by `make eval-browser`
or any documented result. See docs/evaluation_browser.md's v3.1 addendum.

## v3.2 — Security Policy Engine, Agent Auditor, and per-application records  ·  **built**

Built in direct response to a much larger "Security, Safety, Identity
Integrity, and Autonomy Guardrail Specification" the project owner
provided (preserved verbatim at docs/security_spec.md) — a full
production-grade control-plane architecture spanning identity provenance,
temporal validity, cross-application consistency, self-improvement CI,
phishing/domain validation, credential isolation, rollback, and more.
That spec is enterprise-scale; v3.2 implements the parts that are
tractable and testable against what this codebase actually has today, and
names everything else as deliberately deferred, with why, rather than
building untested scaffolding for capabilities (a persistent learning
loop, a multi-application store, real authenticated navigation) that
don't exist anywhere else yet.

**Built:**

1. **`SecurityPolicyEngine`** (`services/security/policy_engine.py`) — the
   spec's core architectural rule ("no direct execution path may bypass
   this control plane"), implemented literally. Every proposed field
   action passes through `evaluate()` regardless of what
   `field_mapper.py` decided; `evaluate_page()` runs right after
   `observe()` and blocks the whole task on a page-level anti-bot/CAPTCHA/
   MFA signal; `evaluate_submit()` extends ground rule 4 so that an
   unresolved BLOCK/ESCALATE finding anywhere in the run's audit trail
   vetoes submission even if the caller passed `approve_submit=True`.
   Actions are classified into the spec's five risk levels
   (LEVEL_0_INFORMATIONAL .. LEVEL_4_CRITICAL) with configurable
   per-level confidence floors.
2. **`AgentAuditor`** (`services/security/auditor.py`) — a second,
   independent opinion, deliberately checking what the policy engine does
   not: that every cited evidence id actually exists in the Digital Self
   (catching a fabricated citation), and that generated text doesn't leak
   the field's own label verbatim (the exact shape of v3.0's MockProvider
   bug, generalized into a permanent, always-on check).
3. **Append-only audit log** (`services/security/audit_log.py`) — one
   `ActionRecord` per decision, written to
   `data/evaluation/results/<tag>/security_audit.jsonl`. The schema has no
   field that could hold a secret, by construction, not by redaction.
4. **A combined attack demonstration**
   (`data/applications/local_demo/adversarial_mixed.html`,
   `scripts/run_security_demo.py`, `make eval-security-demo`) — per the
   spec's own requirement that "the final demo must intentionally include
   several attacks/failures and visibly demonstrate detect / explain /
   block-or-escalate / recover / continue the legitimate workflow": one
   form with two legitimate fields, a prompt-injection attempt, an
   identity-verification question, and an off-topic decoy, run in a
   single pass. Real output: both legitimate fields filled and verified;
   all three attacks halted with an explained rationale; the run
   completes and correctly refuses to submit. See
   docs/evaluation_browser.md's v3.2 addendum for the actual recorded output.
5. **`ApplicationRecord`** (`packages/schemas/application_record.py`,
   `services/application_record/`) — not from the security spec, a direct
   ask: for every application this agent fills, save the questions asked
   and answers given (with evidence and confidence) as both JSON and a
   human-readable Markdown crib sheet, so a person can check what they
   actually told a specific employer once they reach interview stage,
   without relying on memory. Written automatically at the end of every
   `run_application()` call to `data/applications/history/`. This is also
   a minimal, real instance of the spec's `APPLICATION_MEMORY` concept
   (scoped per application, not merged into one global store), giving a
   future cross-application-consistency check real data to compare
   against.

None of this changed v3.0/v3.1's documented reference-run numbers —
re-verified byte-identical after every change. One real bug was found and
fixed while building this: the page-level anti-bot check originally
scanned the *entire* visible page text, which includes every field's own
label — so a single field asking "Are you a robot?" incorrectly halted
the whole task instead of just that field. Fixed by scanning only the
page *title* for page-level signals, letting the per-field checks (which
were already correctly scoped) handle individual suspicious fields while
the rest of the form continues — caught by the same "build the adversarial
test fixture, read what actually happens" discipline as every other
finding in this project, not assumed correct from the design. See
docs/improvement_changelog.md's v3.2 entries.

**Deliberately not built, and why** (see docs/security_spec.md for the
full text of every section named below):

- **Identity Integrity Engine, temporal identity validation, belief
  anti-confirmation** — these require the Digital Self to already support
  versioned, time-stamped, supersession-aware belief states. The current
  `Fact`/`Belief` schema (`packages/schemas/identity.py`) has confidence
  and provenance but not `valid_from`/`valid_until`/`supersedes`; adding
  those fields without a real multi-version identity history to test them
  against would be untested scaffolding.
- **Cross-application consistency, application deduplication, eligibility
  guardrail** — all three need a store of *multiple* real applications to
  compare against. `ApplicationRecord` (above) is the first step — it
  creates that store — but nothing reads it back yet; a real
  consistency/dedup check is the natural v3.3+ item once there's more than
  one recorded application to test against.
- **Self-improvement safety, identity regression CI, anti-promotion,
  reward-hacking defense** — all assume a *persistent, general* learning/
  self-improvement loop that keeps running and keeps proposing changes.
  v4.1 (docs/roadmap.md's v4.1 section) built one scoped instance of the
  EXPERIENCE -> HYPOTHESIS -> COUNTERFACTUAL TEST -> EVALUATION ->
  PROMOTE/REJECT loop — a single, one-shot decision (a retrieval-fallback
  threshold), validated with leave-one-out cross-validation rather than a
  CI gate. It is not a persistent loop that runs on every future
  application and proposes its own next hypothesis; building CI/anti-
  reward-hacking guardrails around that larger, ongoing version of the
  loop still has nothing real to test against, since that larger loop
  itself doesn't exist yet.
- **Domain/phishing validation, credential isolation, OTP-channel
  abstraction, file safety** — all assume real authenticated, multi-domain
  browsing (the current demo is a single local `file://` form) or real
  credential handling (this system has none — there is nowhere for a
  password or token to even enter the codebase yet). MFA/OTP *detection*
  is built (v3.1/v3.2); the *channel abstraction* the spec describes has
  nothing to abstract yet.
- **Rollback, security dashboard, the full 25-item security test suite** —
  rollback needs persistent state mutations to roll back (none exist yet
  beyond `data/digital_self/` versioning, which is already append-only and
  never overwrites); a dashboard needs a running system with traffic to
  monitor, not a one-shot eval harness; the 25-item suite maps mostly onto
  capabilities named above as not yet built — the tests that *are*
  buildable now (prompt injection, hidden fields, unauthorized submission,
  fabricated evidence, identity-verification fields) are built and passing
  (`tests/test_security.py`, `tests/test_browser_engine.py`).

## v3.3 — First real-model run, a free provider, and a shared citation-parsing bug  ·  **built**

Every "re-run with a real provider" line across this project's docs, since
v1, was a deferred next step. Added `GroqProvider`
(`services/providers/groq_provider.py`, free, no credit card, reuses the
`openai` client already a dependency, pointed at Groq's OpenAI-compatible
endpoint) and actually took that step for the first time. It found three
real things in one pass:

1. **A real generative model fabricates specific, detailed, mutually
   contradictory answers a deterministic mock never could** — given zero
   context, `baseline_plain` invented a complete fake patent number and a
   fake three-year nonprofit leadership role with fabricated statistics,
   while answering a differently-worded version of that same underlying
   fact the opposite way in the same run.
2. **The hard-case overclaim detector's predicted blind spot, now
   measured**: `_HARD_CASE_RULES`' exact-phrase matching, calibrated
   against the mock provider's wording, missed both fabrications above —
   named as a real v3.4+ item (semantic judgment, not a longer phrase
   list), not patched with more hand-picked phrases.
3. **A real, root-cause bug in shared verification infrastructure**: the
   citation-parsing regex only ever matched the mock provider's exact
   bracket style (`[id]`, zero whitespace, one id) — a real model's
   `[ id ]`, `[id1; id2]`, and fullwidth `【id】` brackets all silently
   failed to parse, which dragged a **correct, honestly-hedged** answer
   to the single highest-stakes question in the v1 benchmark below the
   refusal threshold for the wrong reason. **Fixed at the root**
   (`services/qa_engine/verification.py`); every mock-provider suite
   re-verified byte-identical afterward; offline re-verification of the
   already-collected real-model outputs showed 4 of 5 refusals were pure
   artifacts of this bug (refusal count 5 -> 1, IFS 0.824 -> 0.838).

Also found and fixed, while wiring the provider up: `python-dotenv` was a
listed dependency nothing actually imported, so `.env` was never loaded
automatically by any script — fixed by adding `load_dotenv()` to every
eval script's entry point. And measured a real token-efficiency issue:
the default model is a reasoning model that was burning most of its
token budget on hidden reasoning (585 of 600 tokens on one call);
`reasoning_effort="low"` cut that 5-25x with no observed quality loss and
is now the provider's default.

Full write-up, exact fabricated text, and the honest disclosure that the
Groq free tier's daily token cap was hit before a fresh low-effort re-run
could complete in this session: docs/evaluation.md's v3.3 section,
docs/hot_take.md's v3.3 addendum, docs/improvement_changelog.md
(Iteration 27-31).

## v3.4+ — Browser execution, deferred scope  ·  not started

- Multi-page navigation (the local demo form is single-page).
- File upload fields (resume/portfolio attachments).
- A real third-party target site, once one is explicitly named and its
  terms of use reviewed — deliberately deferred past this hackathon
  submission for the same reason v1/v2 use the author's own documents.
- v3.1/v3.2's guardrails are pattern/heuristic-based (regex and substring
  matching), not a learned classifier — same honestly-disclosed limitation
  as every other heuristic in this project (docs/hot_take.md). A more
  sophisticated real-world CAPTCHA/anti-bot system (behavioral analysis,
  invisible reCAPTCHA v3 scoring) may not surface any of the text/DOM
  markers checked here; the guardrail's guarantee is "known, common
  patterns are caught and halted," not "every anti-bot mechanism is caught."
- Everything named "deliberately not built, and why" in v3.2 above.
- `identityos_v2_semantic`'s dangerous overclaim rate, re-measured at 0.75
  after v3.0's MockProvider fix (up from 0.50) — not a v3 regression, but a
  previously-masked weakness in a system that was never the shipped path;
  still not a priority to chase directly (see docs/roadmap.md's v2.10+
  section above).
- The hard-case overclaim detector's exact-phrase blind spot, found in
  v3.3: `_HARD_CASE_RULES` missed two real, severe fabrications (a fake
  patent, a fake nonprofit leadership role) because neither used the
  hand-picked phrases the rule checks for. The real fix needs semantic
  judgment (does this text assert sole credit / a leadership role that
  didn't happen), not a longer phrase list — the same conclusion v2.9
  reached independently for a different metric.
- A fresh, full real-model re-run of v1 (and v2/v2.5/v3) with
  `reasoning_effort="low"` — v3.3's corrected numbers for v1 come from
  offline re-verification of already-collected outputs, not a new live
  run, because the Groq free tier's daily token cap was reached first.

## v4.0 — Orchestrator  ·  **built**

`services/orchestrator/router.py` classifies a free-text request
(heuristic keyword/pattern match, not a learned classifier — same
documented simplification as v1's question-type "classify" stage) and
dispatches it into exactly one of the three already-built, independently-
tested agents: QA (v1 `identityos_agent`), application-fit (v2
`identityos_v2_hybrid`), or browser-fill (v3 `browser_engine.agent`). Its
own routing decision is written as a first-class Trajectory, separate from
the routed agent's own trajectory (`make eval-orchestrator-demo`).

**Honestly scoped against the brief's fuller vision:** this is "decide
which of three existing agents handles this," not the brief's full
Identity/Opportunity/Browser/Verification/Contradiction multi-agent roster
with dynamic agent creation. Opportunity discovery and a separate
Contradiction agent remain v5-scope (below) — there was nothing in this
codebase yet for an orchestrator to route *to* for either.

## v4.1 — Learning Engine  ·  **built, narrowly scoped**

`services/learning_engine/engine.py` implements EXPERIENCE -> HYPOTHESIS
-> COUNTERFACTUAL TEST -> EVALUATION -> PROMOTE/REJECT
(docs/research_hypothesis.md #2: "never auto-trust a successful
trajectory") for one concrete, already-instrumented decision: below what
lexical-evidence-coverage threshold does semantic retrieval become worth
its known risk (docs/evaluation_v2.md's dangerous-overclaim finding)? It
operates on the real, already-committed v2_semantic per-requirement
results — no new LLM calls — searches a threshold grid, promotes only a
candidate that is both dangerous-overclaim-free and at least as good as
the already-shipped hybrid heuristic, and then validates the promoted rule
with **leave-one-out cross-validation** (`make eval-learning-engine`) —
the one place in this project a decision rule is checked against data it
never saw while being chosen, rather than measured on the same benchmark
it was designed against (every other version's honest limitation, named
repeatedly in docs/hot_take.md).

**Real result, not asserted**: no threshold beats hybrid's hand-designed
rule; the search confirms hybrid was already at the ceiling a
coverage-only signal can reach for this benchmark, with the same LOO
numbers (agreement 0.714, dangerous-overclaim 0.0) as the full-set fit —
a genuine negative-for-improvement, positive-for-validation outcome. Full
story: docs/improvement_changelog.md's v4.1 entry.

**Honestly scoped against the brief's fuller vision:** this is a
meta-learning policy over one existing signal and two existing retrieval
strategies, not a Digital Self mutation, not automatic belief updating,
and not a general "propose arbitrary code changes" loop — the brief's
COUNTERFACTUAL_EVALUATION section (question wording changes, a different
organization asks it, the website layout changes) is a much larger claim
than "this one retrieval-selection threshold generalizes across held-out
requirements in this one benchmark," which is what was actually built and
measured.

- Contradiction graph made explicit and queryable, not just belief-level
  counter-evidence fields — still not started; would need a second real
  application (or a second version of this one) with an actual contradiction
  to detect, not a synthetic one built to exercise the feature.
- A dynamic multi-agent roster beyond the 3-way orchestrator above (the
  brief's Identity/Opportunity/Browser/Verification/Contradiction agents
  as separate, independently-reasoning components) — still not started.

## v5 — Graph store + opportunity discovery + web UI  ·  not started

- Migrate Digital Self storage from flat JSON to a proper graph (the brief
  suggests Neo4j) once edge types (SUPPORTED_BY, CONTRADICTS, SUPERSEDES...)
  justify it.
- Opportunity discovery agent + fit scoring.
- Next.js dashboard: Digital Self Explorer, Application Workspace, Agent
  Trajectory View, Identity Diff (before/after Digital Self).

## Explicitly deferred, revisit only if asked
Visa/administrative form support, conference-submission support,
accelerator-specific strategy — the brief's "extensible application types"
list. v1-v3 prove the architecture generalizes before widening the type list.
