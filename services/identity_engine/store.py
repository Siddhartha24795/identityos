"""Digital Self persistence and versioning (docs/architecture.md - Digital
Self Versioning). v1 storage is flat JSON files: data/digital_self/v{n}.json
plus data/digital_self/diffs/v{a}_to_v{b}.json. Migrating to Postgres/graph
is a v5 concern once multiple concurrent users and edge types justify it.
"""
from __future__ import annotations

import json
from pathlib import Path

from packages.schemas.identity import DigitalSelf, DigitalSelfDiff

STORE_DIR = Path(__file__).resolve().parents[2] / "data" / "digital_self"
DIFF_DIR = STORE_DIR / "diffs"


def save(ds: DigitalSelf) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORE_DIR / f"v{ds.version}.json"
    path.write_text(ds.model_dump_json(indent=2), encoding="utf-8")
    return path


def load(version: int) -> DigitalSelf:
    path = STORE_DIR / f"v{version}.json"
    return DigitalSelf.model_validate_json(path.read_text(encoding="utf-8"))


def latest_version() -> int:
    if not STORE_DIR.exists():
        return 0
    versions = [
        int(p.stem[1:]) for p in STORE_DIR.glob("v*.json") if p.stem[1:].isdigit()
    ]
    return max(versions, default=0)


def load_latest() -> DigitalSelf:
    return load(latest_version())


def save_new_version(ds: DigitalSelf, reason: str) -> DigitalSelfDiff:
    prev_version = latest_version()
    ds.version = prev_version + 1
    save(ds)

    prev_fact_ids: set[str] = set()
    prev_belief_ids: set[str] = set()
    if prev_version > 0:
        prev = load(prev_version)
        prev_fact_ids = {f.id for f in prev.facts}
        prev_belief_ids = {b.id for b in prev.beliefs}

    diff = DigitalSelfDiff(
        from_version=prev_version,
        to_version=ds.version,
        added_fact_ids=[f.id for f in ds.facts if f.id not in prev_fact_ids],
        added_belief_ids=[b.id for b in ds.beliefs if b.id not in prev_belief_ids],
        reason=reason,
    )
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    diff_path = DIFF_DIR / f"v{diff.from_version}_to_v{diff.to_version}.json"
    diff_path.write_text(diff.model_dump_json(indent=2), encoding="utf-8")
    return diff
