"""Smoke tests for v3's browser automation pipeline.

Most tests here exercise field_mapper/schema logic directly against
DetectedField objects (fast, no browser). One end-to-end test actually
launches Chromium against the local synthetic form
(data/applications/local_demo/) — this is the one that originally
surfaced both v3 bugs (select-field verification, MockProvider prompt
parsing — see services/browser_engine/controller.py and
services/providers/mock_provider.py), so it stays a real regression test
rather than being mocked away. It adds ~1s to `make test` for a real
Chromium launch; still well under the suite's total budget.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.browser import (
    ActionType,
    BrowserAction,
    BrowserObservation,
    BrowserTaskResult,
    DetectedField,
    FieldType,
)
from services.browser_engine.agent import run_application
from services.browser_engine.field_mapper import map_field
from services.embeddings.hash_provider import HashEmbeddingProvider
from services.identity_engine import ingest, seed_beliefs
from services.providers import get_provider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"
FORM_PATH = REPO_ROOT / "data" / "applications" / "local_demo" / "application_form.html"


def _build_test_digital_self():
    sources = sorted(SOURCE_DIR.glob("*.md"))
    ds = ingest.build_digital_self(sources, person_name="Siddhartha Mishra", version=99)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    return ds


def test_schemas_round_trip_through_json():
    field = DetectedField(selector="#x", label="Full name", field_type=FieldType.TEXT)
    obs = BrowserObservation(url="file://x", title="t", visible_text="hi", fields=[field])
    action = BrowserAction(action_type=ActionType.FILL_TEXT, target_selector="#x", value="v")
    result = BrowserTaskResult(observation=obs, avg_confidence=0.5)
    restored = BrowserTaskResult.model_validate_json(result.model_dump_json())
    assert restored.observation.fields[0].label == "Full name"
    assert restored.avg_confidence == 0.5
    assert action.action_type == ActionType.FILL_TEXT  # constructed without error


def test_map_field_name_uses_digital_self_person_name():
    ds = _build_test_digital_self()
    field = DetectedField(selector="#name", label="Full name", field_type=FieldType.TEXT)
    action, note = map_field(field, ds, None, None)
    assert action.action_type == ActionType.FILL_TEXT
    assert action.value == ds.person_name
    assert action.confidence >= 0.9


def test_map_field_unknown_text_field_halts_for_approval():
    ds = _build_test_digital_self()
    field = DetectedField(selector="#phone", label="Phone number", field_type=FieldType.TEXT)
    action, _ = map_field(field, ds, None, None)
    assert action.action_type == ActionType.HALT_FOR_APPROVAL
    assert action.value == ""


def test_map_field_select_matches_cto_option_lexically():
    ds = _build_test_digital_self()
    field = DetectedField(
        selector="#role", label="Desired role", field_type=FieldType.SELECT,
        options=["Individual contributor", "CTO / technical leadership", "Sales"],
    )
    action, _ = map_field(field, ds, None, None)
    assert action.action_type == ActionType.SELECT_OPTION
    assert action.value == "CTO / technical leadership"


def test_map_field_checkbox_is_deferred_to_agent():
    ds = _build_test_digital_self()
    field = DetectedField(selector="#confirm", label="I confirm", field_type=FieldType.CHECKBOX)
    action, note = map_field(field, ds, None, None)
    assert action.action_type == ActionType.HALT_FOR_APPROVAL
    assert note == "deferred"


def test_map_field_textarea_generates_grounded_answer_via_mock_provider():
    ds = _build_test_digital_self()
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    provider = get_provider("mock")
    field = DetectedField(
        selector="#motivation", label="What is your most impactful project, and why?",
        field_type=FieldType.TEXTAREA,
    )
    action, note = map_field(field, ds, index, provider)
    assert action.action_type == ActionType.FILL_TEXT
    assert action.value.strip() != ""
    # Regression guard for the MockProvider header-parsing bug: the raw
    # "FIELD LABEL:" prompt marker must never leak into the generated text.
    assert "FIELD LABEL:" not in action.value


def test_run_application_never_submits_without_explicit_approval():
    """End-to-end: real Chromium against the local synthetic form. Also the
    regression test for both v3 bugs fixed alongside this test suite:
    select-field verification (controller.py) and MockProvider prompt
    parsing (mock_provider.py) — both must show every field verified OK
    with the shipped default (approve_submit=False)."""
    ds = _build_test_digital_self()
    index = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    provider = get_provider("mock")
    result, traj = run_application(
        ds, index, provider, f"file://{FORM_PATH}", approve_submit=False, headless=True,
    )
    assert result.halted_for_approval is True
    assert result.submitted is False
    assert len(result.field_results) == len(result.observation.fields)
    fillable = [
        fr for fr in result.field_results
        if fr.action.action_type in (ActionType.FILL_TEXT, ActionType.SELECT_OPTION)
    ]
    assert fillable  # sanity: at least the name/email/select/textarea fields mapped
    assert all(fr.verified for fr in fillable), [
        (fr.field.label, fr.verification_note) for fr in fillable if not fr.verified
    ]
    stages = [step.stage for step in traj.steps]
    assert "halt_for_approval" in stages
    assert "complete" not in stages  # never reached without approve_submit=True
