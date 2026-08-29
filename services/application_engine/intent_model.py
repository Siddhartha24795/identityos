"""v2 — loads a real ApplicationIntentModel: one job description's
requirements, each paired with the real human's own prior self-assessment
and evidence (ground truth, not fabricated). See
data/applications/iitacb_ceo/requirements.json.
"""
from __future__ import annotations

import json
from pathlib import Path

from packages.schemas.application import ApplicationRequirement


def load_requirements(path: Path) -> list[ApplicationRequirement]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ApplicationRequirement.model_validate(r) for r in raw]
