"""v4.2 — section plan for a generated video statement script.

Many real applications ask for a video, not just text: a research-program
"introduce yourself" video, a fellowship pitch, an accelerator application
video. This is the same section-planning approach as
services/document_engine/sections.py, applied to that shape of ask instead
of a cover letter — see services/video_engine/generate.py's module
docstring for what this does and, explicitly, does not produce.
"""
from __future__ import annotations

VIDEO_STATEMENT_SECTIONS: list[tuple[str, str]] = [
    (
        "introduction",
        "Introduce yourself: who you are, and the core thread that connects your work.",
    ),
    (
        "motivation",
        "What research problem or mission are you most motivated to work on, and why?",
    ),
    (
        "key_achievement",
        "Describe one concrete piece of work that best demonstrates your ability to do this.",
    ),
    (
        "closing",
        "What do you want this specific program or audience to take away, and what are you asking for?",
    ),
]
