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


def test_dossier_excerpts_general_facts_do_not_name_the_committee_or_relocation_commitment():
    """Regression test for the v2.7 fix, scoped to the source file it
    fixed: general facts from dossier_excerpts.md must not reference "the
    committee" (IITACB's Managing Committee) or frame relocation/Kannada
    learning as a commitment made for a specific role — that content
    belongs in the separately-tagged APPLICATION_SPECIFIC facts."""
    ds = _build_test_digital_self()
    general_excerpt_facts = [
        f for f in ds.facts
        if f.id.startswith("dossier_excerpts:")
        and f.category != FactCategory.APPLICATION_SPECIFIC
    ]
    assert general_excerpt_facts  # sanity
    offending = [
        f for f in general_excerpt_facts
        if "committee" in f.text.lower() or "relocat" in f.text.lower()
    ]
    assert offending == [], f"application-specific framing leaked into general facts: {offending}"


def test_prefer_unused_puts_fresh_evidence_first():
    ds = _build_test_digital_self()
    facts = ds.facts[:4]
    used = {facts[0].id, facts[2].id}
    ordered_facts, _ = _prefer_unused(facts, [], used, target_facts=4)
    # the two unused facts should come before the two used ones
    ordered_ids = [f.id for f in ordered_facts]
    assert ordered_ids.index(facts[1].id) < ordered_ids.index(facts[0].id)


def test_dossier_narrative_general_facts_do_not_name_the_secretariat():
    """Regression test for the v2.6 fix, scoped to the source file it fixed:
    a general capability fact from dossier_narrative.md must not carry a
    comparison to "a/the Secretariat" (IITACB's, capitalized in the source
    as a proper reference) baked into its text — that belongs in a
    separately-tagged APPLICATION_SPECIFIC fact. Note: "secretariat" is a
    legitimate general term elsewhere in the corpus (e.g. "Cabinet
    Secretariat", a real government body) — this test only checks the one
    source file where the conflation bug actually was."""
    ds = _build_test_digital_self()
    general_narrative_facts = [
        f for f in ds.facts
        if f.id.startswith("dossier_narrative:")
        and f.category != FactCategory.APPLICATION_SPECIFIC
    ]
    assert general_narrative_facts  # sanity: the file actually contributed general facts
    offending = [f for f in general_narrative_facts if "secretariat" in f.text.lower()]
    assert offending == [], f"role-specific framing leaked into general facts: {offending}"


def test_generate_cover_letter_end_to_end_with_mock():
    ds = _build_test_digital_self()
    provider = get_provider("mock")
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    doc, traj = generate_cover_letter_identityos(ds, index, provider)
    assert doc.document_type == "cover_letter"
    assert len(doc.sections) == 4
    assert doc.full_text.strip() != ""
    assert len(traj.steps) >= 4 * 3  # retrieve+generate+verify per section
