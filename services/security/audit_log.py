"""v3.2 — append-only audit log for every consequential browser action.
JSON Lines, one ActionRecord per line, written to
data/evaluation/results/<tag>/security_audit.jsonl by
services/browser_engine/agent.py. Never holds a secret by construction —
see packages/schemas/security.py's ActionRecord docstring.
"""
from __future__ import annotations

from pathlib import Path

from packages.schemas.security import ActionRecord


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.records: list[ActionRecord] = []

    def record(self, entry: ActionRecord) -> None:
        self.records.append(entry)

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            for r in self.records:
                f.write(r.model_dump_json() + "\n")
