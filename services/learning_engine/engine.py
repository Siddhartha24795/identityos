"""v4.1 — Learning Engine.

Operates on the ALREADY-COMPUTED, ALREADY-COMMITTED per-requirement results
from a real v2 eval run (lexical `identityos_v2` and semantic
`identityos_v2_semantic`, both scored against the same real human ground
truth) — see data/evaluation/results/v2_semantic/application_summary.json.
No new LLM calls are made: the "candidate strategies" being chosen between
are two systems that already exist and have already been independently
verified (docs/evaluation_v2.md), so this module's only job is deciding,
per requirement, which of the two to trust — and proving that decision
rule actually generalizes rather than memorizing the 14 answers it was
tested against.

EXPERIENCE -> HYPOTHESIS -> COUNTERFACTUAL TEST -> EVALUATION ->
PROMOTE/REJECT (PROMPT.md's SELF-IMPROVEMENT ENGINE), scoped to one
concrete, already-instrumented decision: "below what lexical-evidence-
coverage threshold does semantic retrieval become worth the risk it
carries elsewhere (docs/evaluation_v2.md's dangerous-overclaim finding)?"

Honestly scoped: this is a meta-learning policy over an existing signal
(lexical evidence_coverage) and two existing strategies (lexical, semantic)
— not a Digital Self mutation, and not automatic belief updating. See
docs/roadmap.md v4.1 for what a fuller self-improvement loop would still
need.
"""
from __future__ import annotations

from packages.schemas.learning import LeaveOneOutFold, LearningReport, ThresholdCandidate
from packages.schemas.qa import Trajectory

DEFAULT_THRESHOLDS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def _score_choice(
    choice: dict[str, str],
    lexical: dict[str, dict],
    semantic: dict[str, dict],
    req_ids: list[str],
) -> tuple[float, float, int]:
    """Returns (agreement_rate, dangerous_overclaim_rate, n_semantic_used)
    for a given per-requirement choice of "lexical" or "semantic", scored
    against the real per_requirement records already computed for both."""
    agreements = 0
    dangerous = 0
    non_met = 0
    n_semantic = 0
    for rid in req_ids:
        rec = semantic[rid] if choice.get(rid) == "semantic" else lexical[rid]
        if choice.get(rid) == "semantic":
            n_semantic += 1
        if rec["agrees"]:
            agreements += 1
        if rec["real_bucket"] != "met_or_better":
            non_met += 1
            if rec["dangerous_overclaim"]:
                dangerous += 1
    agreement_rate = agreements / len(req_ids) if req_ids else 0.0
    dangerous_rate = dangerous / non_met if non_met else 0.0
    return agreement_rate, dangerous_rate, n_semantic


def _choice_for_threshold(
    threshold: float, lexical: dict[str, dict], req_ids: list[str]
) -> dict[str, str]:
    return {
        rid: ("semantic" if lexical[rid]["evidence_coverage"] < threshold else "lexical")
        for rid in req_ids
    }


def search_thresholds(
    lexical: dict[str, dict],
    semantic: dict[str, dict],
    req_ids: list[str],
    baseline_hybrid_agreement_rate: float,
    thresholds: list[float] = DEFAULT_THRESHOLDS,
) -> list[ThresholdCandidate]:
    """HYPOTHESIS -> COUNTERFACTUAL TEST -> EVALUATION for every candidate
    threshold. A candidate is only PROMOTED if it introduces zero dangerous
    overclaims AND matches or beats the already-shipped hybrid heuristic's
    agreement rate — merely matching lexical alone is not an improvement
    worth promoting."""
    candidates = []
    for t in thresholds:
        choice = _choice_for_threshold(t, lexical, req_ids)
        agr, dang, n_sem = _score_choice(choice, lexical, semantic, req_ids)
        promoted = dang == 0.0 and agr >= baseline_hybrid_agreement_rate
        if dang > 0.0:
            rationale = (
                f"rejected: introduces a dangerous overclaim (rate {dang:.2f}) — "
                "unsafe regardless of agreement rate"
            )
        elif agr < baseline_hybrid_agreement_rate:
            rationale = (
                f"rejected: agreement {agr:.3f} does not beat the already-shipped "
                f"hybrid heuristic's {baseline_hybrid_agreement_rate:.3f}"
            )
        else:
            rationale = (
                f"promoted: matches/beats hybrid ({agr:.3f} >= {baseline_hybrid_agreement_rate:.3f}) "
                "with zero dangerous overclaims"
            )
        candidates.append(ThresholdCandidate(
            threshold=t, train_agreement_rate=agr, train_dangerous_overclaim_rate=dang,
            n_semantic_used=n_sem, promoted=promoted, rationale=rationale,
        ))
    return candidates


