"""BASELINE 2 — LLM + naive resume RAG: dump the entire fact store as
unstructured text, no ranking, no citation ids, no confidence, no
verification. This is what "LLM + resume in the prompt" looks like in
practice, and the fairest strong baseline to compare IdentityOS against.
"""
from __future__ import annotations

import time

from packages.schemas.identity import DigitalSelf
from packages.schemas.qa import Answer, Question, Trajectory

SYSTEM_PROMPT = (
    "You are a helpful assistant. Using the background information provided, "
    "answer this application question directly, in the first person, on "
    "behalf of the applicant."
)


def answer_baseline_rag(
    question: Question, ds: DigitalSelf, provider
) -> tuple[Answer, Trajectory]:
    traj = Trajectory(question_id=question.id, system_name="baseline_rag")
    context = ds.fact_text_blob()
    traj.add(
        stage="retrieve",
        input_summary=question.text,
        action="dump the entire fact store as unstructured text (no ranking, no ids)",
        observation=f"{len(ds.facts)} facts included, no relevance filtering",
        reasoning="Baseline 2 has retrieval but no structure and no grounding check.",
    )
    prompt = f"CONTEXT:\n{context}\n\nQUESTION:\n{question.text}\n"
    t0 = time.time()
    text = provider.complete(SYSTEM_PROMPT, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=question.text,
        action="call provider with the full unstructured context dump",
        observation=text,
        decision="answered_unverified",
    )
    answer = Answer(
        question_id=question.id,
        system_name="baseline_rag",
        text=text,
        overall_confidence=1.0,  # no verification step exists to produce a real confidence
        provider=provider.name,
        latency_ms=latency,
    )
    return answer, traj
