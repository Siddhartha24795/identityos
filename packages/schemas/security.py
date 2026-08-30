"""v3.2 — typed contracts for the Security Policy Engine + Agent Auditor
control plane (services/security/). Every consequential browser action
passes through this layer independently of whatever proposed it
(services/browser_engine/field_mapper.py's own v3.1 checks stay as a fast,
local first line of defense — this is the second, centralized,
un-bypassable one; see services/security/policy_engine.py for why both
exist). Scoped implementation of docs/security_spec.md — see
docs/roadmap.md's v3.2 section for exactly what is and isn't built
against that spec, and why.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LEVEL_0_INFORMATIONAL = "level_0_informational"
    LEVEL_1_LOW_RISK = "level_1_low_risk"
    LEVEL_2_MODERATE = "level_2_moderate"
    LEVEL_3_HIGH = "level_3_high"
    LEVEL_4_CRITICAL = "level_4_critical"


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"


class PolicyResult(BaseModel):
    decision: PolicyDecision
    risk_level: RiskLevel
    rationale: str
    checks_run: list[str] = Field(default_factory=list)


class AuditVerdict(BaseModel):
    decision: PolicyDecision
    rationale: str


class ActionRecord(BaseModel):
    """One append-only audit-log entry (services/security/audit_log.py).

    Deliberately has no field that could ever hold a secret (password,
    OTP, session token, cookie) — this system has no credential handling
    at all yet (docs/roadmap.md's v3.2 section), so the schema simply has
    nowhere to put one, rather than relying on a redaction step that could
    be forgotten."""

    timestamp: float
    agent: str
    action_type: str
    target_selector: str
    input_summary: str
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float
    risk_level: RiskLevel
    policy_decision: PolicyDecision
    policy_rationale: str
    audit_decision: PolicyDecision
    audit_rationale: str
    final_decision: PolicyDecision
