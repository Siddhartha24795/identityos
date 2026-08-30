"""Smoke tests for v2's application-compilation pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.application import FitBucket, RealAssessment
from packages.schemas.qa import AnswerClaim, ClaimType
from services.application_engine.bucketing import (
    bucket_from_signals,
    bucket_real_assessment,
)
from services.application_engine.intent_model import load_requirements

REQUIREMENTS_PATH = REPO_ROOT / "data" / "applications" / "iitacb_ceo" / "requirements.json"


def test_requirements_load_with_real_ground_truth():
    reqs = load_requirements(REQUIREMENTS_PATH)
    assert len(reqs) == 14
    gap_reqs = [r for r in reqs if r.real_assessment == RealAssessment.GAP]
    assert len(gap_reqs) == 1
    assert "professional body" in gap_reqs[0].text.lower()


def test_bucket_real_assessment_mapping():
    assert bucket_real_assessment(RealAssessment.EXCEEDS) == FitBucket.MET_OR_BETTER
    assert bucket_real_assessment(RealAssessment.CONFIRMED) == FitBucket.MET_OR_BETTER
    assert bucket_real_assessment(RealAssessment.PARTIAL) == FitBucket.PARTIAL
    assert bucket_real_assessment(RealAssessment.GAP) == FitBucket.GAP


def test_bucket_from_signals_no_evidence_is_gap():
    assert bucket_from_signals(0.0, 0.0) == FitBucket.GAP


def test_bucket_from_signals_negation_downgrades_confident_claim():
    """Regression test for the req14 finding: a well-grounded NEGATIVE claim
    must not bucket as met_or_better just because it's well-cited."""
    negative_claim = AnswerClaim(
        text="He has no prior record of building or running a professional body.",
        evidence_refs=["dossier_excerpts:006"],
        claim_type=ClaimType.VERIFIED_FACT,
        confidence=0.99,
    )
    bucket = bucket_from_signals(
        evidence_coverage=1.0, overall_confidence=0.9, claims=[negative_claim]
    )
    assert bucket != FitBucket.MET_OR_BETTER


def test_bucket_from_signals_relevance_scores_default_is_backward_compatible():
    """v2.9 added an optional relevance_scores parameter — omitting it (the
    shipped default everywhere in services/application_engine/assess.py)
    must behave exactly as before the parameter existed."""
    claim = AnswerClaim(
        text="He has no prior record of building or running a professional body.",
        evidence_refs=["dossier_excerpts:006"],
        claim_type=ClaimType.VERIFIED_FACT,
        confidence=0.99,
    )
    without = bucket_from_signals(evidence_coverage=1.0, overall_confidence=0.9, claims=[claim])
    with_none = bucket_from_signals(
        evidence_coverage=1.0, overall_confidence=0.9, claims=[claim], relevance_scores=None
    )
    assert without == with_none == FitBucket.GAP


def test_bucket_from_signals_mixed_clause_is_partial_not_gap():
    """Regression test for the req13 finding (v2.2): a single sentence
    mixing a positive and a negative clause must bucket as PARTIAL, not
    GAP — whole-sentence negation detection previously over-penalized it."""
    mixed_claim = AnswerClaim(
        text="He is fluent in English and Hindi but not yet in Kannada.",
        evidence_refs=["dossier_excerpts:007"],
        claim_type=ClaimType.VERIFIED_FACT,
        confidence=0.99,
    )
    bucket = bucket_from_signals(
        evidence_coverage=1.0, overall_confidence=0.9, claims=[mixed_claim]
    )
    assert bucket == FitBucket.PARTIAL
