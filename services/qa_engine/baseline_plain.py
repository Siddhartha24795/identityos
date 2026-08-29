"""BASELINE 1 — one direct prompt with basic instructions, no context at all.

This is the hackathon brief's required "simple baseline": what a person gets
if they just paste the question into a chat model with no setup.
"""
from __future__ import annotations

import time

from packages.schemas.qa import Answer, Question, Trajectory

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer this application question directly, "
    "in the first person, on behalf of the applicant."
)


def answer_baseline_plain(question: Question, provider) -> tuple[Answer, Trajectory]:
    traj = Trajectory(question_id=question.id, system_name="baseline_plain")
    prompt = f"QUESTION:\n{question.text}\n"
    t0 = time.time()
    text = provider.complete(SYSTEM_PROMPT, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=question.text,
        action="call provider with zero context, zero verification",
        observation=text,
        reasoning="Baseline 1 has no retrieval and no grounding check by design.",
        decision="answered_unverified",
    )
    answer = Answer(
        question_id=question.id,
        system_name="baseline_plain",
        text=text,
        overall_confidence=1.0,  # baseline never hedges — that IS the failure mode being measured
        provider=provider.name,
        latency_ms=latency,
    )
    return answer, traj
