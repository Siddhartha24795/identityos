#!/usr/bin/env python3
"""Thin CLI wrapper around services/evaluation/run_learning_engine.py.

Usage:
  python scripts/run_learning_engine.py                    # source=v2_semantic, tag=learning_v4_1
  python scripts/run_learning_engine.py v2_semantic learning_v4_1
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from services.evaluation.run_learning_engine import run  # noqa: E402


def main() -> None:
    source = sys.argv[1] if len(sys.argv) > 1 else "v2_semantic"
    tag = sys.argv[2] if len(sys.argv) > 2 else "learning_v4_1"
    result = run(source, tag)
    print(json.dumps(result["report"], indent=2))
    print(f"\nFull results: data/evaluation/results/{tag}/")


if __name__ == "__main__":
    main()
