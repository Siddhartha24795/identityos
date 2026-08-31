"""v4.0 — Orchestrator tests: classification is deterministic and
auditable, and each routed target actually dispatches into its real,
already-tested agent (not a mock of it)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.orchestrator import AgentTarget
from services.embeddings.hash_provider import HashEmbeddingProvider
from services.identity_engine import ingest, seed_beliefs
from services.orchestrator.router import classify_intent, route_and_execute
from services.providers.mock_provider import MockProvider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"


def _build_test_digital_self():
    sources = sorted(SOURCE_DIR.glob("*.md"))
    ds = ingest.build_digital_self(sources, person_name="Test", version=99)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    return ds


def test_classify_intent_routes_question_to_qa():
    d = classify_intent("What failure taught you the most in your career?")
    assert d.target == AgentTarget.QA


def test_classify_intent_routes_requirement_language_to_application_fit():
    d = classify_intent("Does the candidate meet the requirement for distributed systems experience?")
    assert d.target == AgentTarget.APPLICATION_FIT


def test_classify_intent_routes_form_language_to_browser_fill():
    d = classify_intent("Please fill out the application form at file:///tmp/form.html")
    assert d.target == AgentTarget.BROWSER_FILL


def test_classify_intent_browser_pattern_wins_over_fit_pattern():
    # Names both a "requirement" and a form-fill verb — filling is the more
    # specific, more consequential action, so it must win.
    d = classify_intent("Fill out the application form, checking every requirement first")
    assert d.target == AgentTarget.BROWSER_FILL


def test_route_and_execute_qa_dispatches_real_agent():
    ds = _build_test_digital_self()
    provider = MockProvider()
    idx = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    decision, result, orch_traj, downstream_traj = route_and_execute(
        "What failure taught you the most in your career?", ds, idx, provider,
    )
    assert decision.target == AgentTarget.QA
    assert downstream_traj.system_name == "identityos_v1"
    assert result.text
    assert orch_traj.steps[0].stage == "classify_intent"
    assert orch_traj.steps[-1].stage == "dispatch"


def test_route_and_execute_application_fit_dispatches_real_agent():
    ds = _build_test_digital_self()
    provider = MockProvider()
    idx = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    decision, result, orch_traj, downstream_traj = route_and_execute(
        "Does the candidate meet the requirement for distributed systems experience?",
        ds, idx, provider,
    )
    assert decision.target == AgentTarget.APPLICATION_FIT
    assert downstream_traj.system_name == "identityos_v2_hybrid"
    assert result.requirement_id == "orchestrated_requirement"


def test_route_and_execute_browser_fill_requires_form_url():
    ds = _build_test_digital_self()
    provider = MockProvider()
    idx = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    try:
        route_and_execute("Please fill out the application form", ds, idx, provider)
        assert False, "expected ValueError for missing form_url"
    except ValueError:
        pass


def test_route_and_execute_browser_fill_dispatches_real_agent(tmp_path):
    ds = _build_test_digital_self()
    provider = MockProvider()
    idx = DigitalSelfEmbeddingIndex(ds, HashEmbeddingProvider())
    form_path = REPO_ROOT / "data" / "applications" / "local_demo" / "application_form.html"
    decision, result, orch_traj, downstream_traj = route_and_execute(
        "Please fill out the application form", ds, idx, provider,
        form_url=f"file://{form_path}", history_dir=tmp_path,
    )
    assert decision.target == AgentTarget.BROWSER_FILL
    assert result.halted_for_approval is True
    assert result.submitted is False
