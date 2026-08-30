#!/usr/bin/env python3
"""Thin CLI wrapper around services/evaluation/run_eval_v2.py.

Usage:
  python scripts/run_eval_v2.py                          # mock LLM, hash embeddings (zero deps)
  python scripts/run_eval_v2.py mock v2_mock hash
  python scripts/run_eval_v2.py mock v2_semantic fastembed  # real semantic embeddings
  python scripts/run_eval_v2.py anthropic v2_real fastembed # requires ANTHROPIC_API_KEY
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from services.evaluation.run_eval_v2 import run  # noqa: E402


def main() -> None:
    provider = sys.argv[1] if len(sys.argv) > 1 else None
    tag = sys.argv[2] if len(sys.argv) > 2 else "latest"
    embedding_provider = sys.argv[3] if len(sys.argv) > 3 else None
    summary = run(provider_name=provider, tag=tag, embedding_provider_name=embedding_provider)
    print(json.dumps(summary["scores"], indent=2))
    print(f"\nFull results: data/evaluation/results/{tag}/")


if __name__ == "__main__":
    main()
