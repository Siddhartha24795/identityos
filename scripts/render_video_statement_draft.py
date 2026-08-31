#!/usr/bin/env python3
"""Renders a narrated DRAFT .mp4 for an already-generated video statement
script (see scripts/run_eval_video_statement.py, which must be run first).

This is a SEPARATE, opt-in step from script generation on purpose: it
needs two optional system tools not required by any other IdentityOS
command --

  pico2wave   Debian/Ubuntu: apt-get install libttspico-utils
  ffmpeg      Debian/Ubuntu: apt-get install ffmpeg

-- so `make setup` / `make test` never depend on them. The output is a
timing/content draft only, never a submission-ready video: no synthetic
likeness of the applicant is generated, and every slide carries a
burned-in disclosure banner. See services/video_engine/generate.py and
render.py for the full scope boundary, and docs/architecture.md's v4.2
addendum for why.

Usage:
  python scripts/render_video_statement_draft.py <tag> [system_name]
  python scripts/render_video_statement_draft.py video_statement_mock identityos_video_v4_2
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.schemas.document import GeneratedDocument  # noqa: E402
from services.video_engine.render import render_narrated_draft  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/render_video_statement_draft.py <tag> [system_name]")
    tag = sys.argv[1]
    system_name = sys.argv[2] if len(sys.argv) > 2 else "identityos_video_v4_2"

    run_dir = REPO_ROOT / "data" / "evaluation" / "results" / tag
    answers_path = run_dir / "video_statement_answers.json"
    if not answers_path.exists():
        raise SystemExit(
            f"No {answers_path} found. Run "
            f"`python scripts/run_eval_video_statement.py mock {tag} fastembed` first."
        )
    data = json.loads(answers_path.read_text(encoding="utf-8"))
    if system_name not in data:
        raise SystemExit(f"System '{system_name}' not found in {answers_path}. Options: {list(data)}")
    doc = GeneratedDocument(**data[system_name])

    result = render_narrated_draft(doc, run_dir, tag)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
