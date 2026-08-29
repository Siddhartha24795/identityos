"""IdentityOS v1 — the core "unseen question reasoning" pipeline.

QUESTION -> QUESTION TYPE (v1: declared, not classified) -> STRUCTURED
RETRIEVAL -> CITATION-GROUNDED GENERATION -> CLAIM VERIFICATION ->
CONFIDENCE-GATED REFUSAL POLICY -> FINAL ANSWER

Every step is written to a Trajectory (see docs/ trajectory deliverable).
This module is the "System" arm compared against baseline_plain and
baseline_rag in services/evaluation/run_eval.py.
"""
from __future__ import annotations

import time

from packages.schemas.identity import DigitalSelf
from packages.schemas.qa import Answer, Question, QuestionType, Trajectory
from services.qa_engine.retrieval import format_context, retrieve
from services.qa_engine.verification import (
    evidence_coverage,
    unsupported_claim_rate,
    verify_answer,
)

SYSTEM_PROMPT = (
    "You are IdentityOS, an autonomous representative answering an application "
    "question on behalf of a specific person. Use ONLY the evidence lines given "
    "below, each tagged with an id like [resume:014] or [belief:001]. Cite the "
    "ids you rely on inline, in brackets, next to the sentence they support. "
    "Do not invent employment, degrees, publications, awards, or personal "
    "motivations that are not in the evidence. If a belief line says "
    "counter-evidence exists, do not state it as a certainty. If evidence "
    "about joint work specifies a partial contribution, do not claim full or "
    "sole credit."
)

REFUSAL_THRESHOLD = 0.5
# Question types where an ungrounded, overconfident answer is most costly —
# these are gated by REFUSAL_THRESHOLD; purely factual lookups are not.
SUBJECTIVE_TYPES = {
    QuestionType.UNSEEN_INFERENTIAL,
    QuestionType.ADVERSARIAL,
    QuestionType.CONTRADICTORY,
}


def answer_identityos(
    question: Question, ds: DigitalSelf, provider
) -> tuple[Answer, Trajectory]:
    traj = Trajectory(question_id=question.id, system_name="identityos_v1")

    # 1. classify — v1 simplification: trust the caller-declared type rather
    # than running a separate classifier model (see docs/roadmap.md v2).
    traj.add(
        stage="classify",
        input_summary=question.text,
        action="use declared question.type (v1 simplification, not a learned classifier)",
        observation=question.type.value,
        reasoning="v2 replaces this with an automatic classifier over question text alone.",
    )

    # 2. retrieve
    facts, beliefs = retrieve(ds, question)
    context = format_context(facts, beliefs)
    traj.add(
        stage="retrieve",
        input_summary=question.text,
        action=f"lexical retrieval over Digital Self: top {len(facts)} facts, {len(beliefs)} beliefs",
        observation=context or "(no matching evidence found)",
    )

    # 3. generate
    prompt = f"CONTEXT:\n{context}\n\nQUESTION:\n{question.text}\n"
    t0 = time.time()
    raw_text = provider.complete(SYSTEM_PROMPT, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=question.text,
        action="call provider with structured, citation-tagged, confidence-annotated context",
        observation=raw_text,
    )

    # 4. verify
    claims, overall_confidence = verify_answer(raw_text, facts, beliefs)
    coverage = evidence_coverage(claims)
    unsupported = unsupported_claim_rate(claims)
    traj.add(
        stage="verify",
        input_summary=raw_text,
        action="check every sentence for an explicit citation, else a lexical grounding match",
        observation=(
            f"evidence_coverage={coverage:.2f} "
            f"unsupported_claim_rate={unsupported:.2f} "
            f"overall_confidence={overall_confidence:.2f}"
        ),
        confidence=overall_confidence,
    )

    # 5. refusal policy
    refused = False
    final_text = raw_text
    if question.type in SUBJECTIVE_TYPES and overall_confidence < REFUSAL_THRESHOLD:
        refused = True
        best_hint = context.splitlines()[0] if context else "no matching evidence was retrieved."
        final_text = (
            "I don't have grounded evidence in the Digital Self to answer this "
            "confidently or consistently with prior answers. In a live deployment "
            "this would pause and ask the user directly rather than guess "
            f"(see docs/architecture.md - Uncertainty policy). Closest evidence found: {best_hint}"
        )
        traj.add(
            stage="recover",
            input_summary=raw_text,
            action="apply refusal policy: subjective question type + confidence below threshold",
            observation=final_text,
            reasoning="Never let a low-confidence subjective answer through unhedged.",
            confidence=overall_confidence,
            decision="refuse_and_hedge",
        )

    answer = Answer(
        question_id=question.id,
        system_name="identityos_v1",
        text=final_text,
        claims=claims,
        overall_confidence=overall_confidence,
        refused_low_confidence=refused,
        latency_ms=latency,
        provider=provider.name,
    )
    traj.add(
        stage="complete",
        input_summary=question.id,
        action="return final answer",
        observation=final_text,
        confidence=overall_confidence,
        decision="refused" if refused else "answered",
    )
    return answer, traj
