"""v2 — the three requirement-fit assessors, mirroring v1's three Q&A
systems exactly (services/qa_engine/{baseline_plain,baseline_rag,
identityos_agent}.py): same retrieval/verification machinery, reused
rather than reimplemented. Only the context each system is given differs.
Returns (Assessment, Trajectory) — same trajectory schema as v1, so the
same to_markdown() rendering and viewer work unmodified.
"""
from __future__ import annotations

import time

from packages.schemas.application import Assessment, ApplicationRequirement
from packages.schemas.identity import DigitalSelf
from packages.schemas.qa import Question, QuestionType, Trajectory
from services.application_engine.bucketing import bucket_from_signals
from services.qa_engine.retrieval import (
    DigitalSelfEmbeddingIndex,
    format_context,
    retrieve,
    retrieve_semantic,
)
from services.qa_engine.verification import evidence_coverage, verify_answer

SYSTEM_PROMPT_PLAIN = (
    "You are a helpful assistant. Assess, in the first person, how well the "
    "candidate meets this job requirement. Be direct and confident."
)
SYSTEM_PROMPT_RAG = (
    "You are a helpful assistant. Using the background information provided, "
    "assess in the first person how well the candidate meets this job "
    "requirement."
)
SYSTEM_PROMPT_IDENTITYOS = (
    "You are IdentityOS, assessing how well a specific person meets one job "
    "requirement, using ONLY the evidence lines below, each tagged with an "
    "id like [resume:014] or [belief:001]. Cite the ids you rely on inline. "
    "Do not claim full competence where the evidence states only partial or "
    "committed-but-not-yet-held experience. If no evidence is relevant, say so."
)


def _as_question(req: ApplicationRequirement) -> Question:
    return Question(
        id=req.id,
        text=req.text,
        type=QuestionType.FACTUAL,
        application_context="IITACB CEO application — requirement-fit assessment",
    )


def assess_baseline_plain(
    req: ApplicationRequirement, provider
) -> tuple[Assessment, Trajectory]:
    traj = Trajectory(question_id=req.id, system_name="baseline_plain")
    prompt = f"REQUIREMENT:\n{req.text}\n"
    t0 = time.time()
    text = provider.complete(SYSTEM_PROMPT_PLAIN, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=req.text,
        action="call provider with zero context, zero verification",
        observation=text,
        reasoning="Baseline 1: no identity access at all.",
    )
    claims, overall = verify_answer(text, facts=[], beliefs=[])
    coverage = evidence_coverage(claims)
    bucket = bucket_from_signals(coverage, overall, claims)
    traj.add(
        stage="bucket",
        input_summary=text,
        action="derive fit bucket from coverage+confidence",
        observation=f"coverage={coverage:.2f} confidence={overall:.2f}",
        decision=bucket.value,
    )
    assessment = Assessment(
        requirement_id=req.id,
        system_name="baseline_plain",
        text=text,
        claims=claims,
        overall_confidence=overall,
        evidence_coverage=coverage,
        system_bucket=bucket,
        provider=provider.name,
        latency_ms=latency,
    )
    return assessment, traj


def assess_baseline_rag(
    req: ApplicationRequirement, ds: DigitalSelf, provider
) -> tuple[Assessment, Trajectory]:
    traj = Trajectory(question_id=req.id, system_name="baseline_rag")
    context = ds.fact_text_blob()  # unstructured, no ids, no beliefs
    traj.add(
        stage="retrieve",
        input_summary=req.text,
        action=f"dump all {len(ds.facts)} facts as unstructured text, no ranking, no ids",
        observation="no relevance filtering applied",
    )
    prompt = f"CONTEXT:\n{context}\n\nREQUIREMENT:\n{req.text}\n"
    t0 = time.time()
    text = provider.complete(SYSTEM_PROMPT_RAG, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=req.text,
        action="call provider with the unstructured context dump",
        observation=text,
    )
    # No citation ids exist in this context, so nothing can be verified as
    # explicitly grounded — this is structural, not a provider limitation.
    claims, overall = verify_answer(text, facts=[], beliefs=[])
    coverage = evidence_coverage(claims)
    bucket = bucket_from_signals(coverage, overall, claims)
    traj.add(
        stage="verify",
        input_summary=text,
        action="check for citations/grounding (none possible: no ids in context)",
        observation=f"coverage={coverage:.2f} confidence={overall:.2f}",
        decision=bucket.value,
    )
    assessment = Assessment(
        requirement_id=req.id,
        system_name="baseline_rag",
        text=text,
        claims=claims,
        overall_confidence=overall,
        evidence_coverage=coverage,
        system_bucket=bucket,
        provider=provider.name,
        latency_ms=latency,
    )
    return assessment, traj