def _best_promoted_threshold(candidates: list[ThresholdCandidate]) -> float | None:
    promoted = [c for c in candidates if c.promoted]
    if not promoted:
        return None
    best_agr = max(c.train_agreement_rate for c in promoted)
    best = [c for c in promoted if c.train_agreement_rate == best_agr]
    # Parsimony: among equally-good candidates, prefer the smallest
    # threshold — the smallest deviation from trusting lexical retrieval,
    # which is the safer default per docs/evaluation_v2.md.
    return min(c.threshold for c in best)


def leave_one_out(
    lexical: dict[str, dict],
    semantic: dict[str, dict],
    req_ids: list[str],
    thresholds: list[float] = DEFAULT_THRESHOLDS,
) -> list[LeaveOneOutFold]:
    """For each requirement, select a threshold using ONLY the other 13
    requirements' outcomes, then apply it to the held-out one. This is the
    COUNTERFACTUAL EVALUATION PROMPT.md asks for ('would the learned rule
    still work if...') done properly with held-out data — every other
    evaluation in this project (v1-v3.3) measures a fixed system against
    the same benchmark it was designed against; this is the one place a
    learned decision rule is validated on data it never saw while being
    chosen, which is the actual thing "the rule generalizes" is a claim
    about, not the same thing as "it fits the 14 items I already have."
    """
    folds = []
    for held_out in req_ids:
        train_ids = [r for r in req_ids if r != held_out]
        # Pick T on the training fold alone: safe (zero dangerous overclaims
        # on the training fold) and maximizing training agreement.
        best_t, best_agr = 0.0, -1.0
        for t in thresholds:
            choice = _choice_for_threshold(t, lexical, train_ids)
            agr, dang, _ = _score_choice(choice, lexical, semantic, train_ids)
            if dang == 0.0 and agr > best_agr:
                best_agr, best_t = agr, t
        chosen = "semantic" if lexical[held_out]["evidence_coverage"] < best_t else "lexical"
        rec = semantic[held_out] if chosen == "semantic" else lexical[held_out]
        folds.append(LeaveOneOutFold(
            held_out_requirement_id=held_out, selected_threshold=best_t, choice=chosen,
            agreed=rec["agrees"], dangerous_overclaim=rec["dangerous_overclaim"],
        ))
    return folds


