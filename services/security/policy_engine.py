"""v3.2 — SecurityPolicyEngine: the centralized, un-bypassable control
plane every browser action must pass through, independent of whatever
proposed the action. services/browser_engine/field_mapper.py's own v3.1
heuristic checks (injection/anti-bot/mfa/zero-evidence) stay in place as a
fast, local first line of defense; this module doesn't trust them and
re-derives its own verdict from scratch, so a bug in field_mapper's logic
can't silently skip the security layer — the point of "no direct
execution path may bypass this control plane" (docs/security_spec.md).

This is a deliberately scoped implementation of that spec's core
architectural rule: a first-class policy engine and independent auditor,
not scattered if/else checks; risk-leveled actions; ALLOW/WARN/BLOCK/
ESCALATE decisions; an append-only audit log (audit_log.py). What's NOT
built: most of the spec's other sections (self-improvement CI,
cross-application deduplication, phishing/domain-redirect detection, a
real OTP-channel abstraction) require capabilities — a persistent
learning loop, a multi-application store, real authenticated navigation —
that don't exist anywhere else in this codebase yet, so there is nothing
real for that infrastructure to gate. See docs/roadmap.md's v3.2 section
for the full scoping decision.
"""
from __future__ import annotations

from packages.schemas.browser import ActionType, BrowserAction, BrowserObservation, DetectedField
from packages.schemas.security import PolicyDecision, PolicyResult, RiskLevel
from services.browser_engine.safety import (
    looks_like_anti_bot_check,
    looks_like_mfa_challenge,
    looks_like_prompt_injection,
)

# Configurable, per docs/security_spec.md's "policy thresholds must be
# configurable" — a plain module-level dict, not buried in conditionals.
_MIN_CONFIDENCE_BY_LEVEL: dict[RiskLevel, float] = {
    RiskLevel.LEVEL_1_LOW_RISK: 0.85,
    RiskLevel.LEVEL_2_MODERATE: 0.5,
}


def classify_risk(action: BrowserAction, field: DetectedField) -> RiskLevel:
    """Maps v3's actual action set onto the spec's five risk levels
    (docs/security_spec.md's ACTION RISK LEVELS section). LEVEL_3 isn't
    produced by anything v3.0/v3.1 builds (it's reserved for actions this
    codebase doesn't have yet, e.g. "change salary expectation") — see
    evaluate() below, which still has a rule for it so the level isn't
    dead code once such a field exists."""
    if action.action_type == ActionType.HALT_FOR_APPROVAL:
        return RiskLevel.LEVEL_0_INFORMATIONAL
    if action.action_type == ActionType.CLICK_SUBMIT:
        return RiskLevel.LEVEL_4_CRITICAL
    if action.action_type == ActionType.CHECK:
        return RiskLevel.LEVEL_2_MODERATE
    if action.action_type in (ActionType.FILL_TEXT, ActionType.SELECT_OPTION):
        if field.field_type.value == "text" and action.confidence >= 0.9:
            return RiskLevel.LEVEL_1_LOW_RISK  # known-profile fields (name/email)
        return RiskLevel.LEVEL_2_MODERATE  # generated or option-matched content
    return RiskLevel.LEVEL_2_MODERATE


