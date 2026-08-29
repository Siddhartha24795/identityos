#!/usr/bin/env python3
"""Build Digital Self v1 from the structured source documents in
data/identity_sources/, plus the v1 hand-seeded belief set, and persist it
via services/identity_engine/store.py.

Idempotent by design: this always (re)writes version 1 in place. Versioning
(store.save_new_version, with a diff) is for a future script that adds a
*new* source to an *existing* Digital Self — running the same ingestion
over the same static sources twice should not produce a fake "v2" that
differs from v1 by zero facts.

Usage: python scripts/build_digital_self.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from services.identity_engine import ingest, seed_beliefs, store  # noqa: E402

SOURCE_DIR = REPO_ROOT / "data" / "identity_sources"


def main() -> None:
    sources = sorted(SOURCE_DIR.glob("*.md"))
    if not sources:
        raise SystemExit(f"No source documents found in {SOURCE_DIR}")

    ds = ingest.build_digital_self(sources, person_name="Siddhartha Mishra", version=1)
    ds.beliefs = seed_beliefs.seed_beliefs(ds)
    store.save(ds)

    print(f"Built Digital Self v{ds.version}: {len(ds.facts)} facts, {len(ds.beliefs)} beliefs.")
    print(f"Saved to data/digital_self/v{ds.version}.json")


if __name__ == "__main__":
    main()
