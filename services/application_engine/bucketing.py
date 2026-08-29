"""Bucketing rules for comparing a system-generated assessment to the real
human's own prior self-assessment. Documented and auditable rather than a
free-floating threshold buried in eval code (docs/architecture.md's
"document every simplification" rule).
"""
from __future__ import annotations

from packages.schemas.application import FitBucket, RealAssessment
from packages.schemas.qa import AnswerClaim

_REAL_TO_BUCKET = {
    RealAssessment.EXCEEDS: FitBucket.MET_OR_BETTER,
    RealAssessment.MET: FitBucket.MET_OR_BETTER,
    RealAssessment.CONFIRMED: FitBucket.MET_OR_BETTER,
    RealAssessment.PARTIAL: FitBucket.PARTIAL,
    RealAssessment.GAP: FitBucket.GAP,
}

MET_CONFIDENCE_THRESHOLD = 0.6
MET_COVERAGE_THRESHOLD = 0.6

# Lexical negation markers checked against CITED (grounded) claim text only.
# Discovered necessary via req14 (data/applications/iitacb_ceo/requirements.json):
# a claim can be perfectly grounded (high confidence, fully cited) and still
# be a negative claim ("no prior record of..."). Coverage/confidence alone
# cannot tell "well-supported yes" from "well-supported no" apart — this is
# a documented v2 limitation, not a req14-specific rule. See docs/hot_take.md.
_NEGATION_MARKERS = [
    "no prior", "not yet", "does not have", "do not have", "have not",
    "has no", "haven't", "don't have", "not equivalent", "cannot",
    "lacks", "lacking", "not been", "not a record", "not have that record",
]


def bucket_real_assessment(real: RealAssessment) -> FitBucket:
    return _REAL_TO_BUCKET[real]


def _is_negative_claim(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in _NEGATION_MARKERS)


def bucket_from_signals(
    evidence_coverage: float,
    overall_confidence: float,
    claims: list[AnswerClaim] | None = None,
) -> FitBucket:
    """Derive the system's own fit bucket purely from its verification
    signals (evidence_coverage, overall_confidence, and — critically — the
    polarity of the cited claim text) rather than asking the provider to
    self-report a label. The provider (mock or real) is not trusted to
    self-report a label; this function is the single place that decides.
    """
    if evidence_coverage <= 0.0:
        return FitBucket.GAP

    if claims:
        cited = [c for c in claims if c.evidence_refs]
        if cited:
            negative_ratio = sum(1 for c in cited if _is_negative_claim(c.text)) / len(cited)
            if negative_ratio >= 0.5:
                return FitBucket.GAP
            if negative_ratio > 0.0:
                return FitBucket.PARTIAL

    if evidence_coverage >= MET_COVERAGE_THRESHOLD and overall_confidence >= MET_CONFIDENCE_THRESHOLD:
        return FitBucket.MET_OR_BETTER
    return FitBucket.PARTIAL
