"""Smoke tests for v2.3's embedding-retrieval pipeline. Uses the
zero-dependency HashEmbeddingProvider throughout — fastembed's real
semantic behavior is exercised by the actual eval run
(make eval-v2-semantic), not unit tests, since correctness there is a
"does it help on the real benchmark" question, not a unit-testable one.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.qa import Question, QuestionType
from services.embeddings import get_embedding_provider
from services.embeddings.hash_provider import HashEmbeddingProvider
from services.identity_engine import ingest, seed_beliefs
from services.qa_engine.retrieval import (
    DigitalSelfEmbeddingIndex,
    retrieve,
    retrieve_hybrid,
    retrieve_semantic,
)

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"


def _build_test_digital_self():
    sources = sorted(SOURCE_DIR.glob("*.md"))
    ds = ingest.build_digital_self(sources, person_name="Test", version=99)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    return ds


def test_hash_provider_is_deterministic():
    provider = HashEmbeddingProvider()
    v1 = provider.embed(["hello world"])[0]
    v2 = provider.embed(["hello world"])[0]
    assert v1 == v2


def test_hash_provider_different_text_different_vector():
    provider = HashEmbeddingProvider()
    v1, v2 = HashEmbeddingProvider().embed(["completely different topic", "smartwatch battery"])
    assert v1 != v2


def test_default_embedding_provider_is_hash():
    provider = get_embedding_provider()
    assert provider.name == "hash"


def test_retrieve_semantic_finds_lexically_identical_fact():
    """Sanity check with the hash provider: a query sharing exact
    substrings with a fact must retrieve it (this doesn't test true
    semantic matching — the hash provider can't do that — only that the
    retrieve_semantic/DigitalSelfEmbeddingIndex plumbing works end to end)."""
    ds = _build_test_digital_self()
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    q = Question(
        id="t1",
        text="Jinn Labs RTSP streams video ingestion",
        type=QuestionType.FACTUAL,
        application_context="test",
    )
    facts, _ = retrieve_semantic(index, q, min_similarity=0.05)
    assert any("Jinn Labs" in f.text or "RTSP" in f.text for f in facts)


def test_retrieve_hybrid_prefers_lexical_when_available():
    """When lexical retrieval finds something, hybrid must return exactly
    that — never let the semantic fallback override a working lexical hit
    (this is the whole point of v2.4, see docs/hot_take.md's v2.3 addendum)."""
    ds = _build_test_digital_self()
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    q = Question(
        id="t2",
        text="Jinn Labs RTSP streams video ingestion",
        type=QuestionType.FACTUAL,
        application_context="test",
    )
    lexical_facts, lexical_beliefs = retrieve(ds, q)
    hybrid_facts, hybrid_beliefs = retrieve_hybrid(ds, q, index)
    assert [f.id for f in hybrid_facts] == [f.id for f in lexical_facts]
    assert [b.id for b in hybrid_beliefs] == [b.id for b in lexical_beliefs]


def test_retrieve_hybrid_falls_back_when_lexical_empty():
    """When lexical finds nothing, hybrid must fall back to semantic
    rather than returning empty."""
    ds = _build_test_digital_self()
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    q = Question(
        id="t3",
        text="zzz nonexistent gibberish query xyz123",
        type=QuestionType.FACTUAL,
        application_context="test",
    )
    lexical_facts, lexical_beliefs = retrieve(ds, q)
    assert lexical_facts == [] and lexical_beliefs == []
    # Fallback runs; with the hash provider it may still find nothing
    # (it's not semantic), but it must not raise and must not silently
    # diverge from what retrieve_semantic itself would return.
    hybrid_facts, hybrid_beliefs = retrieve_hybrid(ds, q, index, min_similarity=0.0)
    semantic_facts, semantic_beliefs = retrieve_semantic(index, q, min_similarity=0.0)
    assert [f.id for f in hybrid_facts] == [f.id for f in semantic_facts]
    assert [b.id for b in hybrid_beliefs] == [b.id for b in semantic_beliefs]
