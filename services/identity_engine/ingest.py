"""Identity ingestion: structured markdown sources -> Fact objects.

v1 design choice: source documents are pre-structured markdown with
"## CATEGORY" headers over one-fact-per-line bullets, rather than raw
freeform PDFs/HTML parsed by an LLM. This keeps fact extraction 100%
deterministic and reproducible with zero API calls (see docs/roadmap.md
for why this is v1-scoped: v2 adds an LLM-assisted extractor for
unstructured sources like raw LinkedIn/GitHub HTML).

Every Fact's evidence points back to (file, line range, exact snippet).
"""
from __future__ import annotations

import re
from pathlib import Path

from packages.schemas.identity import DigitalSelf, Evidence, Fact, FactCategory

_HEADER_RE = re.compile(r"^##\s+([A-Z_\- ]+)\s*$")

_CATEGORY_MAP = {
    "EMPLOYMENT": FactCategory.EMPLOYMENT,
    "EDUCATION": FactCategory.EDUCATION,
    "SKILL": FactCategory.SKILL,
    "ACHIEVEMENT": FactCategory.ACHIEVEMENT,
    "PROJECT": FactCategory.PROJECT,
    "SELF-ASSESSED GAP": FactCategory.OTHER,
    "BELIEF-RELEVANT STATEMENT": FactCategory.OTHER,
    "REQUIREMENT EVIDENCE": FactCategory.OTHER,
    # v2.5: this section is strategy/proposal narrative written FOR the
    # IITACB CEO candidature specifically (see data/identity_sources/
    # dossier_narrative.md) — real and true, but not general evidence
    # about the person, so document generation for any other target
    # should not draw on it by default. docs/hot_take.md v2.5 addendum.
    "STRATEGY AND ACCOUNTABILITY": FactCategory.APPLICATION_SPECIFIC,
}


def parse_markdown_facts(path: Path) -> list[Fact]:
    """Parse one structured markdown source file into Facts with provenance."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    facts: list[Fact] = []
    current_category: FactCategory | None = None
    fact_counter = 0

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("<!--") or line.startswith("-->"):
            continue
        header = _HEADER_RE.match(line)
        if header:
            current_category = _CATEGORY_MAP.get(header.group(1).strip(), FactCategory.OTHER)
            continue
        if current_category is None:
            continue

        fact_counter += 1
        fid = f"{path.stem}:{fact_counter:03d}"
        facts.append(
            Fact(
                id=fid,
                text=line,
                category=current_category,
                confidence=0.99,  # directly transcribed from the source document
                evidence=[
                    Evidence(
                        id=f"{fid}:ev1",
                        source_document=path.name,
                        locator=f"line {i}",
                        snippet=line,
                    )
                ],
            )
        )
    return facts


def build_digital_self(
    source_paths: list[Path], person_name: str, version: int = 1
) -> DigitalSelf:
    all_facts: list[Fact] = []
    for p in source_paths:
        all_facts.extend(parse_markdown_facts(p))
    return DigitalSelf(
        version=version,
        person_name=person_name,
        facts=all_facts,
        source_documents=[p.name for p in source_paths],
    )