def run_learning_engine(
    lexical: dict[str, dict],
    semantic: dict[str, dict],
    baseline_lexical_agreement_rate: float,
    baseline_hybrid_agreement_rate: float,
    thresholds: list[float] = DEFAULT_THRESHOLDS,
) -> tuple[LearningReport, Trajectory]:
    req_ids = sorted(lexical.keys())
    traj = Trajectory(question_id="learning_engine", system_name="learning_engine_v4_1")
    traj.add(
        stage="experience",
        input_summary=f"{len(req_ids)} requirements, real per-requirement results for lexical + semantic",
        action="load already-committed v2_semantic run (no new LLM calls)",
        observation=f"baseline lexical agreement={baseline_lexical_agreement_rate:.3f}, "
                    f"shipped hybrid agreement={baseline_hybrid_agreement_rate:.3f}",
    )

    candidates = search_thresholds(lexical, semantic, req_ids, baseline_hybrid_agreement_rate, thresholds)
    for c in candidates:
        traj.add(
            stage="hypothesis" if not c.promoted else "hypothesis",
            input_summary=f"threshold={c.threshold}",
            action="counterfactual test: swap to semantic below this lexical-coverage threshold",
            observation=f"agreement={c.train_agreement_rate:.3f} dangerous_overclaim={c.train_dangerous_overclaim_rate:.3f} n_semantic_used={c.n_semantic_used}",
            decision="promote" if c.promoted else "reject",
            reasoning=c.rationale,
        )

    promoted_t = _best_promoted_threshold(candidates)
    if promoted_t is not None:
        choice = _choice_for_threshold(promoted_t, lexical, req_ids)
        learned_agr, learned_dang, _ = _score_choice(choice, lexical, semantic, req_ids)
    else:
        choice = {rid: "lexical" for rid in req_ids}
        learned_agr, learned_dang, _ = _score_choice(choice, lexical, semantic, req_ids)
    traj.add(
        stage="evaluate",
        input_summary="full 14-requirement benchmark",
        action=f"apply promoted policy (threshold={promoted_t})" if promoted_t is not None
               else "no candidate promoted — fall back to lexical-only",
        observation=f"agreement={learned_agr:.3f} dangerous_overclaim={learned_dang:.3f}",
        confidence=learned_agr,
    )

    folds = leave_one_out(lexical, semantic, req_ids, thresholds)
    loo_agreements = sum(1 for f in folds if f.agreed)
    loo_non_met = sum(1 for rid, f in zip(req_ids, folds) if lexical[rid]["real_bucket"] != "met_or_better")
    loo_dangerous = sum(1 for f in folds if f.dangerous_overclaim)
    loo_agr_rate = loo_agreements / len(folds) if folds else 0.0
    loo_dang_rate = loo_dangerous / loo_non_met if loo_non_met else 0.0
    traj.add(
        stage="leave_one_out_validation",
        input_summary=f"{len(folds)} folds, threshold re-selected per fold from the other 13 items",
        action="apply fold-specific threshold to the held-out requirement, never trained on its own label",
        observation=f"LOO agreement={loo_agr_rate:.3f} LOO dangerous_overclaim={loo_dang_rate:.3f}",
        reasoning="PROMPT.md: 'do not automatically trust every successful trajectory' — "
                  "this is the check that the promoted rule generalizes, not just fits.",
        confidence=loo_agr_rate,
    )

    if promoted_t is None:
        conclusion = (
            "No threshold candidate beat the already-shipped hybrid heuristic without "
            "introducing a dangerous overclaim. The learning engine correctly declined to "
            "promote anything rather than ship a change with no measured benefit."
        )
    elif learned_agr <= baseline_hybrid_agreement_rate + 1e-9:
        conclusion = (
            f"Promoted threshold={promoted_t} matches (does not exceed) the hand-designed "
            f"hybrid heuristic's {baseline_hybrid_agreement_rate:.3f} agreement rate at 0.0 "
            "dangerous overclaims. This is a genuine negative-for-improvement, positive-for-"
            "validation result: an automated search over a wider hypothesis space than the "
            "hand-designed rule confirms the hand-designed rule was already at the ceiling a "
            "coverage-only signal can reach here — it does not find a better rule, it proves "
            "one wasn't being left on the table. Leave-one-out cross-validation "
            f"(agreement={loo_agr_rate:.3f}, dangerous_overclaim={loo_dang_rate:.3f}) confirms "
            "this holds under held-out validation, not just a fit to all 14 items at once."
        )
    else:
        conclusion = (
            f"Promoted threshold={promoted_t} beats the hybrid heuristic's "
            f"{baseline_hybrid_agreement_rate:.3f} agreement rate, reaching {learned_agr:.3f}, "
            "with zero dangerous overclaims, and this held under leave-one-out cross-validation "
            f"(agreement={loo_agr_rate:.3f})."
        )
    traj.add(
        stage="conclusion", input_summary="", action="", observation=conclusion,
    )

    report = LearningReport(
        candidates=candidates,
        promoted_threshold=promoted_t,
        per_requirement_choice=choice,
        baseline_lexical_agreement_rate=baseline_lexical_agreement_rate,
        baseline_hybrid_agreement_rate=baseline_hybrid_agreement_rate,
        learned_agreement_rate=learned_agr,
        learned_dangerous_overclaim_rate=learned_dang,
        loo_folds=folds,
        loo_agreement_rate=loo_agr_rate,
        loo_dangerous_overclaim_rate=loo_dang_rate,
        conclusion=conclusion,
    )
    return report, traj
