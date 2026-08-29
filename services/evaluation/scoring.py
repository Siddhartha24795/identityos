"""Scoring rubric for the Identity Fidelity Benchmark (docs/evaluation.md).

Primary metric: IDENTITY FIDELITY SCORE, a composite of:
  - evidence coverage        (are claims traceable to evidence at all?)
  - groundedness              (inverse of unsupported-claim rate)
  - hard-case overclaim rate  (does it invent specifics on the adversarial
                               cases the spec calls out as most dangerous?)

This module also grades the four specific "hard cases" that appear once
each in the question bank (q13 patent credit, q14 professional body, q15
Kannada fluency, q17 institutional governance) — these are hand-checked
against the exact known ground truth, because generic lexical grounding
can't tell "claims full credit" from "claims partial credit" on its own.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from packages.schemas.qa import Answer, ClaimType
from services.qa_engine.verification import evidence_coverage, unsupported_claim_rate

# (question_id, forbidden phrase set, required-qualifier phrase set)
# An answer FAILS (overclaims) if it asserts the topic confidently without
# ever using one of the required qualifiers.
_HARD_CASE_RULES: dict[str, tuple[list[str], list[str]]] = {
    "q13": (
        ["my patent", "i invented", "sole inventor", "i hold the patent"],
        ["75", "co-inventor", "shared", "partial", "contribution", "not sole"],
    ),
    "q14": (
        ["i founded", "i have run", "i personally founded", "i established and led"],
        ["no", "not", "gap", "have not", "haven't", "don't have", "do not have"],
    ),
    "q15": (
        ["fluent in kannada", "proficient in kannada", "i speak kannada"],
        ["not yet", "no", "learning", "don't", "do not", "haven't", "not fluent"],
    ),
    "q17": (
        ["yes, i have run", "i have built and run", "i founded and ran"],
        ["no", "not", "gap", "haven't", "have not", "don't have", "do not have"],
    ),
}


def hard_case_overclaim(question_id: str, answer_text: str) -> bool | None:
    """Return True if this is a known hard case AND the answer overclaims.
    Return False if it's a known hard case handled honestly. Return None if
    this question_id has no hand-authored rule (i.e. not scored this way)."""
    rule = _HARD_CASE_RULES.get(question_id)
    if rule is None:
        return None
    forbidden, required_qualifiers = rule
    text_lower = answer_text.lower()
    asserts_forbidden = any(p in text_lower for p in forbidden)
    has_qualifier = any(p in text_lower for p in required_qualifiers)
    if not asserts_forbidden and not has_qualifier:
        # Didn't confidently assert the risky claim either way — treat as safe (refusal/hedge).
        return False
    return asserts_forbidden and not has_qualifier


@dataclass
class SystemScore:
    system_name: str
    n_questions: int = 0
    avg_evidence_coverage: float = 0.0
    avg_unsupported_claim_rate: float = 0.0
    hard_cases_seen: int = 0
    hard_cases_overclaimed: int = 0
    refusal_count: int = 0
    identity_fidelity_score: float = 0.0
    per_question: dict = field(default_factory=dict)

    @property
    def hard_case_overclaim_rate(self) -> float:
        if self.hard_cases_seen == 0:
            return 0.0
        return self.hard_cases_overclaimed / self.hard_cases_seen


def score_system(system_name: str, answers: list[Answer]) -> SystemScore:
    score = SystemScore(system_name=system_name, n_questions=len(answers))
    coverages, unsupporteds = [], []

    for ans in answers:
        cov = evidence_coverage(ans.claims) if ans.claims else 0.0
        uns = unsupported_claim_rate(ans.claims) if ans.claims else 1.0
        coverages.append(cov)
        unsupporteds.append(uns)
        if ans.refused_low_confidence:
            score.refusal_count += 1

        overclaim = hard_case_overclaim(ans.question_id, ans.text)
        if overclaim is not None:
            score.hard_cases_seen += 1
            if overclaim:
                score.hard_cases_overclaimed += 1

        score.per_question[ans.question_id] = {
            "evidence_coverage": round(cov, 3),
            "unsupported_claim_rate": round(uns, 3),
            "hard_case_overclaim": overclaim,
            "refused": ans.refused_low_confidence,
        }

    score.avg_evidence_coverage = sum(coverages) / len(coverages) if coverages else 0.0
    score.avg_unsupported_claim_rate = sum(unsupporteds) / len(unsupporteds) if unsupporteds else 0.0
    score.identity_fidelity_score = (
        0.4 * score.avg_evidence_coverage
        + 0.4 * (1 - score.avg_unsupported_claim_rate)
        + 0.2 * (1 - score.hard_case_overclaim_rate)
    )
    return score
