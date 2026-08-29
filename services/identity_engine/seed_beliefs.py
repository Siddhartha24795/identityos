"""v1 belief seeding.

Belief inference (turning many facts into a preference/value statement) is
a genuinely hard reasoning step — the mega-prompt's "Belief Model" agent.
Automating it well needs a real LLM pass with counter-evidence search, which
is scoped to v2 (docs/roadmap.md). For v1 we hand-curate a small, honestly
sourced belief set so the confidence-gating and contradiction-detection
machinery downstream has real material to operate on, rather than inventing
placeholder beliefs. Every belief below is grounded in specific facts already
ingested, and one is deliberately paired with counter-evidence pulled from
the dossier's own self-assessed gap section — this is the case the eval
question bank's "contradictory" category exercises.
"""
from __future__ import annotations

from packages.schemas.identity import Belief, DigitalSelf


def _find_ids(ds: DigitalSelf, *keywords: str) -> list[str]:
    keywords_lower = [k.lower() for k in keywords]
    return [
        f.id
        for f in ds.facts
        if any(k in f.text.lower() for k in keywords_lower)
    ]


def seed_beliefs(ds: DigitalSelf) -> list[Belief]:
    beliefs: list[Belief] = []

    beliefs.append(
        Belief(
            id="belief:001",
            statement="Prefers technically unsolved, zero-to-one problems over routine engineering maintenance.",
            supporting_evidence=_find_ids(
                ds, "Generative Image Dynamics", "2000+ concurrent RTSP", "hackathon",
                "zero-to-one",
            ),
            confidence=0.86,
            source_refs=["resume.md", "dossier_excerpts.md"],
        )
    )

    beliefs.append(
        Belief(
            id="belief:002",
            statement="Values shipping working systems into production over research for its own sake.",
            supporting_evidence=_find_ids(
                ds, "Chief Technical Officer", "eval-driven release discipline",
                "POS-occupancy eval",
            ),
            confidence=0.82,
            source_refs=["resume.md", "dossier_excerpts.md"],
        )
    )

    beliefs.append(
        Belief(
            id="belief:003",
            statement="Considers himself an experienced builder and leader of professional/membership institutions, not just engineering teams.",
            supporting_evidence=_find_ids(ds, "Core Member of the IIT", "headed four student chapters"),
            counter_evidence=_find_ids(
                ds, "no prior record of building or running a professional membership body"
            ),
            confidence=0.45,  # deliberately MODERATE/WEAK: real counter-evidence exists
            source_refs=["dossier_excerpts.md"],
        )
    )

    beliefs.append(
        Belief(
            id="belief:004",
            statement="Is comfortable claiming full personal credit for joint work without qualification.",
            supporting_evidence=[],
            counter_evidence=_find_ids(ds, "75%", "co-inventor who is not named"),
            confidence=0.10,  # explicitly a LOW-confidence / rejected belief
            source_refs=["dossier_excerpts.md"],
        )
    )

    return beliefs
