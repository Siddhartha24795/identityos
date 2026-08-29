"""Core identity schemas: the typed representation of a person's Digital Self.

Design rule (see /docs/architecture.md): facts, beliefs, and evidence are
distinct types. A belief is never silently promoted to a fact, and every
non-trivial claim must carry provenance and a confidence score.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Confidence(str, Enum):
    """Discrete confidence bucket. Maps to a numeric score range for policy
    decisions (e.g. "ask the user" thresholds)."""

    VERIFIED_FACT = "verified_fact"        # 0.95 - 1.00
    STRONG_INFERENCE = "strong_inference"  # 0.80 - 0.95
    MODERATE_INFERENCE = "moderate_inference"  # 0.55 - 0.80
    WEAK_INFERENCE = "weak_inference"      # 0.25 - 0.55
    UNKNOWN = "unknown"                    # 0.00 - 0.25

    @classmethod
    def from_score(cls, score: float) -> "Confidence":
        if score >= 0.95:
            return cls.VERIFIED_FACT
        if score >= 0.80:
            return cls.STRONG_INFERENCE
        if score >= 0.55:
            return cls.MODERATE_INFERENCE
        if score >= 0.25:
            return cls.WEAK_INFERENCE
        return cls.UNKNOWN


class Evidence(BaseModel):
    """A pointer back to the source material that grounds a fact or belief.
    Every Fact and Belief must resolve to at least one Evidence object."""

    id: str
    source_document: str        # e.g. "resume.pdf", "github.com/..."
    locator: Optional[str] = None  # e.g. "page 2", "line 14", "repo:readme"
    snippet: str                # the actual quoted/paraphrased text
    extracted_at: datetime = Field(default_factory=_now)


class FactCategory(str, Enum):
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    PROJECT = "project"
    PUBLICATION = "publication"
    AWARD = "award"
    SKILL = "skill"
    LOCATION = "location"
    DATE = "date"
    ORGANIZATION = "organization"
    TECHNOLOGY = "technology"
    ACHIEVEMENT = "achievement"
    OTHER = "other"


class Fact(BaseModel):
    """A verified, source-grounded statement about the person.

    Facts are the highest-trust layer. They are extracted, not inferred.
    """

    id: str
    text: str
    category: FactCategory
    evidence: list[Evidence]
    confidence: float = 0.99
    added_at: datetime = Field(default_factory=_now)

    @property
    def confidence_bucket(self) -> Confidence:
        return Confidence.from_score(self.confidence)


class Belief(BaseModel):
    """An inferred statement about the person's preferences, values, or
    tendencies. Never treated as a fact. Must carry both supporting and
    counter-evidence, and a timestamp for temporal validity (see
    docs/architecture.md - Contradiction Graph)."""

    id: str
    statement: str
    supporting_evidence: list[str] = Field(default_factory=list)  # fact/evidence ids
    counter_evidence: list[str] = Field(default_factory=list)
    confidence: float
    first_observed: datetime = Field(default_factory=_now)
    last_validated: datetime = Field(default_factory=_now)
    source_refs: list[str] = Field(default_factory=list)

    @property
    def confidence_bucket(self) -> Confidence:
        return Confidence.from_score(self.confidence)


class DigitalSelf(BaseModel):
    """The versioned computational representation of a person.

    v1 storage is a flat JSON file per version (see services/identity_engine
    /store.py). The roadmap (docs/roadmap.md) migrates this to a graph store
    once the number of edge types (SUPPORTED_BY, CONTRADICTS, ...) justifies it.
    """

    version: int
    person_name: str
    facts: list[Fact] = Field(default_factory=list)
    beliefs: list[Belief] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    source_documents: list[str] = Field(default_factory=list)

    def fact_text_blob(self) -> str:
        """Flattened text of all facts, used by the naive-RAG baseline."""
        return "\n".join(f"- {f.text}" for f in self.facts)


class DigitalSelfDiff(BaseModel):
    """A record of how the Digital Self changed between two versions.
    Required by the versioning/rollback requirement in docs/architecture.md."""

    from_version: int
    to_version: int
    added_fact_ids: list[str] = Field(default_factory=list)
    added_belief_ids: list[str] = Field(default_factory=list)
    reason: str
    created_at: datetime = Field(default_factory=_now)
