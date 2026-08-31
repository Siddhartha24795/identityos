"""v4.0 — Orchestrator: routes one free-text request to exactly one of the
three independently-built, independently-tested agents in this repo.

Classification is heuristic (keyword/pattern matching over the request
text), not a learned classifier — the same documented simplification used
elsewhere in this codebase (v1's question-type "classify" stage, the
security layer's CAPTCHA/MFA phrase detection): it keeps the reference run
fully deterministic and free under PROVIDER=mock, and every routing
decision is auditable by reading the exact phrase that triggered it. An
LLM-based intent classifier is a natural extension (see docs/roadmap.md).

This module does not reimplement any agent. It dispatches into the
existing, already-tested entry points:
  - QA              -> services.qa_engine.identityos_agent.answer_identityos
  - APPLICATION_FIT -> services.application_engine.assess.assess_identityos_hybrid
  - BROWSER_FILL    -> services.browser_engine.agent.run_application
"""
from __future__ import annotations

import re

from packages.schemas.application import ApplicationRequirement, Assessment, RealAssessment
from packages.schemas.browser import BrowserTaskResult
from packages.schemas.identity import DigitalSelf
from packages.schemas.orchestrator import AgentTarget, OrchestratorDecision
from packages.schemas.qa import Answer, Question, QuestionType, Trajectory
from services.application_engine.assess import assess_identityos_hybrid
from services.qa_engine.identityos_agent import answer_identityos
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

# Checked in this order: a request naming a form/URL is BROWSER_FILL even
# if it also uses fit-assessment language ("apply" + "requirements"), since
# filling is the more consequential, more specific action.
_BROWSER_PATTERNS = [
    r"\bfill\b", r"\bapply to\b", r"\bapplication form\b", r"\bsubmit the form\b",
    r"https?://", r"file://",
]
_FIT_PATTERNS = [
    r"\bdoes (the|this) candidate\b", r"\bassess fit\b", r"\bjob requirement\b",
    r"\bmeet(s)? the requirement\b", r"\bhow well do i meet\b", r"\brequirement\b",
]


def classify_intent(request_text: str) -> OrchestratorDecision:
    low = request_text.lower()
    for pat in _BROWSER_PATTERNS:
        if re.search(pat, low):
            return OrchestratorDecision(
                request_text=request_text, target=AgentTarget.BROWSER_FILL,
                matched_signal=pat, confidence=0.9,
            )
    for pat in _FIT_PATTERNS:
        if re.search(pat, low):
            return OrchestratorDecision(
                request_text=request_text, target=AgentTarget.APPLICATION_FIT,
                matched_signal=pat, confidence=0.8,
            )
    return OrchestratorDecision(
        request_text=request_text, target=AgentTarget.QA,
        matched_signal="(default — no browser/fit pattern matched)", confidence=0.5,
    )


def route_and_execute(
    request_text: str,
    ds: DigitalSelf,
    embedding_index: DigitalSelfEmbeddingIndex,
    provider,
    form_url: str | None = None,
    headless: bool = True,
    history_dir=None,
    audit_log_path=None,
) -> tuple[OrchestratorDecision, Answer | Assessment | BrowserTaskResult, Trajectory, Trajectory]:
    """Returns (decision, downstream_result, orchestrator_trajectory,
    downstream_trajectory). The orchestrator trajectory is a first-class
    record of the routing decision itself, not just a log line — it is
    written to disk alongside the downstream agent's own trajectory
    (services/evaluation/run_orchestrator_demo.py), so a judge can audit
    "why did this request go here" independently of "what did the routed
    agent then do."
    """
    decision = classify_intent(request_text)
    orch_traj = Trajectory(question_id="orchestrate", system_name="orchestrator_v4")
    orch_traj.add(
        stage="classify_intent",
        input_summary=request_text,
        action=f"heuristic pattern match: matched '{decision.matched_signal}'",
        observation=f"routed to {decision.target.value}",
        confidence=decision.confidence,
        decision=decision.target.value,
    )

    if decision.target == AgentTarget.QA:
        question = Question(
            id="orchestrated_qa",
            text=request_text,
            # Conservative default: no declared type is available from a
            # bare request, so treat every routed question as if it were
            # unseen/inferential — the stricter refusal-gating path, which
            # is the safer default when the orchestrator itself doesn't
            # know the question's real shape.
            type=QuestionType.UNSEEN_INFERENTIAL,
            application_context="orchestrated live request (no declared application context)",
        )
        orch_traj.add(
            stage="dispatch", input_summary=request_text,
            action="call services.qa_engine.identityos_agent.answer_identityos",
            observation="Question.type defaulted to UNSEEN_INFERENTIAL (conservative)",
        )
        answer, downstream_traj = answer_identityos(question, ds, provider)
        return decision, answer, orch_traj, downstream_traj

    if decision.target == AgentTarget.APPLICATION_FIT:
        req = ApplicationRequirement(
            id="orchestrated_requirement",
            text=request_text,
            category="orchestrated",
            # No ground truth exists for a live, previously-unseen request —
            # these two fields exist only to satisfy the benchmark schema
            # and are never read by assess_identityos_hybrid() itself (only
            # by score_application_system(), which this live path never
            # calls).
            real_assessment=RealAssessment.PARTIAL,
            real_evidence_summary="(not applicable — live dispatch, no benchmark ground truth)",
        )
        orch_traj.add(
            stage="dispatch", input_summary=request_text,
            action="call services.application_engine.assess.assess_identityos_hybrid",
            observation="ad-hoc ApplicationRequirement built from request text; no ground truth available",
        )
        assessment, downstream_traj = assess_identityos_hybrid(req, ds, embedding_index, provider)
        return decision, assessment, orch_traj, downstream_traj

    # BROWSER_FILL
    from services.browser_engine.agent import run_application  # local import: optional dependency

    if form_url is None:
        raise ValueError(
            "Orchestrator routed this request to BROWSER_FILL but no form_url was "
            "given — a live browser dispatch needs a concrete target, unlike QA/"
            "APPLICATION_FIT which can act on the request text alone."
        )
    orch_traj.add(
        stage="dispatch", input_summary=request_text,
        action="call services.browser_engine.agent.run_application",
        observation=f"form_url={form_url}",
    )
    result, downstream_traj = run_application(
        ds, embedding_index, provider, form_url, approve_submit=False, headless=headless,
        history_dir=history_dir, audit_log_path=audit_log_path,
    )
    return decision, result, orch_traj, downstream_traj
