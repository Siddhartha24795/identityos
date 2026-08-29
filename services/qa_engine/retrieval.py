"""Structured retrieval over the Digital Self (facts + beliefs).

v1 uses deterministic lexical overlap rather than embeddings. This is a
documented simplification (docs/roadmap.md v2 adds a vector store for
semantic recall) — but it keeps retrieval fully explainable: every
retrieved item's score is just "how many question words it shares",
which is exactly what a judge needs to audit a trajectory by hand.
"""
from __future__ import annotations

import re

from packages.schemas.identity import Belief, DigitalSelf, Confidence, Fact
from packages.schemas.qa import Question

_STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "in", "for", "on", "with", "is",
    "are", "you", "your", "what", "how", "why", "would", "do", "does",
    "did", "that", "this", "at", "as", "be", "or", "it", "i", "we", "us",
    "describe", "explain", "tell", "about", "most", "biggest",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def retrieve(
    ds: DigitalSelf, question: Question, top_k_facts: int = 6, top_k_beliefs: int = 3
) -> tuple[list[Fact], list[Belief]]:
    q_tokens = _tokens(question.text)

    scored_facts = sorted(
        ((len(_tokens(f.text) & q_tokens), f) for f in ds.facts),
        key=lambda t: -t[0],
    )
    facts = [f for score, f in scored_facts[:top_k_facts] if score > 0]

    scored_beliefs = sorted(
        ((len(_tokens(b.statement) & q_tokens), b) for b in ds.beliefs),
        key=lambda t: -t[0],
    )
    beliefs = [b for score, b in scored_beliefs[:top_k_beliefs] if score > 0]

    return facts, beliefs


def _bucket_label(bucket: Confidence) -> str:
    return bucket.value.replace("_", " ")


def format_context(facts: list[Fact], beliefs: list[Belief]) -> str:
    """Render retrieved evidence as citation-tagged lines, e.g.
    "[resume:014] (verified fact) Built VLM-based suspicious-event detection..."
    The provider is instructed to cite these ids inline; the verifier later
    checks the answer text for exactly these tags.
    """
    lines: list[str] = []
    for f in facts:
        lines.append(f"[{f.id}] ({_bucket_label(f.confidence_bucket)}) {f.text}")
    for b in beliefs:
        counter = " — counter-evidence exists, do not state this as certain" if b.counter_evidence else ""
        lines.append(
            f"[{b.id}] (belief, {_bucket_label(b.confidence_bucket)}, "
            f"confidence={b.confidence:.2f}) {b.statement}{counter}"
        )
    return "\n".join(lines)
