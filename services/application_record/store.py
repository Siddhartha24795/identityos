"""v3.2 — persists an ApplicationRecord (packages/schemas/application_record.py)
for every browser-automation run, so a person can look back at exactly
what was told to a specific employer once they reach interview stage.

Written automatically by services/browser_engine/agent.py at the end of
every run_application() call — not opt-in, since the whole point is that
nothing gets forgotten. Two files per application: a machine-readable
`.json` and a human-readable `.md` (the actual "what did I say" crib
sheet), both under data/applications/history/.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from packages.schemas.application_record import ApplicationRecord, QAEntry
from packages.schemas.browser import ActionType, BrowserTaskResult

REPO_ROOT = Path(__file__).resolve().parents[2]
HISTORY_DIR = REPO_ROOT / "data" / "applications" / "history"

_FILLABLE = {ActionType.FILL_TEXT, ActionType.SELECT_OPTION, ActionType.CHECK}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "application"


def build_application_record(result: BrowserTaskResult, form_url: str) -> ApplicationRecord:
    app_id = f"{_slugify(result.observation.title or form_url)}__{int(time.time())}"
    entries = [
        QAEntry(
            field_label=fr.field.label,
            field_type=fr.field.field_type.value,
            answer=fr.filled_value,
            evidence_refs=fr.action.evidence_refs,
            confidence=fr.action.confidence,
            verified=fr.verified,
            halted=fr.action.action_type not in _FILLABLE,
        )
        for fr in result.field_results
    ]
    return ApplicationRecord(
        application_id=app_id,
        form_url=form_url,
        form_title=result.observation.title,
        entries=entries,
        submitted=result.submitted,
        halted_for_approval=result.halted_for_approval,
    )


def save_application_record(
    result: BrowserTaskResult, form_url: str, history_dir: Path = HISTORY_DIR
) -> Path:
    record = build_application_record(result, form_url)
    history_dir.mkdir(parents=True, exist_ok=True)
    json_path = history_dir / f"{record.application_id}.json"
    md_path = history_dir / f"{record.application_id}.md"
    json_path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(record.to_markdown(), encoding="utf-8")
    return json_path


def load_application_history(history_dir: Path = HISTORY_DIR) -> list[ApplicationRecord]:
    """For a future cross-application-consistency check (docs/roadmap.md
    v3.2+) — not consumed anywhere yet, but the history is being recorded
    from v3.2 onward so that check has real data to compare against
    whenever it's built."""
    if not history_dir.exists():
        return []
    records = []
    for path in sorted(history_dir.glob("*.json")):
        records.append(ApplicationRecord.model_validate_json(path.read_text(encoding="utf-8")))
    return records
