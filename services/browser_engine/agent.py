"""v3 — orchestrates one application-form fill: observe -> map fields ->
fill -> re-observe/verify -> HALT for human approval before any submit.

Ground rule 4 ("keep consequential actions controlled through a sandbox or
simulation; add human approval before the action happens") is implemented
literally: this function never clicks submit unless the CALLER explicitly
passes approve_submit=True — there is no code path where the agent decides
on its own to submit. See scripts/run_browser_demo.py, where that flag is
off by default and must be passed on the command line.

v3.1: ground rule 3 ("never bypass MFA/CAPTCHA/anti-bot protections") gets
the same treatment — if `observe()` flags an anti-bot/CAPTCHA signal
(controller.py), this function halts before touching a single field,
rather than attempting to fill around it.

v3.2: every proposed field action — whatever field_mapper.py decided —
now passes through an independent, centralized SecurityPolicyEngine and
AgentAuditor (services/security/) before it is ever executed, per
docs/security_spec.md's "no direct execution path may bypass this control
plane" rule. field_mapper's own checks (injection/anti-bot/mfa/zero-evidence,
v3.1) remain as a fast, local first line of defense; the policy engine and
auditor don't trust them and re-derive their own verdict, so a bug in
field_mapper's logic can't silently skip the security layer. Every
decision is written to an append-only audit log
(data/evaluation/results/<tag>/security_audit.jsonl), and submission is
blocked if the audit trail has any unresolved BLOCK/ESCALATE finding, even
if the caller passed approve_submit=True. See docs/roadmap.md's v3.2
section for exactly what this does and does not implement from the full
spec, and why.

v3.2 also persists an ApplicationRecord (services/application_record/) for
every run — the questions asked and answers given, so a person can check
what they actually told a specific employer once they reach interview
stage, without relying on memory.
"""
from __future__ import annotations

from pathlib import Path

from packages.schemas.browser import (
    ActionType,
    BrowserAction,
    BrowserTaskResult,
    FieldResult,
    FieldType,
)
from packages.schemas.identity import DigitalSelf
from packages.schemas.qa import Trajectory
from packages.schemas.security import ActionRecord, PolicyDecision
from services.application_record.store import HISTORY_DIR, save_application_record
from services.browser_engine.controller import BrowserController
from services.browser_engine.field_mapper import CHECKBOX_CONFIDENCE_THRESHOLD, map_field
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex
from services.security.audit_log import AuditLog
from services.security.auditor import AgentAuditor
from services.security.policy_engine import SecurityPolicyEngine

_FILLABLE = {ActionType.FILL_TEXT, ActionType.SELECT_OPTION}
_OVERRIDABLE = {PolicyDecision.BLOCK, PolicyDecision.ESCALATE}


