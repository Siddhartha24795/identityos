"""Smoke tests for v2.5's document generation pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.identity import FactCategory
from services.document_engine.generate import (
    _exclude_application_specific,
    _prefer_unused,
    generate_cover_letter_identityos,
)
from services.embeddings.hash_provider import HashEmbeddingProvider
from services.identity_engine import ingest, seed_beliefs
from services.providers import get_provider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"


def _build_test_digital_self():
    sources = sorted(SOURCE_DIR.glob("*.md"))
    ds = ingest.build_digital_self(sources, person_name="Test", version=99)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    return ds


def test_ingestion_tags_strategy_section_as_application_specific():
    ds = _build_test_digital_self()
    tagged = [f for f in ds.facts if f.category == FactCategory.APPLICATION_SPECIFIC]
    assert len(tagged) > 0
    assert any("IITACB" in f.text for f in tagged)


def test_exclude_application_specific_filters_correctly():
    ds = _build_test_digital_self()
    application_specific = [f for f in ds.facts if f.category == FactCategory.APPLICATION_SPECIFIC]
    assert application_specific  # sanity: corpus actually has some
    filtered = _exclude_application_specific(ds.facts)
    assert all(f.category != FactCategory.APPLICATION_SPECIFIC for f in filtered)
    assert len(filtered) == len(ds.facts) - len(application_specific)


def test_prefer_unused_puts_fresh_evidence_first():
    ds = _build_test_digital_self()
    facts = ds.facts[:4]
    used = {facts[0].id, facts[2].id}
    ordered_facts, _ = _prefer_unused(facts, [], used, target_facts=4)
    # the two unused facts should come before the two used ones
    ordered_ids = [f.id for f in ordered_facts]
    assert ordered_ids.index(facts[1].id) < ordered_ids.index(facts[0].id)


def test_generate_cover_letter_end_to_end_with_mock():
    ds = _build_test_digital_self()
    provider = get_provider("mock")
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    doc, traj = generate_cover_letter_identityos(ds, index, provider)
    assert doc.document_type == "cover_letter"
    assert len(doc.sections) == 4
    assert doc.full_text.strip() != ""
    assert len(traj.steps) >= 4 * 3  # retrieve+generate+verify per section
