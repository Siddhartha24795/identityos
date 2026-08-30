#!/usr/bin/env python3
"""v3.2 — runs the mixed-attack local demo form
(data/applications/local_demo/adversarial_mixed.html: two legitimate
fields alongside a prompt-injection attempt, an identity-verification
question, and an off-topic decoy field) plus the CAPTCHA-widget fixture,
and writes real, reproducible evidence for docs/security_spec.md's own
demo requirement: detect, explain, block/escalate, recover, and continue
the legitimate workflow — in one run, not asserted from a unit test alone.

Usage: python scripts/run_security_demo.py [provider] [tag] [embedding_provider]
Never passes approve_submit=True — same reproducibility posture as
scripts/run_browser_demo.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")  # PROVIDER / *_API_KEY / EMBEDDING_PROVIDER, if present

from services.browser_engine.agent import run_application  # noqa: E402
from services.embeddings import get_embedding_provider  # noqa: E402
from services.identity_engine import store  # noqa: E402
from services.providers import get_provider  # noqa: E402
from services.qa_engine.retrieval import DigitalSelfEmbeddingIndex  # noqa: E402

FORMS_DIR = REPO_ROOT / "data" / "applications" / "local_demo"
RESULTS_DIR = REPO_ROOT / "data" / "evaluation" / "results"


def _summarize(result) -> dict:
    return {
        "n_fields": len(result.observation.fields),
        "halted_for_approval": result.halted_for_approval,
        "submitted": result.submitted,
        "fields": [
            {
                "label": fr.field.label,
                "action": fr.action.action_type.value,
                "filled_value": fr.filled_value[:80],
                "verified": fr.verified,
                "rationale": fr.action.rationale,
            }
            for fr in result.field_results
        ],
    }


def main() -> None:
    provider_name = sys.argv[1] if len(sys.argv) > 1 else None
    tag = sys.argv[2] if len(sys.argv) > 2 else "security_demo"
    embedding_name = sys.argv[3] if len(sys.argv) > 3 else None

    provider = get_provider(provider_name)
    embedding_provider = get_embedding_provider(embedding_name)
    ds = store.load_latest()
    if ds.version == 0:
        raise RuntimeError("No Digital Self found. Run `python scripts/build_digital_self.py` first.")
    index = DigitalSelfEmbeddingIndex(ds, embedding_provider)

    run_dir = RESULTS_DIR / tag
    run_dir.mkdir(parents=True, exist_ok=True)

    scenarios = {
        "mixed_attacks": FORMS_DIR / "adversarial_mixed.html",
        "captcha_widget": FORMS_DIR / "adversarial_captcha.html",
    }
    report = {}
    for name, form_path in scenarios.items():
        result, traj = run_application(
            ds, index, provider, f"file://{form_path}",
            approve_submit=False, headless=True,
            audit_log_path=run_dir / f"{name}_audit.jsonl",
        )
        (run_dir / f"{name}_trajectory.md").write_text(traj.to_markdown(), encoding="utf-8")
        report[name] = _summarize(result)

    (run_dir / "security_demo_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nFull results: {run_dir}/")


if __name__ == "__main__":
    main()
