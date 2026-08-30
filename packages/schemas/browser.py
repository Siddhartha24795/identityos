"""v3 — Browser execution schemas, matching the shapes named in PROMPT.md's
BROWSER AUTOMATION section (BrowserObservation / BrowserAction), scoped to
what v3.0 actually implements: a single-page form (no multi-page nav,
no file upload, no CAPTCHA/OTP handling yet — see docs/roadmap.md).
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FieldType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"


class DetectedField(BaseModel):
    """One form field as observed in the DOM — the generalized shape the
    field mapper reasons over, independent of any specific site's markup."""

    selector: str          # CSS selector used to act on this field
    label: str              # visible label text, or a best-effort fallback
    field_type: FieldType
    options: list[str] = Field(default_factory=list)  # for SELECT fields
    current_value: str = ""


class BrowserObservation(BaseModel):
    url: str
    title: str
    visible_text: str
    fields: list[DetectedField] = Field(default_factory=list)
    submit_selector: str | None = None
    errors: list[str] = Field(default_factory=list)


class ActionType(str, Enum):
    FILL_TEXT = "fill_text"
    SELECT_OPTION = "select_option"
    CHECK = "check"
    CLICK_SUBMIT = "click_submit"
    HALT_FOR_APPROVAL = "halt_for_approval"


class BrowserAction(BaseModel):
    action_type: ActionType
    target_selector: str
    value: str = ""
    rationale: str = ""
    confidence: float = 0.0
    evidence_refs: list[str] = Field(default_factory=list)


class FieldResult(BaseModel):
    field: DetectedField
    action: BrowserAction
    filled_value: str = ""
    verified: bool = False   # re-observed after filling and value matched
    verification_note: str = ""


class BrowserTaskResult(BaseModel):
    observation: BrowserObservation
    field_results: list[FieldResult] = Field(default_factory=list)
    submitted: bool = False
    halted_for_approval: bool = True
    avg_evidence_coverage: float = 0.0
    avg_confidence: float = 0.0
