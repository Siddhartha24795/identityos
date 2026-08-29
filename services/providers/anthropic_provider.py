from __future__ import annotations

import os

from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str | None = None):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Set it in .env or use PROVIDER=mock."
            )
        from anthropic import Anthropic  # local import: keep it optional at package import time

        self._client = Anthropic(api_key=api_key)
        self._model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

    def complete(self, system: str, prompt: str, max_tokens: int = 600) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [block.text for block in resp.content if getattr(block, "type", "") == "text"]
        return "".join(parts)