def run_application(
    ds: DigitalSelf,
    embedding_index: DigitalSelfEmbeddingIndex,
    provider,
    form_url: str,
    approve_submit: bool = False,
    headless: bool = True,
    audit_log_path: Path | None = None,
    history_dir: Path | None = None,
) -> tuple[BrowserTaskResult, Trajectory]:
    traj = Trajectory(question_id="browser_demo", system_name="identityos_browser_v3")
    policy_engine = SecurityPolicyEngine()
    auditor = AgentAuditor()
    audit_log = AuditLog(audit_log_path) if audit_log_path else None
    effective_history_dir = history_dir if history_dir is not None else HISTORY_DIR

    with BrowserController(headless=headless) as browser:
        browser.open(form_url)
        obs = browser.observe()
        traj.add(
            stage="observe",
            input_summary=form_url,
            action=f"detected {len(obs.fields)} fields via DOM inspection",
            observation=", ".join(f"{f.label} ({f.field_type.value})" for f in obs.fields),
        )

        page_result = policy_engine.evaluate_page(obs)
        if page_result.decision != PolicyDecision.ALLOW:
            traj.add(
                stage="halt_for_approval",
                input_summary="page-level anti-bot/CAPTCHA/MFA check",
                action=(
                    "ground rule 3: never bypass MFA/CAPTCHA/anti-bot protections — "
                    "halting before touching any field"
                ),
                observation=page_result.rationale,
                decision="halted — no fields were filled",
            )
            result = BrowserTaskResult(observation=obs, halted_for_approval=True, submitted=False)
            if audit_log:
                audit_log.flush()
            save_application_record(result, form_url, history_dir=effective_history_dir)
            return result, traj

        checkbox_fields = [f for f in obs.fields if f.field_type == FieldType.CHECKBOX]
        other_fields = [f for f in obs.fields if f.field_type != FieldType.CHECKBOX]

        field_results: list[FieldResult] = []
        for field in other_fields:
            action, note = map_field(field, ds, embedding_index, provider)
            action, policy_result, audit_verdict = _apply_security_layer(
                action, field, ds, policy_engine, auditor
            )
            traj.add(
                stage="plan",
                input_summary=field.label,
                action=f"mapped as {action.action_type.value} ({note})",
                observation=action.value[:200] if action.value else action.rationale,
                confidence=action.confidence,
            )
            traj.add(
                stage="policy_check",
                input_summary=field.label,
                action=f"policy={policy_result.decision.value}, audit={audit_verdict.decision.value}",
                observation=f"{policy_result.rationale} | {audit_verdict.rationale}",
                confidence=action.confidence,
            )
            if audit_log:
                audit_log.record(_to_action_record(action, field, policy_result, audit_verdict))
            filled_value = ""
            if action.action_type == ActionType.FILL_TEXT:
                browser.fill_text(field.selector, action.value)
                filled_value = action.value
            elif action.action_type == ActionType.SELECT_OPTION:
                browser.select_option(field.selector, action.value)
                filled_value = action.value
            field_results.append(FieldResult(field=field, action=action, filled_value=filled_value))

        # Re-observe: this is the BROWSER VERIFICATION dimension from
        # PROMPT.md's verification section — was the entered value actually
        # saved, not just "did we call fill() without an exception."
        obs_after = browser.observe()
        by_selector = {f.selector: f for f in obs_after.fields}
        verify_notes = []
        for fr in field_results:
            if fr.action.action_type not in _FILLABLE:
                continue
            current = by_selector.get(fr.field.selector)
            fr.verified = bool(current) and current.current_value == fr.filled_value
            fr.verification_note = "confirmed on re-observation" if fr.verified else "MISMATCH on re-observation"
            verify_notes.append(f"{fr.field.label}: {'OK' if fr.verified else 'FAIL'}")
        traj.add(
            stage="verify",
            input_summary="re-observed page after filling",
            action="compared each field's current DOM value to the intended fill value",
            observation="; ".join(verify_notes),
        )

        # Checkbox decision: only confirm accuracy if every filled field is
        # both confident AND verified — tying a real form action to the
        # same evidence-quality signal the rest of this project uses.
        fillable = [fr for fr in field_results if fr.action.action_type in _FILLABLE]
        confidences = [fr.action.confidence for fr in fillable if fr.action.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        all_verified = all(fr.verified for fr in fillable) if fillable else False
        text_fields_with_evidence = [
            fr for fr in fillable
            if fr.field.field_type == FieldType.TEXTAREA
        ]
        avg_evidence_coverage = (
            sum(1.0 if fr.action.evidence_refs else 0.0 for fr in text_fields_with_evidence)
            / len(text_fields_with_evidence)
            if text_fields_with_evidence
            else 0.0
        )

        for cb in checkbox_fields:
            should_check = avg_confidence >= CHECKBOX_CONFIDENCE_THRESHOLD and all_verified
            if should_check:
                action = BrowserAction(
                    action_type=ActionType.CHECK, target_selector=cb.selector, value="checked",
                    rationale=(
                        f"avg field confidence {avg_confidence:.2f} >= "
                        f"{CHECKBOX_CONFIDENCE_THRESHOLD} and every field verified"
                    ),
                    confidence=avg_confidence,
                )
                action, policy_result, audit_verdict = _apply_security_layer(
                    action, cb, ds, policy_engine, auditor
                )
                if audit_log:
                    audit_log.record(_to_action_record(action, cb, policy_result, audit_verdict))
                if action.action_type == ActionType.CHECK:
                    browser.check(cb.selector)
                    field_results.append(
                        FieldResult(field=cb, action=action, filled_value="checked", verified=True)
                    )
                else:
                    field_results.append(
                        FieldResult(field=cb, action=action, verified=False, verification_note="left unchecked")
                    )
            else:
                action = BrowserAction(
                    action_type=ActionType.HALT_FOR_APPROVAL, target_selector=cb.selector, value="",
                    rationale=(
                        f"avg field confidence {avg_confidence:.2f} or verification status "
                        "did not clear the bar — leaving unchecked for human review"
                    ),
                    confidence=avg_confidence,
                )
                field_results.append(
                    FieldResult(field=cb, action=action, verified=False, verification_note="left unchecked")
                )
            traj.add(
                stage="recover" if action.action_type != ActionType.CHECK else "verify",
                input_summary=cb.label,
                action="decide accuracy-confirmation checkbox from aggregate field confidence + verification",
                observation=action.rationale,
                confidence=avg_confidence,
            )

        # Human-approval checkpoint — always logged, regardless of outcome.
        # v3.2: authorization now also depends on the run's own audit trail,
        # not just the raw flag — a caller passing approve_submit=True does
        # not override an unresolved BLOCK/ESCALATE finding from this run.
        submit_result = policy_engine.evaluate_submit(approve_submit)
        traj.add(
            stage="halt_for_approval",
            input_summary="submit action",
            action="pausing before any submit click (ground rule 4: sandbox consequential actions)",
            observation=submit_result.rationale,
            decision="approved" if submit_result.decision == PolicyDecision.ALLOW else "not approved — halted",
        )

        submitted = False
        if submit_result.decision == PolicyDecision.ALLOW and obs.submit_selector:
            browser.click(obs.submit_selector)
            submitted = True
            traj.add(
                stage="complete", input_summary="submit",
                action="clicked submit (explicitly approved by caller, audit trail clean)",
                observation="submitted",
            )

        result = BrowserTaskResult(
            observation=obs,
            field_results=field_results,
            submitted=submitted,
            halted_for_approval=submit_result.decision != PolicyDecision.ALLOW,
            avg_evidence_coverage=avg_evidence_coverage,
            avg_confidence=avg_confidence,
        )
        if audit_log:
            audit_log.flush()
        save_application_record(result, form_url, history_dir=effective_history_dir)
        return result, traj


def _apply_security_layer(action, field, ds, policy_engine, auditor):
    """Runs the independent policy + audit checks and, on anything but
    ALLOW from either, downgrades the action to HALT_FOR_APPROVAL —
    overriding whatever field_mapper.py proposed. WARN does not block
    execution; it's logged and surfaced in the trajectory."""
    policy_result = policy_engine.evaluate(action, field)
    if policy_result.decision in _OVERRIDABLE:
        action = BrowserAction(
            action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector, value="",
            rationale=f"security policy engine: {policy_result.rationale}", confidence=0.0,
        )
        return action, policy_result, auditor.review(action, field, ds)

    audit_verdict = auditor.review(action, field, ds)
    if audit_verdict.decision in _OVERRIDABLE:
        action = BrowserAction(
            action_type=ActionType.HALT_FOR_APPROVAL, target_selector=field.selector, value="",
            rationale=f"agent auditor: {audit_verdict.rationale}", confidence=0.0,
        )
    return action, policy_result, audit_verdict


def _to_action_record(action, field, policy_result, audit_verdict) -> ActionRecord:
    import time

    final = PolicyDecision.ALLOW
    if PolicyDecision.BLOCK in (policy_result.decision, audit_verdict.decision):
        final = PolicyDecision.BLOCK
    elif PolicyDecision.ESCALATE in (policy_result.decision, audit_verdict.decision):
        final = PolicyDecision.ESCALATE
    elif PolicyDecision.WARN in (policy_result.decision, audit_verdict.decision):
        final = PolicyDecision.WARN
    return ActionRecord(
        timestamp=time.time(),
        agent="identityos_browser_v3",
        action_type=action.action_type.value,
        target_selector=action.target_selector,
        input_summary=field.label,
        evidence_refs=action.evidence_refs,
        confidence=action.confidence,
        risk_level=policy_result.risk_level,
        policy_decision=policy_result.decision,
        policy_rationale=policy_result.rationale,
        audit_decision=audit_verdict.decision,
        audit_rationale=audit_verdict.rationale,
        final_decision=final,
    )
