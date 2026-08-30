"""v2.5 — cover letter generation: baseline_plain / baseline_rag / identityos.

Reuses v1/v2's retrieval, verification, and hybrid-retrieval machinery
unmodified. The only new logic is section planning + narrative-state
tracking (prefer NOT re-citing a fact already used in an earlier section)
— a concrete, testable instance of the original brief's
APPLICATION_NARRATIVE_STATE, not a new retrieval or verification mechanism.
"""
from __future__ import annotations

import time

from packages.schemas.document import DocumentSection, GeneratedDocument
from packages.schemas.identity import Belief, DigitalSelf, Fact, FactCategory
from packages.schemas.qa import Question, QuestionType, Trajectory
from services.document_engine.sections import COVER_LETTER_SECTIONS
from services.qa_engine.retrieval import (
    DigitalSelfEmbeddingIndex,
    format_context,
    retrieve_hybrid,
)
from services.qa_engine.verification import (
    evidence_coverage,
    unsupported_claim_rate,
    verify_answer,
)

SYSTEM_PROMPT_PLAIN = (
    "You are a helpful assistant writing one section of a cover letter for a "
    "generic technology leadership role, in the first person, on behalf of "
    "the applicant. Be confident and specific."
)
SYSTEM_PROMPT_RAG = (
    "You are a helpful assistant. Using the background information provided, "
    "write one section of a cover letter, in the first person, addressing "
    "the prompt below."
)
SYSTEM_PROMPT_IDENTITYOS = (
    "You are IdentityOS, writing one section of a cover letter on behalf of "
    "a specific person, using ONLY the evidence lines below, each tagged "
    "with an id like [resume:014] or [belief:001]. Cite the ids you rely on "
    "inline. Do not invent employment, degrees, publications, awards, or "
    "personal motivations not in the evidence."
)


def _exclude_application_specific(facts: list[Fact]) -> list[Fact]:
    """A generic cover letter (no named target opportunity yet — see
    docs/roadmap.md v2.6 for a real ApplicationIntentModel scope) must not
    draw on evidence that is real and grounded but was written as strategy
    narrative for a SPECIFIC different application (FactCategory.
    APPLICATION_SPECIFIC — see packages/schemas/identity.py). Found by
    actually reading a generated letter, not designed in from the start —
    docs/hot_take.md v2.5 addendum."""
    return [f for f in facts if f.category != FactCategory.APPLICATION_SPECIFIC]


def _prefer_unused(
    facts: list[Fact],
    beliefs: list[Belief],
    used_ids: set[str],
    target_facts: int = 6,
    target_beliefs: int = 3,
) -> tuple[list[Fact], list[Belief]]:
    """Reorder retrieved evidence so fresh (not-yet-cited) items fill the
    slots first, falling back to already-used items only if there isn't
    enough fresh evidence — real cover letters do sometimes reference the
    same headline achievement twice, so reuse is allowed, just deprioritized.
    """
    unused_facts = [f for f in facts if f.id not in used_ids]
    used_facts = [f for f in facts if f.id in used_ids]
    unused_beliefs = [b for b in beliefs if b.id not in used_ids]
    used_beliefs = [b for b in beliefs if b.id in used_ids]
    return (
        (unused_facts + used_facts)[:target_facts],
        (unused_beliefs + used_beliefs)[:target_beliefs],
    )


def _finalize(
    document_type: str,
    system_name: str,
    sections: list[DocumentSection],
    provider_name: str,
    latency_ms: float,
) -> GeneratedDocument:
    full_text = "\n\n".join(s.text for s in sections)
    coverages = [s.evidence_coverage for s in sections]
    all_claims = [c for s in sections for c in s.claims]
    unsupported = unsupported_claim_rate(all_claims) if all_claims else 1.0
    total_citations = sum(len(c.evidence_refs) for s in sections for c in s.claims)
    reused_citations = sum(len(s.reused_evidence_ids) for s in sections)
    repeated_rate = (reused_citations / total_citations) if total_citations else 0.0
    return GeneratedDocument(
        document_type=document_type,
        system_name=system_name,
        sections=sections,
        full_text=full_text,
        avg_evidence_coverage=sum(coverages) / len(coverages) if coverages else 0.0,
        avg_unsupported_claim_rate=unsupported,
        repeated_evidence_rate=repeated_rate,
        provider=provider_name,
        latency_ms=latency_ms,
    )


