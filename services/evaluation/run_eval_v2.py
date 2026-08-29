"""Runs all three requirement-fit assessors over the real 14-requirement
IITACB CEO application, scores each against the REAL human's own prior
self-assessment, and writes the same shape of artifacts as v1:
  - data/evaluation/results/<tag>/application_answers.json
  - data/evaluation/results/<tag>/application_summary.json
  - data/evaluation/results/<tag>/trajectories/req*__<system>.{md,json}
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from services.application_engine.assess import (
    assess_baseline_plain,
    assess_baseline_rag,
    assess_identityos,
)
from services.application_engine.intent_model import load_requirements
from services.evaluation.scoring import score_application_system
from services.identity_engine import store
from services.providers import get_provider

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_PATH = REPO_ROOT / "data" / "applications" / "iitacb_ceo" / "requirements.json"
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"


def run(provider_name: str | None = None, tag: str = "latest") -> dict:
    provider = get_provider(provider_name)
    ds = store.load_latest()
    if ds.version == 0:
        raise RuntimeError(
            "No Digital Self found. Run `python scripts/build_digital_self.py` first."
        )
    requirements = load_requirements(REQUIREMENTS_PATH)
    requirements_by_id = {r.id: r for r in requirements}

    run_dir = RESULTS_DIR / tag
    traj_dir = run_dir / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)

    all_assessments: dict[str, list] = {
        "baseline_plain": [],
        "baseline_rag": [],
        "identityos_v2": [],
    }

    for req in requirements:
        a_plain, t_plain = assess_baseline_plain(req, provider)
        a_rag, t_rag = assess_baseline_rag(req, ds, provider)
        a_sys, t_sys = assess_identityos(req, ds, provider)

        all_assessments["baseline_plain"].append(a_plain)
        all_assessments["baseline_rag"].append(a_rag)
        all_assessments["identityos_v2"].append(a_sys)

        for traj in (t_plain, t_rag, t_sys):
            stem = f"{req.id}__{traj.system_name}"
            (traj_dir / f"{stem}.md").write_text(traj.to_markdown(), encoding="utf-8")
            (traj_dir / f"{stem}.json").write_text(
                traj.model_dump_json(indent=2), encoding="utf-8"
            )

    scores = {
        name: score_application_system(name, assessments, requirements_by_id)
        for name, assessments in all_assessments.items()
    }

    answers_out = {
        name: [a.model_dump(mode="json") for a in assessments]
        for name, assessments in all_assessments.items()
    }
    (run_dir / "application_answers.json").write_text(
        json.dumps(answers_out, indent=2), encoding="utf-8"
    )

    summary = {
        "application": "IITACB CEO candidature — 14 real requirements",
        "provider": provider.name,
        "digital_self_version": ds.version,
        "n_requirements": len(requirements),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scores": {
            name: {
                "n_requirements": s.n_requirements,
                "agreements": s.agreements,
                "agreement_rate": round(s.agreement_rate, 3),
                "avg_evidence_coverage": round(s.avg_evidence_coverage, 3),
                "non_met_requirements": s.non_met_requirements,
                "dangerous_overclaims": s.dangerous_overclaims,
                "dangerous_overclaim_rate": round(s.dangerous_overclaim_rate, 3),
            }
            for name, s in scores.items()
        },
        "per_requirement": {name: s.per_requirement for name, s in scores.items()},
    }
    (run_dir / "application_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    provider_arg = sys.argv[1] if len(sys.argv) > 1 else None
    tag_arg = sys.argv[2] if len(sys.argv) > 2 else "latest"
    result = run(provider_arg, tag_arg)
    print(json.dumps(result["scores"], indent=2))
