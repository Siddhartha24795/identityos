"""Bucketing rules for comparing a system-generated assessment to the real
human's own prior self-assessment. Documented and auditable rather than a
free-floating threshold buried in eval code (docs/architecture.md's
"document every simplification" rule).
"""
from __future__ import annotations

import re

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

# v2.2 — clause-level split. A single sentence can carry both a positive
# and a negative clause ("fluent in English and Hindi but not yet in
# Kannada") — req13 (data/applications/iitacb_ceo/requirements.json) showed
# that whole-sentence negation detection treats such a sentence as fully
# negative, when the honest read is "mixed" (-> PARTIAL, not GAP). Splitting
# only on unambiguous contrastive conjunctions — never on bare "yet", which
# already does double duty inside the "not yet" negation marker above.
_CLAUSE_SPLIT_RE = re.compile(r"\s+but\s+|;\s*|\s+however\s+|\s+though\s+|\s+while\s+", re.IGNORECASE)


def bucket_real_assessment(real: RealAssessment) -> FitBucket:
    return _REAL_TO_BUCKET[real]


def _is_negative_claim(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in _NEGATION_MARKERS)


def _split_clauses(text: str) -> list[str]:
    return [c.strip() for c in _CLAUSE_SPLIT_RE.split(text) if c.strip()]


def _claim_polarity(text: str) -> str:
    """"negative" if every clause is negative, "positive" if none are,
    "mixed" if the claim contains both."""
    flags = [_is_negative_claim(clause) for clause in _split_clauses(text)]
    if not flags:
        return "positive"
    if all(flags):
        return "negative"
    if any(flags):
        return "mixed"
    return "positive"


RELEVANCE_DOMINANCE_RATIO = 0.5


def _claim_relevance(claim: AnswerClaim, relevance_scores: dict[str, float]) -> float:
    """A claim can cite multiple ids; use the strongest one — "is at least
    one of this claim's citations a genuinely strong match," not the
    average, since a claim naming one weak and one strong id is still as
    trustworthy as the strong id alone."""
    scores = [relevance_scores.get(ref, 0.0) for ref in claim.evidence_refs]
    return max(scores) if scores else 0.0


def bucket_from_signals(
    evidence_coverage: float,
    overall_confidence: float,
    claims: list[AnswerClaim] | None = None,
    relevance_scores: dict[str, float] | None = None,
) -> FitBucket:
    """Derive the system's own fit bucket purely from its verification
    signals (evidence_coverage, overall_confidence, and — critically — the
    polarity of the cited claim text) rather than asking the provider to
    self-report a label. The provider (mock or real) is not trusted to
    self-report a label; this function is the single place that decides.

    v2.9 — relevance_scores (retrieval score per evidence id, e.g. from
    services/qa_engine/retrieval.py's IDF scoring) is optional and, when
    provided, gates which negative/mixed claims are allowed to trigger a
    downgrade: only a claim whose strongest citation scores at least
    RELEVANCE_DOMINANCE_RATIO of the best-scoring citation anywhere in this
    context counts toward negative_ratio. This directly targets the v2.8
    finding — a fact sharing one weak, incidental token with the question
    could out-vote (or tie) the actual intended evidence purely by being
    negatively phrased. Facts, claims, or context with no relevance_scores
    provided fall back to the original v2.2 behavior exactly (every cited
    claim counted equally) — fully backward compatible.
    """
    if evidence_coverage <= 0.0:
        return FitBucket.GAP

    if claims:
        cited = [c for c in claims if c.evidence_refs]
        if cited:
            if relevance_scores:
                best_score = max(
                    (relevance_scores.get(ref, 0.0) for c in cited for ref in c.evidence_refs),
                    default=0.0,
                )
                dominant = [
                    c for c in cited
                    if best_score <= 0
                    or _claim_relevance(c, relevance_scores) >= RELEVANCE_DOMINANCE_RATIO * best_score
                ]
                voting_claims = dominant or cited
            else:
                voting_claims = cited

            polarities = [_claim_polarity(c.text) for c in voting_claims]
            negative_ratio = polarities.count("negative") / len(voting_claims)
            mixed_count = polarities.count("mixed")
            if negative_ratio >= 0.5:
                return FitBucket.GAP
            if negative_ratio > 0.0 or mixed_count > 0:
                return FitBucket.PARTIAL

    if evidence_coverage >= MET_COVERAGE_THRESHOLD and overall_confidence >= MET_CONFIDENCE_THRESHOLD:
        return FitBucket.MET_OR_BETTER
    return FitBucket.PARTIAL
