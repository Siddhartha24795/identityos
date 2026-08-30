#!/usr/bin/env python3
"""Thin CLI wrapper around services/evaluation/run_eval.py.

Usage:
  python scripts/run_eval.py                 # mock provider, tag "latest"
  python scripts/run_eval.py mock v1_baseline
  python scripts/run_eval.py anthropic v2_real_llm   # requires ANTHROPIC_API_KEY
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")  # PROVIDER / *_API_KEY / EMBEDDING_PROVIDER, if present

from services.evaluation.run_eval import run  # noqa: E402


def main() -> None:
    provider = sys.argv[1] if len(sys.argv) > 1 else None
    tag = sys.argv[2] if len(sys.argv) > 2 else "latest"
    summary = run(provider_name=provider, tag=tag)
    print(json.dumps(summary["scores"], indent=2))
    print(f"\nFull results: data/evaluation/results/{tag}/")


if __name__ == "__main__":
    main()
