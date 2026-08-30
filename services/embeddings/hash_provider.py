"""Zero-dependency, zero-network embedding fallback.

This is NOT a semantic embedding model — it's a deterministic character
trigram hash ("feature hashing" / the hashing trick) into a fixed-size
vector. It catches morphological variants that exact lexical-word-overlap
retrieval misses (e.g. "communication" / "communicate" share trigrams) but
has no synonym or concept understanding at all — "entrepreneurial mindset"
and "comfortable with ambiguity" will NOT score meaningfully similar here,
because they share no character substrings. It exists purely so the
pipeline runs everywhere with zero setup, the same role MockProvider plays
for LLM generation (services/providers/mock_provider.py). The real
capability under test lives in fastembed_provider.py.
"""
from __future__ import annotations

import hashlib
import math
import re

from .base import EmbeddingProvider

_DIM = 256


def _trigrams(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    padded = f" {normalized} "
    return [padded[i : i + 3] for i in range(len(padded) - 2)]


def _hash_vector(text: str) -> list[float]:
    vec = [0.0] * _DIM
    for tri in _trigrams(text):
        idx = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16) % _DIM
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


class HashEmbeddingProvider(EmbeddingProvider):
    name = "hash"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [_hash_vector(t) for t in texts]