def assess_identityos(
    req: ApplicationRequirement, ds: DigitalSelf, provider
) -> tuple[Assessment, Trajectory]:
    traj = Trajectory(question_id=req.id, system_name="identityos_v2")
    q = _as_question(req)
    facts, beliefs = retrieve(ds, q, top_k_facts=8, top_k_beliefs=4)
    context = format_context(facts, beliefs)
    traj.add(
        stage="retrieve",
        input_summary=req.text,
        action=f"lexical retrieval over Digital Self: top {len(facts)} facts, {len(beliefs)} beliefs",
        observation=context or "(no matching evidence found)",
    )
    prompt = f"CONTEXT:\n{context}\n\nREQUIREMENT:\n{req.text}\n"
    t0 = time.time()
    text = provider.complete(SYSTEM_PROMPT_IDENTITYOS, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=req.text,
        action="call provider with cited, confidence-annotated context",
        observation=text,
    )
    claims, overall = verify_answer(text, facts, beliefs)
    coverage = evidence_coverage(claims)
    bucket = bucket_from_signals(coverage, overall, claims)
    traj.add(
        stage="verify",
        input_summary=text,
        action="per-sentence grounding check (same verifier as v1)",
        observation=f"coverage={coverage:.2f} confidence={overall:.2f}",
        confidence=overall,
    )
    traj.add(
        stage="bucket",
        input_summary=text,
        action="derive fit bucket from coverage+confidence, not a self-reported label",
        observation=bucket.value,
        reasoning="A self-reported label from generation isn't independently checkable; a derived one is.",
        decision=bucket.value,
    )
    assessment = Assessment(
        requirement_id=req.id,
        system_name="identityos_v2",
        text=text,
        claims=claims,
        overall_confidence=overall,
        evidence_coverage=coverage,
        system_bucket=bucket,
        provider=provider.name,
        latency_ms=latency,
    )
    return assessment, traj


def assess_identityos_semantic(
    req: ApplicationRequirement,
    embedding_index: DigitalSelfEmbeddingIndex,
    provider,
) -> tuple[Assessment, Trajectory]:
    """v2.3 — identical pipeline to assess_identityos(), except retrieval
    is embedding-cosine-similarity ranked (retrieve_semantic) instead of
    lexical word-overlap (retrieve). Everything downstream — generation,
    verification, bucketing — is the exact same code, so any difference in
    outcome is attributable to retrieval alone."""
    traj = Trajectory(question_id=req.id, system_name="identityos_v2_semantic")
    q = _as_question(req)
    facts, beliefs = retrieve_semantic(embedding_index, q, top_k_facts=8, top_k_beliefs=4)
    context = format_context(facts, beliefs)
    traj.add(
        stage="retrieve",
        input_summary=req.text,
        action=(
            f"embedding-similarity retrieval ({embedding_index._provider.name}): "
            f"top {len(facts)} facts, {len(beliefs)} beliefs"
        ),
        observation=context or "(no matching evidence found)",
    )
    prompt = f"CONTEXT:\n{context}\n\nREQUIREMENT:\n{req.text}\n"
    t0 = time.time()
    text = provider.complete(SYSTEM_PROMPT_IDENTITYOS, prompt)
    latency = (time.time() - t0) * 1000
    traj.add(
        stage="generate",
        input_summary=req.text,
        action="call provider with cited, confidence-annotated context",
        observation=text,
    )
    claims, overall = verify_answer(text, facts, beliefs)
    coverage = evidence_coverage(claims)
    bucket = bucket_from_signals(coverage, overall, claims)
    traj.add(
        stage="verify",
        input_summary=text,
        action="per-sentence grounding check (same verifier as lexical identityos_v2)",
        observation=f"coverage={coverage:.2f} confidence={overall:.2f}",
        confidence=overall,
    )
    traj.add(
        stage="bucket",
        input_summary=text,
        action="derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)",
        observation=bucket.value,
        decision=bucket.value,
    )
    assessment = Assessment(
        requirement_id=req.id,
        system_name="identityos_v2_semantic",
        text=text,
        claims=claims,
        overall_confidence=overall,
        evidence_coverage=coverage,
        system_bucket=bucket,
        provider=provider.name,
        latency_ms=latency,
    )
    return assessment, traj
