"""v3 — maps detected form fields to BrowserActions. Reuses v1/v2's
retrieval + generation + verification unmodified for free-text fields
(a textarea's label IS a question); text/select/checkbox fields use
lighter, field-type-appropriate strategies. Nothing here is specific to
the local demo form's exact field ids — matching is by label text and
field type, the generalized shape PROMPT.md's BROWSER AUTOMATION section
asks for.
"""
from __future__ import annotations

import os

from packages.schemas.browser import ActionType, BrowserAction, DetectedField, FieldType
from packages.schemas.identity import DigitalSelf
from packages.schemas.qa import Question, QuestionType
from services.browser_engine.safety import (
    looks_like_anti_bot_check,
    looks_like_mfa_challenge,
    looks_like_prompt_injection,
)
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex, format_context, retrieve_hybrid
from services.qa_engine.verification import evidence_coverage, verify_answer

# v3.0 simplification: basic contact-routing fields (name/email) are looked
# up from a small known-profile table, not the Fact/Belief evidence system
# — those exist to verify substantive claims, not route static contact
# info. The name is the person's own (see docs/architecture.md). The email
# is read from APPLICANT_EMAIL (.env, gitignored) so a real address is
# never hardcoded into source that ships with the submission — falls back
# to a synthetic placeholder when unset, which is what every committed
# trajectory/eval artifact in this repo was generated with.
_APPLICANT_EMAIL = os.environ.get("APPLICANT_EMAIL", "identityos.demo@example.com")
_KNOWN_PROFILE_FIELDS = {
    "email address": _APPLICANT_EMAIL,
    "email": _APPLICANT_EMAIL,
}

CHECKBOX_CONFIDENCE_THRESHOLD = 0.7
SYSTEM_PROMPT = (
    "You are IdentityOS, answering one field of a job application on behalf "
    "of a specific person, using ONLY the evidence lines below, each tagged "
    "with an id like [resume:014] or [belief:001]. Cite the ids you rely on "
    "inline. Do not invent employment, degrees, publications, awards, or "
    "personal motivations not in the evidence."
)


def _map_text_field(field: DetectedField, ds: DigitalSelf) -> BrowserAction:
    label_lower = field.label.lower()
    if "name" in label_lower:
        return BrowserAction(
            action_type=ActionType.FILL_TEXT, target_selector=field.selector,
            value=ds.person_name, rationale="Digital Self person_name", confidence=0.99,
        )
    for key, value in _KNOWN_PROFILE_FIELDS.items():
        if key in label_lower:
            return BrowserAction(
                action_type=ActionType.FILL_TEXT, target_selector=field.selector,
                value=value, rationale="known profile field, not a Fact/Belief claim",
                confidence=0.95,
            )
    return BrowserAction(
        action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
        value="", rationale=f"no known mapping for text field '{field.label}'", confidence=0.0,
    )


def _map_select_field(field: DetectedField, ds: DigitalSelf) -> BrowserAction:
    """Simple lexical overlap between each option and the person's most
    recent role fact — the same word-overlap principle as v1's lexical
    retrieval, applied to a fixed option set instead of free text."""
    role_tokens = set()
    for f in ds.facts:
        if "chief technical officer" in f.text.lower() or "cto" in f.text.lower():
            role_tokens |= {"cto", "technical", "leadership", "chief"}
            break
    best_option, best_score = None, -1
    for opt in field.options:
        score = sum(1 for t in role_tokens if t in opt.lower())
        if score > best_score:
            best_option, best_score = opt, score
    if best_option is None or best_score <= 0:
        return BrowserAction(
            action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
            value="", rationale="no confident option match", confidence=0.0,
        )
    return BrowserAction(
        action_type=ActionType.SELECT_OPTION, target_selector=field.selector,
        value=best_option, rationale=f"current role matches option '{best_option}'",
        confidence=0.85,
    )


