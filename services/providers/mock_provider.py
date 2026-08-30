"""Deterministic offline stand-in for a real LLM.

This is NOT a language model. It exists so the full pipeline — retrieval,
confidence gating, citation, verification, evaluation — is reproducible by
a judge on a clean machine with zero API keys (ground rule: "Give judges
enough access to run the project and reproduce the main result").

It measures the *harness's structural behavior* (does it cite evidence? does
it refuse when it should? does it avoid inventing specifics?), not answer
prose quality. See docs/evaluation.md for the distinction and instructions
to re-run with a real provider for a qualitative pass.

Behavior:
- If the prompt contains a CONTEXT block, it extractively selects the
  context lines most relevant to the question (word-overlap scoring) and
  stitches them into an answer, preserving any "[F03]"-style citation tags
  already present in the context lines.
- If the prompt contains NO context (the plain baseline), it fabricates a
  generic, confident-sounding, ungrounded answer from stock phrasing plus
  keywords borrowed from the question itself — this deliberately simulates
  the hallucination failure mode a context-free LLM call actually produces.

v3 fix: parsing used to require the final section be labeled literally
"QUESTION:" — every other caller in this codebase (v2's "REQUIREMENT:",
v2.5's "SECTION PROMPT:", v3's "FIELD LABEL:") silently fell through to
treating the *entire prompt* as both context and question, which meant the
question/label text itself could rank as an "extractable context line" and
leak verbatim into the answer. Normally invisible, because real matching
facts outscore a line that trivially matches itself — visible only when
retrieval was already weak, which is exactly when a silent bug is most
dangerous. Fixed generally: the parser no longer looks for a specific
keyword. It treats the text after the LAST blank line as the query
(stripping whatever ALL-CAPS header precedes it, whatever that header is
named) and everything before it, after the "CONTEXT:" prefix, as context —
correct for every caller, present and future, not just the ones audited
after this bug was found. See docs/hot_take.md's v3 addendum.
"""
from __future__ import annotations

import re
from hashlib import sha256

from .base import LLMProvider

_STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "in", "for", "on", "with", "is",
    "are", "you", "your", "what", "how", "why", "would", "do", "does",
    "did", "that", "this", "at", "as", "be", "or", "it", "i", "we", "us",
    "describe", "explain", "tell", "about",
}

_GENERIC_OPENERS = [
    "I have consistently demonstrated strong ability in this area.",
    "This is something I have thought about carefully throughout my career.",
    "I believe my track record speaks directly to this question.",
    "Over the years, I have built a reputation for excellence here.",
]
_GENERIC_CLOSERS = [
    "I am confident this reflects who I am professionally.",
    "This has shaped my approach to every project I take on.",
    "I look forward to bringing this strength to your organization.",
]


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def _score(context_line: str, question_tokens: set[str]) -> int:
    return len(_tokens(context_line) & question_tokens)


def _stable_pick(seed_text: str, options: list[str]) -> str:
    """Deterministic pseudo-random pick, seeded by content (never random.seed
    global state, so repeated eval runs are byte-identical)."""
    idx = int(sha256(seed_text.encode()).hexdigest(), 16) % len(options)
    return options[idx]


class MockProvider(LLMProvider):
    name = "mock"

    def complete(self, system: str, prompt: str, max_tokens: int = 600) -> str:
        if "\n\n" in prompt:
            context_part, _, query_part = prompt.rpartition("\n\n")
        else:
            context_part, query_part = "", prompt

        context = re.sub(r"^CONTEXT:\s*", "", context_part.strip(), flags=re.S).strip()
        question = re.sub(r"^[A-Z][A-Z ]*:\s*", "", query_part.strip()).strip()

        if not context:
            return self._hallucinate(question)

        return self._extractive_answer(question, context)

    def _hallucinate(self, question: str) -> str:
        q_tokens = sorted(_tokens(question))
        borrowed = " and ".join(q_tokens[:3]) if q_tokens else "this area"
        opener = _stable_pick(question, _GENERIC_OPENERS)
        closer = _stable_pick(question[::-1], _GENERIC_CLOSERS)
        return (
            f"{opener} When it comes to {borrowed}, I have always taken a "
            f"proactive, results-driven approach and delivered measurable "
            f"impact. {closer}"
        )

    def _extractive_answer(self, question: str, context: str) -> str:
        q_tokens = _tokens(question)
        lines = [ln.strip("- ").strip() for ln in context.splitlines() if ln.strip()]
        scored = sorted(
            ((_score(ln, q_tokens), i, ln) for i, ln in enumerate(lines)),
            key=lambda t: (-t[0], t[1]),
        )
        top = [ln for score, _, ln in scored[:4] if score > 0]
        if not top:
            # nothing in context matches the question at all
            top = [ln for _, _, ln in scored[:2]]
        return " ".join(top) if top else "No relevant evidence was found for this question."
