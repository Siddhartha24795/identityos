from __future__ import annotations

import os

from .base import EmbeddingProvider
from .hash_provider import HashEmbeddingProvider


def get_embedding_provider(name: str | None = None) -> EmbeddingProvider:
    """Factory, mirroring services/providers/get_provider(). Defaults to
    "hash" (zero-dependency, zero-network) so the pipeline runs everywhere;
    set EMBEDDING_PROVIDER=fastembed (or pass name="fastembed") for real
    semantic embeddings — see docs/evaluation_v2.md for why the reference
    v2.3 numbers use fastembed, not the default.
    """
    name = (name or os.environ.get("EMBEDDING_PROVIDER") or "hash").lower()
    if name == "hash":
        return HashEmbeddingProvider()
    if name == "fastembed":
        from .fastembed_provider import FastEmbedProvider

        return FastEmbedProvider()
    raise ValueError(f"Unknown embedding provider '{name}'. Use one of: hash, fastembed.")


__all__ = ["EmbeddingProvider", "HashEmbeddingProvider", "get_embedding_provider"]