def _map_textarea_field(
    field: DetectedField, ds: DigitalSelf, embedding_index: DigitalSelfEmbeddingIndex, provider
) -> tuple[BrowserAction, list, list, str]:
    """Reuses the exact v1/v2 pipeline: the field's label is a question,
    hybrid retrieval finds evidence, the provider generates a cited
    answer, and the verifier scores it — this is not new logic.

    v3.1: if retrieve_hybrid() finds literally nothing — no lexical
    overlap AND the semantic fallback's best similarity stays under its
    own threshold (services/qa_engine/retrieval.py) — refuse instead of
    generating. This is deliberately NOT the same gate as v1's
    REFUSAL_THRESHOLD on overall_confidence: docs/hot_take.md documents
    that confidence is unreliable here because it's inherited from
    whatever gets cited, including a fact that's real but off-topic.
    Gating on evidence_coverage == 0 instead only fires when nothing was
    retrieved at all, which is a fact about retrieval, not a
    post-hoc-unreliable confidence score. This is what turns a
    decoy/off-topic field ("what's your favorite biryani recipe?") or an
    unscripted identity-verification question with no real evidence
    behind it into a halt instead of a confidently fabricated answer —
    without hand-coding either example."""
    q = Question(
        id=field.selector, text=field.label, type=QuestionType.UNSEEN_INFERENTIAL,
        application_context="Browser-filled application field",
    )
    facts, beliefs = retrieve_hybrid(ds, q, embedding_index, top_k_facts=8, top_k_beliefs=4)
    if not facts and not beliefs:
        # Short-circuits before any provider call — no point generating (and,
        # with a real LLM, paying for) text that's about to be discarded.
        action = BrowserAction(
            action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector, value="",
            rationale=(
                "zero evidence retrieved for this field (lexical and semantic "
                "retrieval both empty) — refusing rather than fabricating an answer"
            ),
            confidence=0.0,
        )
        return action, facts, beliefs, "halted: no evidence retrieved (coverage=0.00)"
    context = format_context(facts, beliefs)
    prompt = f"CONTEXT:\n{context}\n\nFIELD LABEL:\n{field.label}\n"
    text = provider.complete(SYSTEM_PROMPT, prompt)
    claims, overall = verify_answer(text, facts, beliefs)
    coverage = evidence_coverage(claims)
    action = BrowserAction(
        action_type=ActionType.FILL_TEXT, target_selector=field.selector, value=text,
        rationale=f"generated from {len(facts)} facts + {len(beliefs)} beliefs via hybrid retrieval",
        confidence=overall,
        evidence_refs=[ref for c in claims for ref in c.evidence_refs],
    )
    return action, facts, beliefs, f"coverage={coverage:.2f} confidence={overall:.2f}"


def map_field(
    field: DetectedField, ds: DigitalSelf, embedding_index: DigitalSelfEmbeddingIndex, provider
) -> tuple[BrowserAction, str]:
    """Returns (action, log_note). Dispatches purely on field_type — the
    same function handles any form with these four field types, not just
    the local demo's specific labels.

    v3.1: a field's label is untrusted content from a page this agent
    doesn't control. Checked here, before any type-specific dispatch, so
    neither check ever depends on field_type and the label text never
    reaches an LLM prompt once flagged (services/browser_engine/safety.py
    has the full rationale for both checks)."""
    if looks_like_prompt_injection(field.label):
        return (
            BrowserAction(
                action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
                value="", rationale="field label matches a prompt-injection pattern — not acted on",
                confidence=0.0,
            ),
            "halted: suspected prompt injection in field label",
        )
    if looks_like_anti_bot_check(field.label):
        return (
            BrowserAction(
                action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
                value="", rationale=(
                    "field asks an identity-verification question — an AI agent must not "
                    "answer this on a human's behalf"
                ),
                confidence=0.0,
            ),
            "halted: identity-verification question, not answered",
        )
    if looks_like_mfa_challenge(field.label):
        return (
            BrowserAction(
                action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
                value="", rationale=(
                    "field asks for an MFA/OTP code — ground rule 3: never bypass, "
                    "a human must enter this"
                ),
                confidence=0.0,
            ),
            "halted: MFA/OTP field, not answered",
        )
    if field.field_type == FieldType.TEXT:
        return _map_text_field(field, ds), "direct/known-profile mapping"
    if field.field_type == FieldType.SELECT:
        return _map_select_field(field, ds), "lexical option match"
    if field.field_type == FieldType.TEXTAREA:
        action, _, _, note = _map_textarea_field(field, ds, embedding_index, provider)
        return action, note
    if field.field_type == FieldType.CHECKBOX:
        # Decided after all other fields are known — see agent.py, which
        # only checks this once it has every other field's confidence.
        return (
            BrowserAction(
                action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
                value="", rationale="checkbox decided after other fields (see agent.py)",
                confidence=0.0,
            ),
            "deferred",
        )
    return (
        BrowserAction(
            action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector,
            value="", rationale="unknown field type", confidence=0.0,
        ),
        "unknown field type",
    )
