#!/usr/bin/env python3
"""Thin CLI wrapper around services/evaluation/run_eval_browser.py.

Usage:
  python scripts/run_browser_demo.py                          # mock LLM, hash embeddings, headless, never submits
  python scripts/run_browser_demo.py mock browser_mock fastembed
  python scripts/run_browser_demo.py anthropic browser_real fastembed --approve-submit
  python scripts/run_browser_demo.py mock browser_headed hash --headed   # watch it in a real browser window

--approve-submit is the ONLY way the demo form's submit button gets
clicked, and it is off by default — this is the human-approval checkpoint
required by the hackathon's ground rule 4, implemented as an explicit,
separate flag rather than something the agent can decide on its own.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")  # PROVIDER / *_API_KEY / EMBEDDING_PROVIDER, if present

from services.evaluation.run_eval_browser import run  # noqa: E402


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}

    provider = args[0] if len(args) > 0 else None
    tag = args[1] if len(args) > 1 else "latest"
    embedding_provider = args[2] if len(args) > 2 else None
    approve_submit = "--approve-submit" in flags
    headless = "--headed" not in flags

    summary = run(
        provider_name=provider,
        tag=tag,
        embedding_provider_name=embedding_provider,
        approve_submit=approve_submit,
        headless=headless,
    )
    print(json.dumps(summary, indent=2))
    print(f"\nFull results: data/evaluation/results/{tag}/")


if __name__ == "__main__":
    main()
