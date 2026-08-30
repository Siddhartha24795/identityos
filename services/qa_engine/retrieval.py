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
    ds: DigitalSelf,
    question: Question,
    top_k_facts: int = 6,
    top_k_beliefs: int = 3,
    min_shared_tokens: int = 1,
) -> tuple[list[Fact], list[Belief]]:
    """min_shared_tokens defaults to 1 (any shared non-stopword token) for
    backward compatibility. v2.8 found that a single shared token is a
    noisy inclusion bar: a fact can rank into the top-k on one incidental
    word overlap, contribute an unrelated negation marker, and wrongly
    downgrade an otherwise strong, clearly relevant answer
    (docs/evaluation_v2.md's v2.8 section). See retrieve_hybrid() for where
    a higher bar is actually used."""
    q_tokens = _tokens(question.text)

    scored_facts = sorted(
        ((len(_tokens(f.text) & q_tokens), f) for f in ds.facts),
        key=lambda t: -t[0],
    )
    facts = [f for score, f in scored_facts[:top_k_facts] if score >= min_shared_tokens]

    scored_beliefs = sorted(
        ((len(_tokens(b.statement) & q_tokens), b) for b in ds.beliefs),
        key=lambda t: -t[0],
    )
    beliefs = [b for score, b in scored_beliefs[:top_k_beliefs] if score >= min_shared_tokens]

    return facts, beliefs


def build_idf_table(ds: DigitalSelf) -> dict[str, float]:
    """Standard smoothed IDF, computed once per Digital Self (the same
    "precompute once, query many times" pattern as DigitalSelfEmbeddingIndex).

    v2.9 — the direct fix v2.8 pointed to. Raw shared-token *count* scores
    "management" (common across many facts: P&L management, power
    management, team management...) the same as "stakeholder" (rare,
    appears in exactly the fact that actually matters) — that's why a
    weakly-relevant fact could tie or beat the genuinely relevant one and
    inject an unrelated negation marker (docs/evaluation_v2.md's v2.8
    section). IDF weighting down-weights common tokens and up-weights
    distinctive ones without excluding anything or needing a hand-picked
    threshold.
    """
    docs = [_tokens(f.text) for f in ds.facts] + [_tokens(b.statement) for b in ds.beliefs]
    n = len(docs)
    df: dict[str, int] = {}
    for tokens in docs:
        for t in tokens:
            df[t] = df.get(t, 0) + 1
    return {t: math.log((n + 1) / (d + 1)) + 1 for t, d in df.items()}


def _idf_score(item_tokens: set[str], q_tokens: set[str], idf_table: dict[str, float]) -> float:
    return sum(idf_table.get(t, 1.0) for t in (item_tokens & q_tokens))


def retrieve_idf(
    ds: DigitalSelf,
    question: Question,
    idf_table: dict[str, float],
    top_k_facts: int = 6,
    top_k_beliefs: int = 3,
    min_score: float = 0.0,
) -> tuple[list[Fact], list[Belief]]:
    """Same contract as retrieve(), IDF-weighted instead of raw-count
    scored. See build_idf_table() for why."""
    q_tokens = _tokens(question.text)

    scored_facts = sorted(
        ((_idf_score(_tokens(f.text), q_tokens, idf_table), f) for f in ds.facts),
        key=lambda t: -t[0],
    )
    facts = [f for score, f in scored_facts[:top_k_facts] if score > min_score]

    scored_beliefs = sorted(
        ((_idf_score(_tokens(b.statement), q_tokens, idf_table), b) for b in ds.beliefs),
        key=lambda t: -t[0],
    )
    beliefs = [b for score, b in scored_beliefs[:top_k_beliefs] if score > min_score]

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


def retrieve_hybrid(
    ds: DigitalSelf,
    question: Question,
    index: DigitalSelfEmbeddingIndex,
    top_k_facts: int = 6,
    top_k_beliefs: int = 3,
    min_similarity: float = 0.55,
    lexical_min_shared_tokens: int = 1,
) -> tuple[list[Fact], list[Belief]]:
    """v2.4 — lexical first, semantic ONLY as a fallback when lexical finds
    nothing at all.

    This is a direct, evidence-based response to the v2.3 finding
    (docs/hot_take.md, docs/evaluation_v2.md): semantic retrieval's failure
    mode was adding noisy, topically-adjacent-but-wrong evidence to
    requirements where lexical retrieval ALREADY had good evidence (req09
    and six others) — not fixing the cases where lexical genuinely found
    nothing (req05, req10). Scoring fusion (blending both signals on every
    query) would reintroduce that same noise on every query. Falling back
    only when lexical is empty targets exactly the diagnosed failure mode
    and nothing else — verified by re-running the full 14-requirement
    comparison, not assumed from the design alone (docs/evaluation_v2.md).
    """
    facts, beliefs = retrieve(
        ds, question, top_k_facts, top_k_beliefs, min_shared_tokens=lexical_min_shared_tokens
    )
    if not facts and not beliefs:
        facts, beliefs = retrieve_semantic(
            index, question, top_k_facts, top_k_beliefs, min_similarity
        )
    return facts, beliefs


def idf_relevance_map(
    question: Question,
    idf_table: dict[str, float],
    facts: list[Fact],
    beliefs: list[Belief],
) -> dict[str, float]:
    """IDF relevance score per id, for exactly the facts/beliefs already
    retrieved for this question — the map bucket_from_signals()'s
    relevance_scores parameter expects (v2.9)."""
    q_tokens = _tokens(question.text)
    scores: dict[str, float] = {}
    for f in facts:
        scores[f.id] = _idf_score(_tokens(f.text), q_tokens, idf_table)
    for b in beliefs:
        scores[b.id] = _idf_score(_tokens(b.statement), q_tokens, idf_table)
    return scores


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
