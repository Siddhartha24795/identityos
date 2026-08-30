"""v3 — runs the browser agent once against the local synthetic
application form and writes:
  - data/evaluation/results/<tag>/browser_result.json
  - data/evaluation/results/<tag>/trajectories/browser_demo__identityos_browser_v3.{md,json}

approve_submit defaults to False and is never set true by this harness —
that decision is scripts/run_browser_demo.py's, made explicitly on the
command line by a human, never by the eval harness itself.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from services.browser_engine.agent import run_application
from services.embeddings import get_embedding_provider
from services.identity_engine import store
from services.providers import get_provider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex

REPO_ROOT = Path(__file__).resolve().parents[2]
FORM_PATH = REPO_ROOT / "data" / "applications" / "local_demo" / "application_form.html"
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"


def run(
    provider_name: str | None = None,
    tag: str = "latest",
    embedding_provider_name: str | None = None,
    approve_submit: bool = False,
    headless: bool = True,
) -> dict:
    provider = get_provider(provider_name)
    embedding_provider = get_embedding_provider(embedding_provider_name)
    ds = store.load_latest()
    if ds.version == 0:
        raise RuntimeError(
            "No Digital Self found. Run `python scripts/build_digital_self.py` first."
        )
    embedding_index = DigitalSelfEmbeddingIndex(ds, embedding_provider)
    form_url = f"file://{FORM_PATH}"

    run_dir = RESULTS_DIR / tag
    traj_dir = run_dir / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)

    result, traj = run_application(
        ds, embedding_index, provider, form_url, approve_submit=approve_submit, headless=headless,
        audit_log_path=run_dir / "security_audit.jsonl",
    )

    stem = "browser_demo__identityos_browser_v3"
    (traj_dir / f"{stem}.md").write_text(traj.to_markdown(), encoding="utf-8")
    (traj_dir / f"{stem}.json").write_text(traj.model_dump_json(indent=2), encoding="utf-8")

    result_out = result.model_dump(mode="json")
    (run_dir / "browser_result.json").write_text(json.dumps(result_out, indent=2), encoding="utf-8")

    summary = {
        "provider": provider.name,
        "embedding_provider": embedding_provider.name,
        "digital_self_version": ds.version,
        "n_fields": len(result.observation.fields),
        "n_filled": sum(1 for fr in result.field_results if fr.filled_value),
        "n_verified": sum(1 for fr in result.field_results if fr.verified),
        "avg_evidence_coverage": round(result.avg_evidence_coverage, 3),
        "avg_confidence": round(result.avg_confidence, 3),
        "halted_for_approval": result.halted_for_approval,
        "submitted": result.submitted,
    }
    return summary


if __name__ == "__main__":
    provider_arg = sys.argv[1] if len(sys.argv) > 1 else None
    tag_arg = sys.argv[2] if len(sys.argv) > 2 else "latest"
    embedding_arg = sys.argv[3] if len(sys.argv) > 3 else None
    result = run(provider_arg, tag_arg, embedding_arg)
    print(json.dumps(result, indent=2))
