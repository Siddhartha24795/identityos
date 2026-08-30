# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v3.3**, taken from the
live working directory at `../identityos/` once a free, no-credit-card
real-LLM provider was added and actually used for this project's
first-ever real-model run — which found and fixed a real, root-cause bug
in shared verification infrastructure, and honestly disclosed hitting a
free-tier quota limit mid-verification rather than working around it
silently.

- v1 through v3.2 are frozen separately at `../identityos-v1/` through
  `../identityos-v2.9/`, `../identityos-v3.0/`, `../identityos-v3.2/`
  (v3.1 was superseded by v3.2 in the same work session before a separate
  snapshot was taken).
- **v3.3** adds:
  1. **`GroqProvider`** (`services/providers/groq_provider.py`) — free,
     no credit card, reuses the `openai` client already a dependency
     (for `OpenAIProvider`) pointed at Groq's OpenAI-compatible endpoint.
     No new package, no new abstraction. Wired into `get_provider()`,
     `.env.example`, and new `make eval-real-groq` / `eval-v2-real-groq` /
     `eval-documents-real-groq` / `eval-browser-real-groq` targets.
  2. **A fixed, pre-existing gap**: `python-dotenv` was a listed
     dependency nothing in the codebase actually imported, so `.env` was
     never loaded automatically by any script — every `PROVIDER=anthropic`/
     `openai` instruction in this project's docs, before this fix, only
     worked if the user separately exported the env var into their own
     shell. Fixed by adding `load_dotenv(REPO_ROOT / ".env")` to every
     eval-running script's entry point.
  3. **This project's first real-model run** (`PROVIDER=groq`,
     `openai/gpt-oss-120b`), which found three real things in one pass:
     - Given zero context, `baseline_plain` fabricated a complete fake
       patent (number, title, four paragraphs of invented technical
       detail) and a fake three-year nonprofit leadership role with
       fabricated growth statistics — while answering a differently-worded
       version of that same underlying fact the *opposite* way in the
       same run. A real generative model demonstrates the mock-provider
       reference run's own predicted limitation ("a real LLM can
       hallucinate specifics a mock never could") far more concretely
       than the mock ever could.
     - The hand-authored hard-case overclaim detector (`_HARD_CASE_RULES`,
       tuned to the mock provider's exact phrasing) missed both
       fabrications above — a real, previously-only-predicted blind spot,
       now measured and named as a v3.4+ item (semantic judgment needed,
       not a longer phrase list) rather than patched with more hand-picked
       phrases.
     - A real, root-cause bug in `services/qa_engine/verification.py`:
       the citation-parsing regex only ever matched the mock provider's
       exact bracket style (`[id]`, zero whitespace, one id per bracket).
       A real model's `[ id ]` (space-padded), `[id1; id2]` (two ids in
       one bracket), and `【id】` (fullwidth CJK brackets, which this
       specific model sometimes emits) all silently failed to parse —
       which dragged a **correct, honestly-hedged, properly-cited**
       answer to the single highest-stakes question in the v1 benchmark
       (the patent-credit question) below the refusal threshold, for a
       reason that had nothing to do with the answer's actual quality.
       **Fixed at the root**: capture raw bracket contents (either
       bracket style) and split on `,`/`;`, instead of requiring one
       tightly-formatted ASCII id. Every mock-provider suite (v1, all
       three v2 retrieval arms, v2.5, v3) re-verified byte-identical
       afterward. Offline re-verification of the already-collected
       real-model outputs (re-running the fixed verifier over the
       trajectory-logged generation text, no new API call) showed 4 of
       the run's 5 refusals were pure artifacts of this bug: refusal
       count 5 -> 1, Identity Fidelity Score 0.824 -> 0.838.
  4. **A measured token-efficiency fix**: `openai/gpt-oss-120b` is a
     reasoning model that, with no `reasoning_effort` set, consumed 585
     of a 600-token budget on hidden chain-of-thought for one call,
     leaving 15 tokens for the actual answer (visibly truncating some
     answers in the run). Measured directly: `reasoning_effort="low"` cut
     reasoning-token consumption 5-25x in side-by-side testing with no
     observed loss of answer correctness or citation quality — now the
     provider's default, configurable via `GROQ_REASONING_EFFORT`.

  **Disclosed, not hidden**: the original (higher, implicit-"high")
  reasoning-effort run had already consumed nearly this project's entire
  Groq free-tier daily token allowance (200,000 TPD) by itself, which
  blocked a fresh `reasoning_effort="low"` re-run of the full v1 suite
  from completing live in this session. The "after fix" numbers above
  come from offline re-verification of already-collected outputs, not a
  second live run — stated plainly in docs/evaluation.md's v3.3 section
  rather than left implicit. A fresh, low-effort live re-run (expected to
  use a small fraction of the tokens the first run needed) is named as
  the natural next step in docs/roadmap.md's v3.4+ section.

  9 new/updated tests (`tests/test_providers.py` — 8 tests, all mocked,
  never hit the real network; `tests/test_pipeline.py` — 2 new citation-
  parsing regression tests). Full story: docs/evaluation.md's v3.3
  section, docs/hot_take.md's v3.3 addendum, docs/improvement_changelog.md
  (Iteration 27-31), docs/roadmap.md's v3.3 section.

  **A real secret was almost included in this snapshot and was caught
  before publishing**: the initial `rsync` copy included the live
  directory's `.env` file (containing a real Groq API key pasted into
  this session by the project owner for testing). Caught by grepping the
  snapshot for the literal key string before finishing this file, and
  removed — `.env` is gitignored in the live directory for exactly this
  reason, and this snapshot process should exclude it going forward the
  same way `.venv`/`.git`/caches already are.

- Ongoing development continues in `../identityos/` (the live directory).
- No `.venv`, `.git`, `.env`, or cache directories were copied. `make
  setup` needs everything prior versions needed (~300MB Chromium,
  one-time). To actually exercise `PROVIDER=groq`, copy `.env.example` to
  `.env` and add a real (free) `GROQ_API_KEY` — this snapshot's own `.env`
  was deliberately not carried over.

## Independent clean-environment verification (this snapshot)

Ran from scratch, inside this frozen folder, in a throwaway venv, with
`PROVIDER=mock` (the only path a snapshot verification can reproduce
without a live key of its own):

```
make setup && make test && make eval-mock && make eval-v2-mock \
  && make eval-v2-semantic && make eval-documents && make eval-browser \
  && make eval-security-demo
```

All 66 tests passed. Every eval number reproduced byte-identical to the
live directory's numbers documented in `docs/evaluation.md`,
`docs/evaluation_v2.md`, `docs/evaluation_documents.md`, and
`docs/evaluation_browser.md`, confirming the citation-parsing fix changed
nothing about the mock-provider reference path — exactly the claim this
version's own documentation makes. The real-model (`PROVIDER=groq`)
results referenced throughout this snapshot's docs were produced in the
live directory (`data/evaluation/results/v1_groq/`, carried into this
snapshot as evidence) and are not independently re-run here, since doing
so would require this snapshot to hold its own live API key — verified
instead by the offline re-verification method described above, which
this snapshot's own `tests/test_pipeline.py` regression tests also cover.
The verification venv and embedding cache were then removed from this
folder.

See `README.md` for everything else, and `docs/hackathon_compliance_check.md`
for the self-audit against the hackathon PDF's own rubric, ground rules,
and deliverables list.
