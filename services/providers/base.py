"""Model-provider abstraction (docs/architecture.md - Model Abstraction).

The rest of the system never imports openai/anthropic directly. It calls
`LLMProvider.complete(system, prompt)` so the provider can be swapped via
the PROVIDER env var without touching agent logic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 600) -> str:
        """Return a text completion. Must be side-effect free and safe to
        call repeatedly (the eval harness calls this dozens of times)."""
        raise NotImplementedError
