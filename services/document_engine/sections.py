"""Section plan for a generated cover letter.

Each section has its own retrieval query, deliberately phrased close to
what a real application would ask, so retrieve_hybrid() has real signal
to work with rather than a generic "write a cover letter" prompt.
"""
from __future__ import annotations

COVER_LETTER_SECTIONS: list[tuple[str, str]] = [
    (
        "opening",
        "Why are you a strong fit for a technology leadership role, and what drives you professionally?",
    ),
    (
        "technical_depth",
        "Describe your most significant hands-on technical achievements and engineering work.",
    ),
    (
        "leadership",
        "Describe your leadership experience and how you build, mentor, and manage teams.",
    ),
    (
        "closing",
        "What are your career goals, and why should an employer choose you over another candidate?",
    ),
]
