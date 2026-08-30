"""Unit tests for v3.2's per-application record store
(services/application_record/) — saved automatically at the end of every
run_application() call so a person can check what was actually told to a
specific employer once they reach interview stage."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.application_record import ApplicationRecord
from packages.schemas.browser import (
    ActionType,
    BrowserAction,
    BrowserObservation,
    BrowserTaskResult,
    DetectedField,
    FieldResult,
    FieldType,
)
from services.application_record.store import build_application_record, save_application_record


def _sample_result() -> BrowserTaskResult:
    field = DetectedField(selector="#name", label="Full name", field_type=FieldType.TEXT)
    action = BrowserAction(
        action_type=ActionType.FILL_TEXT, target_selector="#name", value="Jane Doe",
        confidence=0.99, evidence_refs=["resume:001"],
    )
    fr = FieldResult(field=field, action=action, filled_value="Jane Doe", verified=True)
    halted_field = DetectedField(selector="#weird", label="Are you a robot?", field_type=FieldType.TEXT)
    halted_action = BrowserAction(action_type=ActionType.HALT_FOR_APPROVAL, target_selector="#weird")
    halted_fr = FieldResult(field=halted_field, action=halted_action)
    obs = BrowserObservation(url="file://x", title="Test Application Form", visible_text="", fields=[field, halted_field])
    return BrowserTaskResult(
        observation=obs, field_results=[fr, halted_fr], submitted=False, halted_for_approval=True,
    )


def test_build_application_record_captures_filled_and_halted_entries():
    record = build_application_record(_sample_result(), "file://x")
    assert record.form_title == "Test Application Form"
    assert len(record.entries) == 2
    filled = next(e for e in record.entries if e.field_label == "Full name")
    assert filled.answer == "Jane Doe"
    assert filled.evidence_refs == ["resume:001"]
    assert filled.halted is False
    halted = next(e for e in record.entries if e.field_label == "Are you a robot?")
    assert halted.halted is True
    assert halted.answer == ""


def test_save_application_record_writes_json_and_markdown(tmp_path):
    path = save_application_record(_sample_result(), "file://x", history_dir=tmp_path)
    assert path.exists()
    md_path = path.with_suffix(".md")
    assert md_path.exists()
    restored = ApplicationRecord.model_validate_json(path.read_text(encoding="utf-8"))
    assert len(restored.entries) == 2
    md_text = md_path.read_text(encoding="utf-8")
    assert "Full name" in md_text
    assert "Jane Doe" in md_text
    assert "Halted for human review" in md_text
