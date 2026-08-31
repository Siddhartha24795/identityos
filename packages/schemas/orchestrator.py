"""v4.0 — Orchestrator schemas.

PROMPT.md's AGENT ORGANIZATION section names an orchestrator that "must
dynamically decide which agents are actually necessary" and explicitly
warns against creating agents "for the sake of saying multi-agent." This
orchestrator routes a free-text request to exactly one of the three
already-built, independently-tested agents (v1 Q&A, v2 application-fit,
v3 browser-fill) rather than adding a fourth thing to say for itself.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class AgentTarget(str, Enum):
    QA = "qa"                          # services/qa_engine — v1 identityos_agent
    APPLICATION_FIT = "application_fit"  # services/application_engine — v2 identityos_v2_hybrid
    BROWSER_FILL = "browser_fill"      # services/browser_engine — v3 agent.run_application


class OrchestratorDecision(BaseModel):
    request_text: str
    target: AgentTarget
    matched_signal: str  # which keyword/pattern triggered this route, for auditability
    confidence: float
