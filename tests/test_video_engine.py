"""v4.2 — video statement script generation + optional narrated-draft
rendering. Render tests that need real pico2wave/ffmpeg skip cleanly when
those optional system tools aren't installed, so `make test` never
requires them."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.document import DocumentSection, GeneratedDocument
from services.embeddings.hash_provider import HashEmbeddingProvider
from services.identity_engine import ingest, seed_beliefs
from services.providers.mock_provider import MockProvider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex
from services.video_engine.generate import (
    generate_video_statement_baseline_plain,
    generate_video_statement_baseline_rag,
    generate_video_statement_identityos,
)
from services.video_engine.render import DISCLOSURE_BANNER, _clean_for_narration, render_narrated_draft

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"


def _build_test_digital_self():
    sources = sorted(SOURCE_DIR.glob("*.md"))
    ds = ingest.build_digital_self(sources, person_name="Test", version=99)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    return ds


def test_baseline_plain_has_zero_evidence_coverage():
    provider = MockProvider()
    doc, traj = generate_video_statement_baseline_plain(provider)
    assert doc.document_type == "video_statement"
    assert len(doc.sections) == 4
    assert doc.avg_evidence_coverage == 0.0
    assert traj.system_name == "baseline_plain"


def test_identityos_video_cites_real_evidence():
    ds = _build_test_digital_self()
    provider = MockProvider()
    idx = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    doc, traj = generate_video_statement_identityos(ds, idx, provider)
    assert doc.system_name == "identityos_video_v4_2"
    assert len(doc.sections) == 4
    assert doc.avg_evidence_coverage > 0.0  # at least some sections found real evidence
    all_refs = [ref for s in doc.sections for c in s.claims for ref in c.evidence_refs]
    assert all_refs  # at least one citation somewhere across the script


def test_identityos_video_excludes_application_specific_facts():
    # Same guardrail as the cover letter (v2.6/v2.7): a generic video
    # statement must not draw on strategy narrative written for one
    # specific prior application.
    ds = _build_test_digital_self()
    provider = MockProvider()
    idx = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    doc, _ = generate_video_statement_identityos(ds, idx, provider)
    full_text = doc.full_text
    assert "IITACB" not in full_text


def test_clean_for_narration_strips_citations_and_dashes():
    text = "[resume:014] I ship things -- fast, and I mean it — always."
    cleaned = _clean_for_narration(text)
    assert "[resume:014]" not in cleaned
    assert "--" not in cleaned
    assert "—" not in cleaned
    assert cleaned == "I ship things, fast, and I mean it, always."


def _make_tiny_document() -> GeneratedDocument:
    return GeneratedDocument(
        document_type="video_statement",
        system_name="identityos_video_v4_2",
        sections=[
            DocumentSection(
                section_name="introduction", query_text="q",
                text="[resume:001] I build things.", evidence_coverage=1.0, overall_confidence=0.9,
            ),
        ],
        full_text="[resume:001] I build things.",
    )


@pytest.mark.skipif(
    shutil.which("pico2wave") is None or shutil.which("ffmpeg") is None,
    reason="render_narrated_draft needs pico2wave + ffmpeg, both optional system tools",
)
def test_render_narrated_draft_produces_a_real_mp4_with_disclosure(tmp_path):
    doc = _make_tiny_document()
    result = render_narrated_draft(doc, tmp_path, "unit_test")
    out = Path(result["output_path"])
    assert out.exists()
    assert out.stat().st_size > 1000  # a real video file, not an empty stub
    assert result["disclosure"] == DISCLOSURE_BANNER
    assert result["n_sections"] == 1


def test_render_narrated_draft_raises_clear_error_when_pico2wave_missing(tmp_path, monkeypatch):
    import services.video_engine.render as render_mod

    monkeypatch.setattr(render_mod.shutil, "which", lambda name: None)
    doc = _make_tiny_document()
    with pytest.raises(RuntimeError, match="pico2wave"):
        render_narrated_draft(doc, tmp_path, "unit_test")
