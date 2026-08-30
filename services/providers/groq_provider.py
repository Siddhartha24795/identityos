"""Groq — a free, no-credit-card real-LLM option for testing this system
with actual model quality rather than the deterministic MockProvider (see
docs/evaluation.md for why the mock provider alone doesn't prove
generation quality). Groq's API is OpenAI-compatible, so this reuses the
`openai` client library already a dependency of this repo (for
OpenAIProvider) pointed at Groq's endpoint instead of OpenAI's — no new
package, no new abstraction.

Free tier (as of writing, verify at https://console.groq.com/docs/rate-limits
since providers change limits without notice): no credit card required,
rate-limited per organization (not per key) rather than metered by spend.

Token efficiency (found by actually running this, not assumed): the
default model, `openai/gpt-oss-120b`, is a reasoning model that spends
part of its `max_tokens` budget on hidden chain-of-thought before writing
the visible answer. Measured directly: with no `reasoning_effort` set
(the API's own default, "high"), a real question from this project's own
benchmark consumed 585 of a 600-token budget on reasoning alone, leaving
almost nothing for the actual answer and truncating it mid-sentence.
Setting `reasoning_effort="low"` cut that to single digits to a few dozen
tokens in side-by-side testing, at no observed loss of answer quality on
this project's short, structured completions (cited factual answers, form
fields) — full comparison: docs/evaluation.md's real-model section. This
is NOT a claim that "low" is always the right setting for every task;
it's what was measured for this workload. Override via `GROQ_REASONING_EFFORT`
(one of "low"/"medium"/"high", or "" to omit the parameter entirely — e.g.
for a non-reasoning Groq model that doesn't accept it).
"""
from __future__ import annotations

import os

from .base import LLMProvider

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_DEFAULT_MODEL = "openai/gpt-oss-120b"
_DEFAULT_REASONING_EFFORT = "low"


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self, model: str | None = None, reasoning_effort: str | None = None):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Get a free key (no credit card) at "
                "https://console.groq.com/keys, set it in .env, or use PROVIDER=mock."
            )
        from openai import OpenAI  # local import: keep it optional at package import time

        self._client = OpenAI(api_key=api_key, base_url=_GROQ_BASE_URL)
        self._model = model or os.environ.get("GROQ_MODEL", _DEFAULT_MODEL)
        self._reasoning_effort = (
            reasoning_effort
            if reasoning_effort is not None
            else os.environ.get("GROQ_REASONING_EFFORT", _DEFAULT_REASONING_EFFORT)
        )

    def complete(self, system: str, prompt: str, max_tokens: int = 600) -> str:
        kwargs = {}
        if self._reasoning_effort:
            kwargs["reasoning_effort"] = self._reasoning_effort
        resp = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            **kwargs,
        )
        return resp.choices[0].message.content or ""
