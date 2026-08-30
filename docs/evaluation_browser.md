# Evaluation — v3.0 (Browser Automation)

## What this is

The original design brief's `BROWSER AUTOMATION` section, scoped to what
v3.0 actually builds: a single-page form fill, against a local, offline,
synthetic application form (`data/applications/local_demo/application_form.html`)
representing every field type the brief names — text, textarea, select,
checkbox — rather than a real third-party site. No named real target
exists yet, and scraping/filling a real company's site without an explicit
engagement would be exactly the kind of "consequential action against a
system we don't control" this project's own ground-rule compliance
(docs/hackathon_compliance_check.md) argues against. Same reasoning v1/v2
apply to using the author's own real documents instead of a scraped
corpus: prove the abstraction generalizes on a case we fully control before
widening scope (docs/roadmap.md's v3.1+ section).

Reproduce: `python scripts/build_digital_self.py && python scripts/run_browser_demo.py mock browser_mock fastembed`.
Read the trajectory, not just the score: `data/evaluation/results/browser_mock/trajectories/browser_demo__identityos_browser_v3.md`.

## The pipeline

```
open(url) -> observe() [DOM inspection: label text + input type -> DetectedField]
   -> map_field() per field:
        text   -> known-profile lookup (name / email) or HALT
        select -> lexical overlap between options and Digital Self facts
        textarea -> the unmodified v1/v2 pipeline: hybrid retrieval
                    -> cited generation -> per-claim verification
        checkbox -> deferred until every other field's confidence is known
   -> fill + re-observe -> BROWSER VERIFICATION (compare filled vs. observed DOM value)
   -> decide the accuracy-confirmation checkbox from aggregate
      confidence + verification
   -> HALT FOR APPROVAL (ground rule 4) — always logged, submit only if
      the caller explicitly passed approve_submit=True
```

`services/browser_engine/agent.py` implements ground rule 4 literally:
there is no code path where the agent decides on its own to submit.
`scripts/run_browser_demo.py`'s `--approve-submit` flag is the only way
the demo form's submit button is ever clicked, and it defaults off; the
eval harness (`services/evaluation/run_eval_browser.py`) never sets it.

## Result (reference run, `PROVIDER=mock`, `EMBEDDING_PROVIDER=fastembed`)

| Metric | Value |
|---|---|
| Fields detected | 6 (text x2, select x1, textarea x2, checkbox x1) |
| Fields filled | 6 / 6 |
| Fields verified (BROWSER VERIFICATION) | **6 / 6** |
| Avg. evidence coverage (textarea fields) | **1.00** |
| Avg. confidence (fillable fields) | **0.93** |
| Halted for approval | **true** |
| Submitted | **false** (no `--approve-submit` passed) |

There is no baseline comparison table here, unlike v1/v2/v2.5: a
"baseline" browser agent (fill every field with a plain LLM call, no
retrieval, no verification, no approval gate) would trivially "pass" a
structural fill/verify check while providing zero evidence grounding and
zero human checkpoint — the two properties this version actually tests.
The meaningful comparison for v3 is the ground-rule-4 checkpoint itself
(below), not a coverage number against a strawman.

## Two real bugs, found by reading the actual trajectory

The first run reported `n_verified: 4/6`, not 6/6. Per this project's
standing practice (every version so far), the trajectory was read in full
before trusting the score, and two real bugs turned up:

**1. Select-field verification compared the wrong representation.**
`BrowserController.observe()` used `el.input_value()` for `<select>`
elements, which returns the underlying `<option value="...">` attribute
(e.g. `cto_leadership`), while `field_mapper.py` fills and compares using
the option's visible label text (e.g. `CTO / technical leadership`). The
"desired role" field was correctly filled and showed `FAIL` anyway,
purely from an observe/fill representation mismatch. Fixed by reading the
selected option's own `inner_text()` in `observe()` instead, so fill,
observe, and compare all use the same representation.

**2. A systemic MockProvider prompt-parsing bug, not scoped to v3.**
The generated text for "what is your most impactful project, and why?"
contained the literal fragment `"...Perforce. What is your most impactful
project, and why? FIELD LABEL:"` — clearly not real evidence. Traced to
`MockProvider.complete()` hardcoding a literal `"QUESTION:"` string to
find where context ends; v3's `field_mapper.py` prompts with
`"FIELD LABEL:"` instead, which the old parser never matched, so it fell
back to treating the entire prompt (label included) as its own context,
letting the label self-match and leak into the answer. Grepping the rest
of the codebase found the identical latent defect in v2's `assess.py`
(`"REQUIREMENT:"`) and v2.5's `generate.py` (`"SECTION PROMPT:"`) — masked
there because real matching facts normally outscore a trivially
self-matching label, until v3's own field-label prompts produced a case
weak enough to expose it. **Fixed at the root**, in `mock_provider.py`
only: the parser no longer requires a specific keyword, it takes the text
after the last blank line as the query regardless of the header's name.

Both fixes were followed by a full re-run of every affected suite (v1, all
three v2 retrieval arms, v2.5), not just v3's own demo — see
docs/evaluation_v2.md's v3 addendum and docs/evaluation_documents.md's v3
addendum for what did and didn't change, and docs/hot_take.md's v3
addendum for the general lesson. **After both fixes: 6/6 fields verified,
avg. evidence coverage 1.00, no leaked prompt text in any generated
field** (also covered by `tests/test_browser_engine.py`'s regression
tests).

## What v3.0 does and doesn't cover

**Covers**: single-page forms, DOM-based field detection generalized
across any page with standard form semantics (not hard-coded to this
form's specific ids — matching is by label text and input type), all four
field types the brief names, browser-level fill verification, and a
literal, unconditional human-approval gate before submit.

**Does not cover** (named honestly in docs/roadmap.md's v3.1+ section, not
hidden): multi-page navigation, file uploads, and CAPTCHA/OTP/MFA
handling. The synthetic form has none of the latter, so nothing has been
built or tested for it yet — ground rule 3 ("never bypass MFA/CAPTCHA/
anti-bot protections") requires any future implementation to make that a
human-in-the-loop pause, never an automated bypass, and that requirement
is recorded before the feature exists, not after.

## What this run does and doesn't prove

Same mock-provider caveat as v1/v2/v2.5: the textarea fields' generated
text comes from the deterministic, extractive `MockProvider`, not a real
LLM — it proves the harness's structural behavior (does it cite evidence,
verify against the live DOM, and refuse to submit without approval), not
prose quality. A real LLM/VLM run is the natural next step for a
qualitative read, and for handling pages where field labels aren't plain
DOM text (e.g. reading a rendered screenshot) — deferred to v3.1+, since
it needs a provider API key this offline harness deliberately doesn't
require.
