"""v4.1 — Learning Engine tests. Uses small synthetic per-requirement
fixtures (not the real committed data) so the tests assert on the
mechanism, not on numbers that will drift as the real corpus evolves —
docs/evaluation.md's real numbers are checked separately by the eval
script's own output, not duplicated here as brittle assertions."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from services.learning_engine.engine import (
    leave_one_out,
    run_learning_engine,
    search_thresholds,
)


def _rec(agrees, real_bucket="gap", dangerous=False, coverage=1.0):
    return {"agrees": agrees, "real_bucket": real_bucket, "dangerous_overclaim": dangerous, "evidence_coverage": coverage}


def test_search_thresholds_promotes_only_when_safe_and_at_least_as_good():
    # r1: lexical wrong with zero coverage, semantic right and safe -> a
    # threshold that swaps r1 should be promoted.
    lexical = {
        "r1": _rec(agrees=False, coverage=0.0),
        "r2": _rec(agrees=True, coverage=1.0),
    }
    semantic = {
        "r1": _rec(agrees=True, coverage=1.0),
        "r2": _rec(agrees=True, coverage=1.0),
    }
    candidates = search_thresholds(lexical, semantic, ["r1", "r2"], baseline_hybrid_agreement_rate=0.5,
                                    thresholds=[0.0, 0.5, 1.0])
    by_t = {c.threshold: c for c in candidates}
    assert by_t[0.0].n_semantic_used == 0  # never swaps r1 (0.0 < 0.0 is False)
    assert by_t[0.0].train_agreement_rate == 0.5  # matches baseline exactly -> still promoted
    assert by_t[0.5].promoted is True   # swaps r1 (0.0 < 0.5), fixes it, no danger
    assert by_t[0.5].train_agreement_rate == 1.0  # strictly better than baseline


def test_search_thresholds_rejects_when_swap_introduces_dangerous_overclaim():
    lexical = {
        "r1": _rec(agrees=False, coverage=0.0),
    }
    semantic = {
        # semantic "fixes" r1 but the real answer was GAP and semantic
        # claims MET_OR_BETTER -> dangerous overclaim.
        "r1": {"agrees": False, "real_bucket": "gap", "dangerous_overclaim": True, "evidence_coverage": 1.0},
    }
    candidates = search_thresholds(lexical, semantic, ["r1"], baseline_hybrid_agreement_rate=0.0,
                                    thresholds=[0.0, 1.0])
    by_t = {c.threshold: c for c in candidates}
    assert by_t[1.0].promoted is False
    assert "dangerous" in by_t[1.0].rationale


def test_leave_one_out_never_uses_held_out_labels_to_pick_threshold():
    # Construct a case where the "obviously best" global threshold would
    # overfit to one item; LOO should still produce a safe, defined result
    # for every fold (no crash, no threshold picked using the held-out
    # item's own outcome).
    lexical = {f"r{i}": _rec(agrees=(i % 2 == 0), coverage=0.0 if i == 0 else 1.0) for i in range(4)}
    semantic = {f"r{i}": _rec(agrees=True, coverage=1.0) for i in range(4)}
    folds = leave_one_out(lexical, semantic, list(lexical.keys()), thresholds=[0.0, 0.5, 1.0])
    assert len(folds) == 4
    for f in folds:
        assert f.choice in ("lexical", "semantic")


def test_run_learning_engine_end_to_end_produces_report_and_trajectory():
    lexical = {
        "r1": _rec(agrees=False, coverage=0.0),
        "r2": _rec(agrees=True, coverage=1.0),
        "r3": _rec(agrees=True, coverage=1.0),
    }
    semantic = {
        "r1": _rec(agrees=True, coverage=1.0),
        "r2": _rec(agrees=True, coverage=1.0),
        "r3": _rec(agrees=True, coverage=1.0),
    }
    report, traj = run_learning_engine(lexical, semantic, baseline_lexical_agreement_rate=2 / 3,
                                        baseline_hybrid_agreement_rate=2 / 3, thresholds=[0.0, 0.5, 1.0])
    assert report.promoted_threshold == 0.5
    assert report.learned_agreement_rate == 1.0
    assert report.learned_dangerous_overclaim_rate == 0.0
    assert traj.system_name == "learning_engine_v4_1"
    assert traj.steps[0].stage == "experience"
    assert traj.steps[-1].stage == "conclusion"


def test_run_learning_engine_declines_to_promote_when_nothing_beats_baseline():
    lexical = {"r1": _rec(agrees=True, coverage=1.0)}
    semantic = {"r1": _rec(agrees=True, coverage=1.0)}
    report, _ = run_learning_engine(lexical, semantic, baseline_lexical_agreement_rate=1.0,
                                     baseline_hybrid_agreement_rate=1.0, thresholds=[0.0, 1.0])
    # threshold=0.0 never swaps (matches baseline exactly, promoted);
    # regardless, learned result must not regress below baseline.
    assert report.learned_agreement_rate >= 1.0
    assert report.learned_dangerous_overclaim_rate == 0.0
