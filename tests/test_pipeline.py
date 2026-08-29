"""Smoke tests for the v1 pipeline. Not a substitute for the Identity
Fidelity Benchmark (services/evaluation) — these just guarantee the plumbing
works from a clean environment, which reproducibility scoring depends on.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.identity import Confidence
from packages.schemas.qa import Question, QuestionType
from services.identity_engine import ingest, seed_beliefs
from services.providers import get_provider
from services.providers.mock_provider import MockProvider
from services.qa_engine.identityos_agent import answer_identityos
from services.qa_engine.retrieval import retrieve
from services.qa_engine.verification import verify_answer

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"


def _build_test_digital_self():
    sources = sorted(SOURCE_DIR.glob("*.md"))
    ds = ingest.build_digital_self(sources, person_name="Test", version=99)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    return ds


def test_ingestion_produces_facts_with_provenance():
    ds = _build_test_digital_self()
    assert len(ds.facts) > 20
    for fact in ds.facts[:5]:
        assert fact.evidence, f"fact {fact.id} has no evidence"
        assert fact.evidence[0].source_document


def test_confidence_bucketing():
    assert Confidence.from_score(0.99) == Confidence.VERIFIED_FACT
    assert Confidence.from_score(0.10) == Confidence.UNKNOWN


def test_mock_provider_is_deterministic():
    provider = MockProvider()
    out1 = provider.complete("sys", "CONTEXT:\n[f:1] hello world\n\nQUESTION:\nhello?\n")
    out2 = provider.complete("sys", "CONTEXT:\n[f:1] hello world\n\nQUESTION:\nhello?\n")
    assert out1 == out2


def test_retrieval_finds_relevant_fact():
    ds = _build_test_digital_self()
    q = Question(
        id="t1",
        text="What did you build at Jinn Labs for video ingestion?",
        type=QuestionType.FACTUAL,
        application_context="test",
    )
    facts, _ = retrieve(ds, q)
    assert any("Jinn Labs" in f.text or "RTSP" in f.text for f in facts)


def test_verification_flags_unsupported_sentence():
    claims, overall = verify_answer(
        "This sentence has no citation and shares no words with any evidence at all.",
        facts=[],
        beliefs=[],
    )
    assert overall == 0.0
    assert all(c.claim_type.value == "unsupported" for c in claims)


def test_identityos_agent_end_to_end_with_mock_provider():
    ds = _build_test_digital_self()
    provider = get_provider("mock")
    q = Question(
        id="t2",
        text="What patent have you filed related to generative AI video codecs?",
        type=QuestionType.FACTUAL,
        application_context="test",
    )
    answer, traj = answer_identityos(q, ds, provider)
    assert answer.provider == "mock"
    assert len(traj.steps) >= 4
    assert "202511076834" in answer.text
