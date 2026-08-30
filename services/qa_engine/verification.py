"""Grounding verification: does every sentence in a generated answer trace
back to real evidence, or was it invented?

v1 implements the FACTUAL VERIFICATION dimension from docs/architecture.md
(the other six — identity, contradiction, style, application, completeness,
browser — are out of scope until browser execution and a full application
narrative exist; see docs/roadmap.md). This is the dimension that most
directly measures hallucination, which is the core research question.

Citation parsing (v3.3): the original regex required a bracket to contain
exactly one id with zero internal whitespace (`[resume:014]`) — the only
shape the deterministic MockProvider ever produces. This project's first
real-LLM run (PROVIDER=groq, docs/evaluation.md) found it silently failed
on `[ resume:014 ]` (real models routinely pad brackets with spaces),
`[resume:014; belief:002]` (a real model citing two ids in one bracket),
and `【resume:014】` (fullwidth CJK brackets — Groq's `gpt-oss-120b`
sometimes emits these instead of ASCII ones) — every such sentence was
scored as uncited, which dragged a correctly-cited, honestly-hedged
patent-question answer's confidence below the refusal threshold for the
wrong reason (see docs/hot_take.md's v3.3 addendum). Fixed generally:
capture the raw contents of either bracket style, then split on `,`/`;`
and trim, rather than requiring one tightly-formatted ASCII-only id.
"""
from __future__ import annotations

import re

from packages.schemas.identity import Belief, Confidence, Fact
from packages.schemas.qa import AnswerClaim, ClaimType

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_BRACKET_RE = re.compile(r"\[([^\[\]]+)\]|【([^【】]+)】")


def _extract_citation_ids(text: str) -> list[str]:
    """Every id inside every bracket in `text`, whitespace-trimmed, brackets
    possibly holding more than one id separated by a comma or semicolon.
    `_BRACKET_RE` has two alternatives (ASCII `[...]` / fullwidth `【...】`),
    so each match is a 2-tuple with exactly one side populated. Membership
    in the real evidence store is checked by the caller — this just parses
    *candidate* ids, it doesn't validate them."""
    ids: list[str] = []
    for ascii_group, fullwidth_group in _BRACKET_RE.findall(text):
        group = ascii_group or fullwidth_group
        for part in re.split(r"[;,]", group):
            part = part.strip()
            if part:
                ids.append(part)
    return ids


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) > 2}


def _bucket_to_claim_type(bucket: Confidence) -> ClaimType:
    if bucket in (Confidence.VERIFIED_FACT,):
        return ClaimType.VERIFIED_FACT
    if bucket in (Confidence.STRONG_INFERENCE,):
        return ClaimType.STRONG_INFERENCE
    if bucket in (Confidence.MODERATE_INFERENCE, Confidence.WEAK_INFERENCE):
        return ClaimType.WEAK_INFERENCE
    return ClaimType.UNSUPPORTED


def verify_answer(
    answer_text: str, facts: list[Fact], beliefs: list[Belief]
) -> tuple[list[AnswerClaim], float]:
    """Return (per-sentence claims, overall_confidence)."""
    by_id: dict[str, tuple[str, Confidence, float]] = {}
    for f in facts:
        by_id[f.id] = (f.text, f.confidence_bucket, f.confidence)
    for b in beliefs:
        by_id[b.id] = (b.statement, b.confidence_bucket, b.confidence)

    evidence_texts = {eid: _tokens(txt) for eid, (txt, _, _) in by_id.items()}

    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(answer_text) if s.strip()]
    claims: list[AnswerClaim] = []

    for sentence in sentences:
        cited_ids = [m for m in _extract_citation_ids(sentence) if m in by_id]
        if cited_ids:
            # Ground truth via explicit citation: trust the weakest cited source.
            worst = min(cited_ids, key=lambda i: by_id[i][2])
            _, bucket, conf = by_id[worst]
            claims.append(
                AnswerClaim(
                    text=sentence,
                    evidence_refs=cited_ids,
                    claim_type=_bucket_to_claim_type(bucket),
                    confidence=conf,
                )
            )
            continue

        # No explicit citation: fall back to lexical-overlap grounding check.
        sentence_tokens = _tokens(sentence)
        best_id, best_overlap = None, 0.0
        for eid, ev_tokens in evidence_texts.items():
            if not sentence_tokens:
                continue
            overlap = len(sentence_tokens & ev_tokens) / len(sentence_tokens)
            if overlap > best_overlap:
                best_id, best_overlap = eid, overlap

        if best_id and best_overlap >= 0.35:
            claims.append(
                AnswerClaim(
                    text=sentence,
                    evidence_refs=[best_id],
                    claim_type=ClaimType.WEAK_INFERENCE,
                    confidence=0.5,
                )
            )
        else:
            claims.append(
                AnswerClaim(
                    text=sentence,
                    evidence_refs=[],
                    claim_type=ClaimType.UNSUPPORTED,
                    confidence=0.0,
                )
            )

    if not claims:
        return claims, 0.0
    overall = sum(c.confidence for c in claims) / len(claims)
    return claims, overall


def evidence_coverage(claims: list[AnswerClaim]) -> float:
    if not claims:
        return 0.0
    return sum(1 for c in claims if c.evidence_refs) / len(claims)


def unsupported_claim_rate(claims: list[AnswerClaim]) -> float:
    if not claims:
        return 1.0
    return sum(1 for c in claims if c.claim_type == ClaimType.UNSUPPORTED) / len(claims)
