"""Structured retrieval over the Digital Self (facts + beliefs).

v1 uses deterministic lexical overlap rather than embeddings. This is a
documented simplification — but it keeps retrieval fully explainable:
every retrieved item's score is just "how many question words it shares",
which is exactly what a judge needs to audit a trajectory by hand.

v2.3 adds `retrieve_semantic()`: the same signature and return shape, but
ranked by embedding cosine similarity instead of word overlap, so the two
are directly comparable rather than one silently replacing the other
(docs/roadmap.md v2.3).
"""
from __future__ import annotations

import math
import re

from packages.schemas.identity import Belief, DigitalSelf, Confidence, Fact
from packages.schemas.qa import Question
from services.embeddings.base import EmbeddingProvider

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


class DigitalSelfEmbeddingIndex:
    """Precomputed embeddings for every fact/belief in a Digital Self,
    computed once per eval run (not per query) — the realistic pattern for
    a vector index, at a scale (tens to low hundreds of facts) that doesn't
    yet justify an actual vector database (docs/roadmap.md v5)."""

    def __init__(self, ds: DigitalSelf, provider: EmbeddingProvider):
        self.facts = ds.facts
        self.beliefs = ds.beliefs
        texts = [f.text for f in ds.facts] + [b.statement for b in ds.beliefs]
        vectors = provider.embed(texts) if texts else []
        n_facts = len(ds.facts)
        self._fact_vecs = vectors[:n_facts]
        self._belief_vecs = vectors[n_facts:]
        self._provider = provider

    def query(self, question_text: str) -> list[float]:
        return self._provider.embed([question_text])[0]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na > 0 and nb > 0 else 0.0


def retrieve_semantic(
    index: DigitalSelfEmbeddingIndex,
    question: Question,
    top_k_facts: int = 6,
    top_k_beliefs: int = 3,
    min_similarity: float = 0.55,
) -> tuple[list[Fact], list[Belief]]:
    """Same contract as retrieve(): returns (facts, beliefs) ranked by
    relevance, consumable by format_context() unmodified. min_similarity is
    an empirically-set cutoff for BAAI/bge-small-en-v1.5 (see
    docs/evaluation_v2.md for the calibration) — a real embedding model's
    cosine similarities don't hit ~0 for unrelated text the way lexical
    overlap does, so an explicit threshold is what preserves "no relevant
    evidence" as a real, reachable outcome rather than always returning
    top-k regardless of relevance.
    """
    q_vec = index.query(question.text)

    scored_facts = sorted(
        ((_cosine(q_vec, v), f) for v, f in zip(index._fact_vecs, index.facts)),
        key=lambda t: -t[0],
    )
    facts = [f for score, f in scored_facts[:top_k_facts] if score >= min_similarity]

    scored_beliefs = sorted(
        ((_cosine(q_vec, v), b) for v, b in zip(index._belief_vecs, index.beliefs)),
        key=lambda t: -t[0],
    )
    beliefs = [b for score, b in scored_beliefs[:top_k_beliefs] if score >= min_similarity]

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
