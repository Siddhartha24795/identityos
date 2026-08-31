"""v4.0 — runs three representative requests through the orchestrator, one
per agent target (QA, application-fit, browser-fill), and writes:
  - data/evaluation/results/<tag>/orchestrator_decisions.json
  - data/evaluation/results/<tag>/trajectories/orchestrator__*.{md,json}
    (the orchestrator's own routing trajectory)
  - data/evaluation/results/<tag>/trajectories/<downstream>__*.{md,json}
    (the routed agent's own trajectory, unmodified)

Demonstrates that the orchestrator dispatches into the real, already-tested
agents rather than a fourth thing built just for this demo.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from services.embeddings import get_embedding_provider
from services.identity_engine import store
from services.orchestrator.router import route_and_execute
from services.providers import get_provider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"
LOCAL_FORM = REPO_ROOT / "data" / "applications" / "local_demo" / "application_form.html"

_REQUESTS = [
    ("orchestrator_demo_01", "What failure taught you the most in your career?", None),
    (
        "orchestrator_demo_02",
        "Does the candidate meet the requirement for deep, hands-on distributed systems experience at scale?",
        None,
    ),
    ("orchestrator_demo_03", "Please fill out the application form for this role", f"file://{LOCAL_FORM}"),
]


def run(
    provider_name: str | None = None,
    tag: str = "orchestrator_demo",
    embedding_provider_name: str | None = None,
) -> dict:
    provider = get_provider(provider_name)
    embedding_provider = get_embedding_provider(embedding_provider_name)
    ds = store.load_latest()
    if ds.version == 0:
        raise RuntimeError("No Digital Self found. Run `python scripts/build_digital_self.py` first.")
    embedding_index = DigitalSelfEmbeddingIndex(ds, embedding_provider)

    run_dir = RESULTS_DIR / tag
    traj_dir = run_dir / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)

    decisions_out = []
    for request_id, text, form_url in _REQUESTS:
        decision, result, orch_traj, downstream_traj = route_and_execute(
            text, ds, embedding_index, provider, form_url=form_url, headless=True,
        )
        orch_traj.question_id = request_id
        downstream_traj.question_id = request_id

        for traj in (orch_traj, downstream_traj):
            stem = f"{request_id}__{traj.system_name}"
            (traj_dir / f"{stem}.md").write_text(traj.to_markdown(), encoding="utf-8")
            (traj_dir / f"{stem}.json").write_text(traj.model_dump_json(indent=2), encoding="utf-8")

        result_summary: dict = {"result_type": type(result).__name__}
        if hasattr(result, "text"):
            result_summary["text"] = result.text[:300]
        if hasattr(result, "overall_confidence"):
            result_summary["overall_confidence"] = round(result.overall_confidence, 3)
        if hasattr(result, "halted_for_approval"):
            result_summary["halted_for_approval"] = result.halted_for_approval
            result_summary["submitted"] = result.submitted

        decisions_out.append({
            "request_id": request_id,
            "request_text": text,
            "target": decision.target.value,
            "matched_signal": decision.matched_signal,
            "confidence": decision.confidence,
            "result_summary": result_summary,
        })

    summary = {
        "provider": provider.name,
        "embedding_provider": embedding_provider.name,
        "digital_self_version": ds.version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions_out,
    }
    (run_dir / "orchestrator_decisions.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    import sys

    provider_arg = sys.argv[1] if len(sys.argv) > 1 else None
    tag_arg = sys.argv[2] if len(sys.argv) > 2 else "orchestrator_demo"
    embedding_arg = sys.argv[3] if len(sys.argv) > 3 else None
    result = run(provider_arg, tag_arg, embedding_arg)
    print(json.dumps(result, indent=2))
