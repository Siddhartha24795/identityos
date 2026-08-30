"""Embedding-provider abstraction (docs/roadmap.md v2.3), mirroring
services/providers/'s LLM abstraction: the rest of the system calls
`EmbeddingProvider.embed(texts)` and never imports a specific backend
directly, so it can be swapped via the EMBEDDING_PROVIDER env var.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    name: str = "base"

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, same order."""
        raise NotImplementedError
