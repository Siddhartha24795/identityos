"""Real semantic embeddings via fastembed (ONNX runtime, no torch — chosen
specifically for footprint: ~65MB model cache, no GPU, no API key, no
per-call cost). Model downloads once on first use; cached under
data/.embedding_cache/ so a second run doesn't re-download.
"""
from __future__ import annotations

from pathlib import Path

from .base import EmbeddingProvider

_CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / ".embedding_cache"
_MODEL_NAME = "BAAI/bge-small-en-v1.5"


class FastEmbedProvider(EmbeddingProvider):
    name = "fastembed"

    def __init__(self, model_name: str = _MODEL_NAME):
        from fastembed import TextEmbedding  # local import: optional dependency

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(_CACHE_DIR))

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self._model.embed(texts)]