class SecurityPolicyEngine:
    """Stateless per call except for an append-only decision history for
    the current run, used by evaluate_submit()'s "no open findings" gate."""

    def __init__(self) -> None:
        self.history: list[PolicyResult] = []

    def evaluate_page(self, obs: BrowserObservation) -> PolicyResult:
        """Ground rule 3: never bypass MFA/CAPTCHA/anti-bot protections.
        Page-level signals (controller.py's observe()) BLOCK the entire
        task before a single field is touched.

        v4.3: also blocks on "page never actually loaded" signals (a
        failed HTTP status or blocked-page title phrasing) — found by
        testing against a real site that returned a 403 which observe()
        used to silently report as "0 fields, 0 errors," indistinguishable
        from "this page has no form." See controller.py / safety.py."""
        flags = [
            e for e in obs.errors
            if "anti-bot" in e or "CAPTCHA" in e or "MFA/OTP" in e
            or "page failed to load" in e or "blocked-page" in e
        ]
        checks_run = ["anti_bot_widget", "anti_bot_text", "mfa_text", "page_load_status", "blocked_page_text"]
        if flags:
            result = PolicyResult(
                decision=PolicyDecision.BLOCK, risk_level=RiskLevel.LEVEL_4_CRITICAL,
                rationale="; ".join(flags), checks_run=checks_run,
            )
        else:
            result = PolicyResult(
                decision=PolicyDecision.ALLOW, risk_level=RiskLevel.LEVEL_0_INFORMATIONAL,
                rationale="no anti-bot/CAPTCHA/MFA signal on page", checks_run=checks_run,
            )
        self.history.append(result)
        return result

    def evaluate(self, action: BrowserAction, field: DetectedField) -> PolicyResult:
        """Independent re-check of a single proposed action. Order matters:
        untrusted-content checks (injection/anti-bot/mfa) and target
        validation run regardless of what action_type was proposed, before
        any risk-based confidence floor is applied."""
        checks_run = [
            "prompt_injection", "anti_bot_text", "mfa_text",
            "target_validation", "confidence_floor",
        ]

        if looks_like_prompt_injection(field.label):
            result = PolicyResult(
                decision=PolicyDecision.BLOCK, risk_level=RiskLevel.LEVEL_3_HIGH,
                rationale="field label matches a prompt-injection pattern", checks_run=checks_run,
            )
        elif looks_like_anti_bot_check(field.label) or looks_like_mfa_challenge(field.label):
            result = PolicyResult(
                decision=PolicyDecision.ESCALATE, risk_level=RiskLevel.LEVEL_3_HIGH,
                rationale="field asks an identity-verification/MFA question a human must answer",
                checks_run=checks_run,
            )
        elif action.target_selector != field.selector:
            result = PolicyResult(
                decision=PolicyDecision.BLOCK, risk_level=RiskLevel.LEVEL_3_HIGH,
                rationale=(
                    f"target mismatch: action targets {action.target_selector!r}, "
                    f"observed field is {field.selector!r}"
                ),
                checks_run=checks_run,
            )
        elif action.action_type == ActionType.HALT_FOR_APPROVAL:
            result = PolicyResult(
                decision=PolicyDecision.ALLOW, risk_level=RiskLevel.LEVEL_0_INFORMATIONAL,
                rationale="proposed action is already a halt — nothing to execute", checks_run=checks_run,
            )
        else:
            risk = classify_risk(action, field)
            floor = _MIN_CONFIDENCE_BY_LEVEL.get(risk, 1.0)
            if action.confidence < floor:
                result = PolicyResult(
                    decision=PolicyDecision.BLOCK, risk_level=risk,
                    rationale=f"confidence {action.confidence:.2f} below the {floor:.2f} floor for {risk.value}",
                    checks_run=checks_run,
                )
            elif risk == RiskLevel.LEVEL_3_HIGH:
                result = PolicyResult(
                    decision=PolicyDecision.ESCALATE, risk_level=risk,
                    rationale="LEVEL_3 actions always require human review", checks_run=checks_run,
                )
            else:
                result = PolicyResult(
                    decision=PolicyDecision.ALLOW, risk_level=risk,
                    rationale=f"confidence {action.confidence:.2f} clears the {floor:.2f} floor for {risk.value}",
                    checks_run=checks_run,
                )
        self.history.append(result)
        return result

    def evaluate_submit(self, approve_submit: bool) -> PolicyResult:
        """Ground rule 4, extended: authorization depends on this run's own
        audit trail, not just the raw flag. A caller passing
        approve_submit=True does not override an unresolved BLOCK/ESCALATE
        finding recorded earlier in the same run — "never silently infer
        authorization for critical actions" (docs/security_spec.md)."""
        checks_run = ["explicit_approval", "open_findings"]
        open_findings = [
            r for r in self.history if r.decision in (PolicyDecision.BLOCK, PolicyDecision.ESCALATE)
        ]
        if not approve_submit:
            result = PolicyResult(
                decision=PolicyDecision.BLOCK, risk_level=RiskLevel.LEVEL_4_CRITICAL,
                rationale="approve_submit=False — ground rule 4, no code path submits without it",
                checks_run=checks_run,
            )
        elif open_findings:
            result = PolicyResult(
                decision=PolicyDecision.BLOCK, risk_level=RiskLevel.LEVEL_4_CRITICAL,
                rationale=(
                    f"{len(open_findings)} unresolved BLOCK/ESCALATE finding(s) in this run's "
                    "audit trail — submission refused even though approve_submit=True"
                ),
                checks_run=checks_run,
            )
        else:
            result = PolicyResult(
                decision=PolicyDecision.ALLOW, risk_level=RiskLevel.LEVEL_4_CRITICAL,
                rationale="approve_submit=True and no open findings in this run's audit trail",
                checks_run=checks_run,
            )
        self.history.append(result)
        return result
