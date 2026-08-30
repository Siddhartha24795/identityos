"""v2.5 — Document generation schemas.

A GeneratedDocument is assembled section by section (not one monolithic
generation call) so that:
  1. each section can be independently verified (same verifier as v1/v2),
  2. the generator can track which facts/beliefs have already been used
     and deprioritize re-citing them — a concrete, testable instance of
     the original brief's APPLICATION_NARRATIVE_STATE concept (avoid the
     same three facts repeated in every paragraph).
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from packages.schemas.qa import AnswerClaim


class DocumentSection(BaseModel):
    section_name: str
    query_text: str  # the prompt used to retrieve/generate this section
    text: str
    claims: list[AnswerClaim] = Field(default_factory=list)
    evidence_coverage: float = 0.0
    overall_confidence: float = 0.0
    reused_evidence_ids: list[str] = Field(default_factory=list)  # ids cited elsewhere too


class GeneratedDocument(BaseModel):
    document_type: str  # "cover_letter"
    system_name: str  # "baseline_plain" | "baseline_rag" | "identityos_v2_5"
    sections: list[DocumentSection] = Field(default_factory=list)
    full_text: str = ""
    avg_evidence_coverage: float = 0.0
    avg_unsupported_claim_rate: float = 0.0
    repeated_evidence_rate: float = 0.0  # fraction of citations that are reused across sections
    provider: str = "mock"
    latency_ms: float = 0.0
