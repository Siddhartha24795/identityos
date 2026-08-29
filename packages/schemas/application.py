"""v2 — Application compilation schemas.

An ApplicationRequirement is one row of a real job description, paired with
the REAL HUMAN's own prior self-assessment and evidence — this is the
"REAL HUMAN ANSWER vs IDENTITYOS ANSWER" ground truth the original design
brief calls for (docs/roadmap.md v2), which v1's benchmark did not have.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from packages.schemas.qa import AnswerClaim


class RealAssessment(str, Enum):
    """The human's own original self-assessment label, exactly as written in
    the source dossier. Kept at full granularity for display; bucketed via
    bucket_real_assessment() (services/application_engine/bucketing.py) for
    scoring, since EXCEEDS/MET/CONFIRMED are not meaningfully separable from
    outside evidence alone."""

    EXCEEDS = "exceeds"
    MET = "met"
    CONFIRMED = "confirmed"   # commitment-type requirement (e.g. relocation)
    PARTIAL = "partial"
    GAP = "gap"


class FitBucket(str, Enum):
    """3-way bucket used for scoring agreement between the system's derived
    label and the human's real label."""

    MET_OR_BETTER = "met_or_better"
    PARTIAL = "partial"
    GAP = "gap"


class ApplicationRequirement(BaseModel):
    id: str
    text: str
    category: str = ""
    real_assessment: RealAssessment
    real_evidence_summary: str  # the human's own words — ground truth, not fabricated
    notes: str = ""


class Assessment(BaseModel):
    """One system's generated fit assessment for one requirement."""

    requirement_id: str
    system_name: str  # "baseline_plain" | "baseline_rag" | "identityos_v2"
    text: str
    claims: list[AnswerClaim] = Field(default_factory=list)
    overall_confidence: float = 0.0
    evidence_coverage: float = 0.0
    system_bucket: FitBucket = FitBucket.GAP
    provider: str = "mock"
    latency_ms: float = 0.0
