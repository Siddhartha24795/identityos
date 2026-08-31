#!/usr/bin/env python3
"""Thin CLI wrapper around services/evaluation/run_orchestrator_demo.py.

Usage:
  python scripts/run_orchestrator_demo.py                        # mock LLM, hash embeddings
  python scripts/run_orchestrator_demo.py mock orchestrator_demo fastembed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")

from services.evaluation.run_orchestrator_demo import run  # noqa: E402


def main() -> None:
    provider = sys.argv[1] if len(sys.argv) > 1 else None
    tag = sys.argv[2] if len(sys.argv) > 2 else "orchestrator_demo"
    embedding_provider = sys.argv[3] if len(sys.argv) > 3 else None

    summary = run(provider_name=provider, tag=tag, embedding_provider_name=embedding_provider)
    print(json.dumps(summary, indent=2))
    print(f"\nFull results: data/evaluation/results/{tag}/")


if __name__ == "__main__":
    main()
