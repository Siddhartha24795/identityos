"""Question-answering and trajectory schemas.

These are shared by the two baselines and the IdentityOS system so that the
evaluation harness (services/evaluation) can score all three with one
comparable representation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class QuestionType(str, Enum):
    FACTUAL = "factual"                # directly answerable from a single fact
    UNSEEN_INFERENTIAL = "unseen"       # never answered before, requires reasoning
    AMBIGUOUS = "ambiguous"             # underspecified, multiple valid readings
    ADVERSARIAL = "adversarial"         # invites fabrication / overclaiming
    CONTRADICTORY = "contradictory"     # tests handling of conflicting beliefs
    LONG_HORIZON = "long_horizon"       # requires synthesizing across many sources


class Question(BaseModel):
    id: str
    text: str
    type: QuestionType
    application_context: str  # e.g. "Research internship application, short-answer field"
    max_words: Optional[int] = None
    notes: str = ""  # why this question is in the bank / what it tests


class ClaimType(str, Enum):
    VERIFIED_FACT = "verified_fact"
    STRONG_INFERENCE = "strong_inference"
    WEAK_INFERENCE = "weak_inference"
    UNSUPPORTED = "unsupported"  # flagged by verification, no grounding found


class AnswerClaim(BaseModel):
    """One atomic claim extracted from a generated answer, for verification."""

    text: str
    evidence_refs: list[str] = Field(default_factory=list)
    claim_type: ClaimType = ClaimType.UNSUPPORTED
    confidence: float = 0.0


class Answer(BaseModel):
    question_id: str
    system_name: str  # "baseline_plain" | "baseline_rag" | "identityos_v1"
    text: str
    claims: list[AnswerClaim] = Field(default_factory=list)
    overall_confidence: float = 0.0
    refused_low_confidence: bool = False
    latency_ms: float = 0.0
    provider: str = "mock"
    created_at: datetime = Field(default_factory=_now)


class TrajectoryStep(BaseModel):
    timestamp: datetime = Field(default_factory=_now)
    stage: str            # e.g. "retrieve", "classify", "generate", "verify"
    input_summary: str
    action: str
    observation: str
    reasoning: str = ""
    confidence: Optional[float] = None
    decision: str = ""


class Trajectory(BaseModel):
    question_id: str
    system_name: str
    steps: list[TrajectoryStep] = Field(default_factory=list)

    def add(self, **kwargs) -> None:
        self.steps.append(TrajectoryStep(**kwargs))

    def to_markdown(self) -> str:
        lines = [f"### Trajectory — {self.system_name} — {self.question_id}", ""]
        for s in self.steps:
            lines.append(f"**{s.timestamp.strftime('%H:%M:%S')} · {s.stage}**")
            lines.append(f"- input: {s.input_summary}")
            lines.append(f"- action: {s.action}")
            lines.append(f"- observation: {s.observation}")
            if s.reasoning:
                lines.append(f"- reasoning: {s.reasoning}")
            if s.confidence is not None:
                lines.append(f"- confidence: {s.confidence:.2f}")
            if s.decision:
                lines.append(f"- decision: {s.decision}")
            lines.append("")
        return "\n".join(lines)
