"""v4.1 — Learning Engine schemas.

PROMPT.md's SELF-IMPROVEMENT ENGINE / META-LEARNING sections ask for:
EXPERIENCE -> HYPOTHESIS -> COUNTERFACTUAL TEST -> EVALUATION ->
PROMOTE/REJECT, storing conditional strategies ("Strategy X tends to work
under conditions A/B/C") rather than blanket rules, and explicitly warn
against trusting every successful trajectory. These schemas record that
loop as data, not just as a docstring: every candidate tried, its
train-set numbers, and why it was promoted or rejected.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ThresholdCandidate(BaseModel):
    """One hypothesis: 'use semantic retrieval instead of lexical for any
    requirement where lexical's own evidence_coverage is below this
    threshold.' The condition (lexical coverage) is observable before the
    real answer is known, unlike 'did lexical agree' — so this is a
    genuinely usable live policy, not one that cheats by peeking at ground
    truth."""

    threshold: float
    train_agreement_rate: float
    train_dangerous_overclaim_rate: float
    n_semantic_used: int
    promoted: bool
    rationale: str


class LeaveOneOutFold(BaseModel):
    held_out_requirement_id: str
    selected_threshold: float
    choice: str  # "lexical" | "semantic"
    agreed: bool
    dangerous_overclaim: bool


class LearningReport(BaseModel):
    candidates: list[ThresholdCandidate] = Field(default_factory=list)
    promoted_threshold: float | None
    per_requirement_choice: dict[str, str] = Field(default_factory=dict)
    baseline_lexical_agreement_rate: float
    baseline_hybrid_agreement_rate: float
    learned_agreement_rate: float
    learned_dangerous_overclaim_rate: float
    loo_folds: list[LeaveOneOutFold] = Field(default_factory=list)
    loo_agreement_rate: float
    loo_dangerous_overclaim_rate: float
    conclusion: str
