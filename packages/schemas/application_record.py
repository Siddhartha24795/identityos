"""v3.2 — a per-application record of every question this agent answered
on a person's behalf and what it answered, so that later — at interview
stage, weeks or months on — the person can check what they actually told
a specific employer rather than relying on memory. This is also a
minimal, real instance of the security spec's APPLICATION_MEMORY concept
(docs/security_spec.md's DATA ISOLATION section): each record is scoped
to one application, not merged into one global answer store, which is
what a future cross-application-consistency check (docs/roadmap.md v3.2+)
would need to compare against.
"""
from __future__ import annotations

import time

from pydantic import BaseModel, Field


class QAEntry(BaseModel):
    field_label: str
    field_type: str
    answer: str
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    verified: bool = False
    halted: bool = False


class ApplicationRecord(BaseModel):
    application_id: str
    form_url: str
    form_title: str = ""
    created_at: float = Field(default_factory=time.time)
    entries: list[QAEntry] = Field(default_factory=list)
    submitted: bool = False
    halted_for_approval: bool = True

    def to_markdown(self) -> str:
        lines = [
            f"# Application record — {self.form_title or self.form_url}",
            "",
            f"- Form: {self.form_url}",
            f"- Recorded: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.created_at))}",
            f"- Submitted: {self.submitted}",
            "",
            "## Questions asked and answers given",
            "",
        ]
        for e in self.entries:
            lines.append(f"**{e.field_label}** ({e.field_type})")
            if e.halted:
                lines.append("- _Halted for human review — no answer was submitted for this field._")
            else:
                lines.append(f"- Answer: {e.answer}")
                lines.append(
                    f"- Confidence: {e.confidence:.2f}, verified: {e.verified}, "
                    f"evidence: {', '.join(e.evidence_refs) or 'none'}"
                )
            lines.append("")
        return "\n".join(lines)