def generate_cover_letter_baseline_plain(provider) -> tuple[GeneratedDocument, Trajectory]:
    traj = Trajectory(question_id="cover_letter", system_name="baseline_plain")
    sections: list[DocumentSection] = []
    t0 = time.time()
    for name, query in COVER_LETTER_SECTIONS:
        text = provider.complete(SYSTEM_PROMPT_PLAIN, f"SECTION PROMPT:\n{query}\n")
        claims, overall = verify_answer(text, facts=[], beliefs=[])
        coverage = evidence_coverage(claims)
        sections.append(
            DocumentSection(
                section_name=name, query_text=query, text=text, claims=claims,
                evidence_coverage=coverage, overall_confidence=overall,
            )
        )
        traj.add(
            stage="generate", input_summary=query,
            action="call provider with zero context, zero verification",
            observation=text,
        )
    latency = (time.time() - t0) * 1000
    return _finalize("cover_letter", "baseline_plain", sections, provider.name, latency), traj


def generate_cover_letter_baseline_rag(
    ds: DigitalSelf, provider
) -> tuple[GeneratedDocument, Trajectory]:
    traj = Trajectory(question_id="cover_letter", system_name="baseline_rag")
    context = ds.fact_text_blob()
    sections: list[DocumentSection] = []
    t0 = time.time()
    for name, query in COVER_LETTER_SECTIONS:
        prompt = f"CONTEXT:\n{context}\n\nSECTION PROMPT:\n{query}\n"
        text = provider.complete(SYSTEM_PROMPT_RAG, prompt)
        claims, overall = verify_answer(text, facts=[], beliefs=[])
        coverage = evidence_coverage(claims)
        sections.append(
            DocumentSection(
                section_name=name, query_text=query, text=text, claims=claims,
                evidence_coverage=coverage, overall_confidence=overall,
            )
        )
        traj.add(
            stage="generate", input_summary=query,
            action="call provider with unstructured full-fact dump, no ids",
            observation=text,
        )
    latency = (time.time() - t0) * 1000
    return _finalize("cover_letter", "baseline_rag", sections, provider.name, latency), traj


def generate_cover_letter_identityos(
    ds: DigitalSelf, embedding_index: DigitalSelfEmbeddingIndex, provider
) -> tuple[GeneratedDocument, Trajectory]:
    traj = Trajectory(question_id="cover_letter", system_name="identityos_v2_5")
    used_ids: set[str] = set()
    sections: list[DocumentSection] = []
    t0 = time.time()
    for name, query in COVER_LETTER_SECTIONS:
        q = Question(
            id=f"cover_letter:{name}",
            text=query,
            type=QuestionType.UNSEEN_INFERENTIAL,
            application_context="Cover letter section",
        )
        raw_facts, raw_beliefs = retrieve_hybrid(
            ds, q, embedding_index, top_k_facts=12, top_k_beliefs=6
        )
        n_before = len(raw_facts)
        raw_facts = _exclude_application_specific(raw_facts)
        n_excluded = n_before - len(raw_facts)
        facts, beliefs = _prefer_unused(raw_facts, raw_beliefs, used_ids)
        reused_ids = [f.id for f in facts if f.id in used_ids] + [
            b.id for b in beliefs if b.id in used_ids
        ]
        context = format_context(facts, beliefs)
        traj.add(
            stage="retrieve", input_summary=query,
            action=(
                f"hybrid retrieval, preferring unused evidence, excluding "
                f"application-specific proposal content ({n_excluded} excluded): "
                f"{len(facts)} facts, {len(beliefs)} beliefs "
                f"({len(reused_ids)} reused from earlier sections)"
            ),
            observation=context or "(no matching evidence found)",
        )
        prompt = f"CONTEXT:\n{context}\n\nSECTION PROMPT:\n{query}\n"
        text = provider.complete(SYSTEM_PROMPT_IDENTITYOS, prompt)
        traj.add(
            stage="generate", input_summary=query,
            action="call provider with cited, confidence-annotated context",
            observation=text,
        )
        claims, overall = verify_answer(text, facts, beliefs)
        coverage = evidence_coverage(claims)
        traj.add(
            stage="verify", input_summary=text,
            action="per-sentence grounding check (same verifier as v1/v2)",
            observation=f"coverage={coverage:.2f} confidence={overall:.2f}",
            confidence=overall,
        )
        used_ids.update(f.id for f in facts)
        used_ids.update(b.id for b in beliefs)
        sections.append(
            DocumentSection(
                section_name=name, query_text=query, text=text, claims=claims,
                evidence_coverage=coverage, overall_confidence=overall,
                reused_evidence_ids=reused_ids,
            )
        )
    latency = (time.time() - t0) * 1000
    return _finalize("cover_letter", "identityos_v2_5", sections, provider.name, latency), traj
