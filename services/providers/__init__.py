from __future__ import annotations

import os

from .base import LLMProvider
from .mock_provider import MockProvider


def get_provider(name: str | None = None) -> LLMProvider:
    """Factory selecting a provider by name or the PROVIDER env var.
    Defaults to "mock" so the system runs with zero configuration.
    """
    name = (name or os.environ.get("PROVIDER") or "mock").lower()
    if name == "mock":
        return MockProvider()
    if name == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider()
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    raise ValueError(f"Unknown provider '{name}'. Use one of: mock, openai, anthropic.")


__all__ = ["LLMProvider", "MockProvider", "get_provider"]
