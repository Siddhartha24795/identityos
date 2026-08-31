"""v4.1 — runs the Learning Engine against an already-committed v2 eval
run's per-requirement results (lexical + semantic, scored against real
human ground truth) and writes:
  - data/evaluation/results/<tag>/learning_report.json
  - data/evaluation/results/<tag>/trajectories/learning_engine__learning_engine_v4_1.{md,json}

No new LLM calls: this operates entirely on already-recorded outcomes from
`data/evaluation/results/<source_tag>/application_summary.json` (default
"v2_semantic", the only committed run with real, non-hash semantic
embeddings — see docs/evaluation_v2.md for why hash embeddings would make
this meaningless).

Baselines (lexical and hybrid agreement rates) are recomputed directly from
the unrounded per-requirement `agrees` counts, NOT read from the summary's
pre-rounded `agreement_rate` field — a real bug caught while building this:
comparing a full-precision computed rate (10/14 = 0.714285...) against a
pre-rounded JSON value (0.714) produced a false "the learned policy beats
hybrid" verdict, when it actually matches exactly. See
docs/improvement_changelog.md's v4.1 entry.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from services.learning_engine.engine import DEFAULT_THRESHOLDS, run_learning_engine

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"


def _agreement_rate(per_req: dict[str, dict]) -> float:
    n = len(per_req)
    return sum(1 for v in per_req.values() if v["agrees"]) / n if n else 0.0


def run(source_tag: str = "v2_semantic", tag: str = "learning_v4_1") -> dict:
    source_path = RESULTS_DIR / source_tag / "application_summary.json"
    if not source_path.exists():
        raise RuntimeError(
            f"No source eval run found at {source_path}. Run "
            f"`make eval-v2-semantic` first (writes tag 'v2_semantic')."
        )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    per_req = source["per_requirement"]
    lexical = per_req["identityos_v2"]
    semantic = per_req["identityos_v2_semantic"]
    hybrid = per_req["identityos_v2_hybrid"]

    baseline_lexical_agreement_rate = _agreement_rate(lexical)
    baseline_hybrid_agreement_rate = _agreement_rate(hybrid)

    report, traj = run_learning_engine(
        lexical, semantic, baseline_lexical_agreement_rate, baseline_hybrid_agreement_rate,
        thresholds=DEFAULT_THRESHOLDS,
    )

    run_dir = RESULTS_DIR / tag
    traj_dir = run_dir / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    stem = f"learning_engine__{traj.system_name}"
    (traj_dir / f"{stem}.md").write_text(traj.to_markdown(), encoding="utf-8")
    (traj_dir / f"{stem}.json").write_text(traj.model_dump_json(indent=2), encoding="utf-8")

    out = {
        "source_tag": source_tag,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report": report.model_dump(mode="json"),
    }
    (run_dir / "learning_report.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    source_arg = sys.argv[1] if len(sys.argv) > 1 else "v2_semantic"
    tag_arg = sys.argv[2] if len(sys.argv) > 2 else "learning_v4_1"
    result = run(source_arg, tag_arg)
    print(json.dumps(result["report"], indent=2))
