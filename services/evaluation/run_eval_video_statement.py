"""v4.2 — generates one video statement SCRIPT with each of baseline_plain,
baseline_rag, and identityos_video_v4_2 (hybrid retrieval + narrative-state
tracking, reused unmodified from services/document_engine), scores every
one with the same verifier as v1/v2/v2.5, and writes:
  - data/evaluation/results/<tag>/documents/<system>_video_statement.md   (the actual script)
  - data/evaluation/results/<tag>/video_statement_summary.json            (scored comparison)
  - data/evaluation/results/<tag>/trajectories/video_statement__<system>.{md,json}

This produces a SCRIPT only. See services/video_engine/generate.py's module
docstring and services/video_engine/render.py for the scope boundary: no
synthetic likeness of the applicant is ever generated.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from services.embeddings import get_embedding_provider
from services.identity_engine import store
from services.providers import get_provider
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex
from services.video_engine.generate import (
    generate_video_statement_baseline_plain,
    generate_video_statement_baseline_rag,
    generate_video_statement_identityos,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"


def run(
    provider_name: str | None = None,
    tag: str = "latest",
    embedding_provider_name: str | None = None,
) -> dict:
    provider = get_provider(provider_name)
    embedding_provider = get_embedding_provider(embedding_provider_name)
    ds = store.load_latest()
    if ds.version == 0:
        raise RuntimeError(
            "No Digital Self found. Run `python scripts/build_digital_self.py` first."
        )
    embedding_index = DigitalSelfEmbeddingIndex(ds, embedding_provider)

    run_dir = RESULTS_DIR / tag
    traj_dir = run_dir / "trajectories"
    docs_dir = run_dir / "documents"
    traj_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    doc_plain, traj_plain = generate_video_statement_baseline_plain(provider)
    doc_rag, traj_rag = generate_video_statement_baseline_rag(ds, provider)
    doc_sys, traj_sys = generate_video_statement_identityos(ds, embedding_index, provider)

    documents = {"baseline_plain": doc_plain, "baseline_rag": doc_rag, "identityos_video_v4_2": doc_sys}
    trajectories = {"baseline_plain": traj_plain, "baseline_rag": traj_rag, "identityos_video_v4_2": traj_sys}

    for name, traj in trajectories.items():
        stem = f"video_statement__{name}"
        (traj_dir / f"{stem}.md").write_text(traj.to_markdown(), encoding="utf-8")
        (traj_dir / f"{stem}.json").write_text(traj.model_dump_json(indent=2), encoding="utf-8")

    for name, doc in documents.items():
        (docs_dir / f"{name}_video_statement.md").write_text(doc.full_text, encoding="utf-8")

    (run_dir / "video_statement_answers.json").write_text(
        json.dumps({name: d.model_dump(mode="json") for name, d in documents.items()}, indent=2),
        encoding="utf-8",
    )

    summary = {
        "document_type": "video_statement",
        "note": "script only -- no synthetic likeness of the applicant is generated, see services/video_engine/generate.py",
        "provider": provider.name,
        "embedding_provider": embedding_provider.name,
        "digital_self_version": ds.version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scores": {
            name: {
                "avg_evidence_coverage": round(d.avg_evidence_coverage, 3),
                "avg_unsupported_claim_rate": round(d.avg_unsupported_claim_rate, 3),
                "repeated_evidence_rate": round(d.repeated_evidence_rate, 3),
                "n_sections": len(d.sections),
            }
            for name, d in documents.items()
        },
    }
    (run_dir / "video_statement_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    provider_arg = sys.argv[1] if len(sys.argv) > 1 else None
    tag_arg = sys.argv[2] if len(sys.argv) > 2 else "latest"
    embedding_arg = sys.argv[3] if len(sys.argv) > 3 else None
    result = run(provider_arg, tag_arg, embedding_arg)
    print(json.dumps(result["scores"], indent=2))
