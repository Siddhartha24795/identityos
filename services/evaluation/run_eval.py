"""Runs all three systems (baseline_plain, baseline_rag, identityos_v1) over
the full question bank, verifies + scores every answer, and writes:
  - data/evaluation/results/<tag>/answers.json      (every generated answer)
  - data/evaluation/results/<tag>/summary.json      (aggregate scores)
  - data/evaluation/results/<tag>/trajectories/*.md  (human-readable trajectories)
  - data/evaluation/results/<tag>/trajectories/*.json (structured trajectories)

This is the single source of truth behind docs/evaluation.md and
docs/improvement_changelog.md — every number in those docs was produced by
this script, not hand-written.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from packages.schemas.qa import Question
from services.identity_engine import store
from services.providers import get_provider
from services.qa_engine.baseline_plain import answer_baseline_plain
from services.qa_engine.baseline_rag import answer_baseline_rag
from services.qa_engine.identityos_agent import answer_identityos
from services.evaluation.scoring import score_system

REPO_ROOT = Path(__file__).resolve().parents[2]
QUESTION_BANK_PATH = REPO_ROOT / "data" / "evaluation" / "question_bank.json"
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"


def load_questions() -> list[Question]:
    raw = json.loads(QUESTION_BANK_PATH.read_text(encoding="utf-8"))
    return [Question.model_validate(q) for q in raw]


def run(provider_name: str | None = None, tag: str = "latest") -> dict:
    provider = get_provider(provider_name)
    ds = store.load_latest()
    if ds.version == 0:
        raise RuntimeError(
            "No Digital Self found. Run `python scripts/build_digital_self.py` first."
        )
    questions = load_questions()

    run_dir = RESULTS_DIR / tag
    traj_dir = run_dir / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)

    all_answers: dict[str, list] = {
        "baseline_plain": [],
        "baseline_rag": [],
        "identityos_v1": [],
    }

    for q in questions:
        ans_plain, traj_plain = answer_baseline_plain(q, provider)
        ans_rag, traj_rag = answer_baseline_rag(q, ds, provider)
        ans_sys, traj_sys = answer_identityos(q, ds, provider)

        all_answers["baseline_plain"].append(ans_plain)
        all_answers["baseline_rag"].append(ans_rag)
        all_answers["identityos_v1"].append(ans_sys)

        for traj in (traj_plain, traj_rag, traj_sys):
            stem = f"{q.id}__{traj.system_name}"
            (traj_dir / f"{stem}.md").write_text(traj.to_markdown(), encoding="utf-8")
            (traj_dir / f"{stem}.json").write_text(
                traj.model_dump_json(indent=2), encoding="utf-8"
            )

    scores = {name: score_system(name, answers) for name, answers in all_answers.items()}

    answers_out = {
        name: [a.model_dump(mode="json") for a in answers]
        for name, answers in all_answers.items()
    }
    (run_dir / "answers.json").write_text(json.dumps(answers_out, indent=2), encoding="utf-8")

    summary = {
        "provider": provider.name,
        "digital_self_version": ds.version,
        "n_questions": len(questions),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scores": {
            name: {
                "n_questions": s.n_questions,
                "avg_evidence_coverage": round(s.avg_evidence_coverage, 3),
                "avg_unsupported_claim_rate": round(s.avg_unsupported_claim_rate, 3),
                "hard_cases_seen": s.hard_cases_seen,
                "hard_cases_overclaimed": s.hard_cases_overclaimed,
                "hard_case_overclaim_rate": round(s.hard_case_overclaim_rate, 3),
                "refusal_count": s.refusal_count,
                "identity_fidelity_score": round(s.identity_fidelity_score, 3),
            }
            for name, s in scores.items()
        },
        "per_question": {name: s.per_question for name, s in scores.items()},
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    provider_arg = sys.argv[1] if len(sys.argv) > 1 else None
    tag_arg = sys.argv[2] if len(sys.argv) > 2 else "latest"
    result = run(provider_arg, tag_arg)
    print(json.dumps(result["scores"], indent=2))
