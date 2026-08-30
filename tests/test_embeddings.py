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
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex, retrieve_semantic

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
