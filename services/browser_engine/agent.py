"""v3 — orchestrates one application-form fill: observe -> map fields ->
fill -> re-observe/verify -> HALT for human approval before any submit.

Ground rule 4 ("keep consequential actions controlled through a sandbox or
simulation; add human approval before the action happens") is implemented
literally: this function never clicks submit unless the CALLER explicitly
passes approve_submit=True — there is no code path where the agent decides
on its own to submit. See scripts/run_browser_demo.py, where that flag is
off by default and must be passed on the command line.
"""
from __future__ import annotations

from packages.schemas.browser import (
    ActionType,
    BrowserAction,
    BrowserTaskResult,
    FieldResult,
    FieldType,
)
from packages.schemas.identity import DigitalSelf
from packages.schemas.qa import Trajectory
from services.browser_engine.controller import BrowserController
from services.browser_engine.field_mapper import CHECKBOX_CONFIDENCE_THRESHOLD, map_field
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

_FILLABLE = {ActionType.FILL_TEXT, ActionType.SELECT_OPTION}


def run_application(
    ds: DigitalSelf,
    embedding_index: DigitalSelfEmbeddingIndex,
    provider,
    form_url: str,
    approve_submit: bool = False,
    headless: bool = True,
) -> tuple[BrowserTaskResult, Trajectory]:
    traj = Trajectory(question_id="browser_demo", system_name="identityos_browser_v3")

    with BrowserController(headless=headless) as browser:
        browser.open(form_url)
        obs = browser.observe()
        traj.add(
            stage="observe",
            input_summary=form_url,
            action=f"detected {len(obs.fields)} fields via DOM inspection",
            observation=", ".join(f"{f.label} ({f.field_type.value})" for f in obs.fields),
        )

        checkbox_fields = [f for f in obs.fields if f.field_type == FieldType.CHECKBOX]
        other_fields = [f for f in obs.fields if f.field_type != FieldType.CHECKBOX]

        field_results: list[FieldResult] = []
        for field in other_fields:
            action, note = map_field(field, ds, embedding_index, provider)
            traj.add(
                stage="plan",
                input_summary=field.label,
                action=f"mapped as {action.action_type.value} ({note})",
                observation=action.value[:200] if action.value else action.rationale,
                confidence=action.confidence,
            )
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
                browser.check(cb.selector)
                action = BrowserAction(
                    action_type=ActionType.CHECK, target_selector=cb.selector, value="checked",
                    rationale=(
                        f"avg field confidence {avg_confidence:.2f} >= "
                        f"{CHECKBOX_CONFIDENCE_THRESHOLD} and every field verified"
                    ),
                    confidence=avg_confidence,
                )
                field_results.append(FieldResult(field=cb, action=action, filled_value="checked", verified=True))
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
                stage="recover" if not should_check else "verify",
                input_summary=cb.label,
                action="decide accuracy-confirmation checkbox from aggregate field confidence + verification",
                observation=action.rationale,
                confidence=avg_confidence,
            )

        # Human-approval checkpoint — always logged, regardless of outcome.
        traj.add(
            stage="halt_for_approval",
            input_summary="submit action",
            action="pausing before any submit click (ground rule 4: sandbox consequential actions)",
            observation="awaiting explicit approve_submit=True from a human-invoked caller",
            decision="approved" if approve_submit else "not approved — halted",
        )

        submitted = False
        if approve_submit and obs.submit_selector:
            browser.click(obs.submit_selector)
            submitted = True
            traj.add(
                stage="complete", input_summary="submit",
                action="clicked submit (explicitly approved by caller)", observation="submitted",
            )

        result = BrowserTaskResult(
            observation=obs,
            field_results=field_results,
            submitted=submitted,
            halted_for_approval=not approve_submit,
            avg_evidence_coverage=avg_evidence_coverage,
            avg_confidence=avg_confidence,
        )
        return result, traj
