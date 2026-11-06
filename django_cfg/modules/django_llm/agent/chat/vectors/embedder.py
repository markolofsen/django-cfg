"""The embedder seam: a callable `list[str] -> list[list[float]]` (one vector per text, `[]` for "no vector, skip").

The default is `django_llm.embed_texts` (OpenRouter, `openai/text-embedding-3-small`, multilingual, 1536 dims) in batches. Tests pass
their own callable, so nothing here needs the network. It already refuses a mock vector (returns `[]`), so a keyless host stores
nothing instead of noise.
"""

from __future__ import annotations

from collections.abc import Callable

Embedder = Callable[[list[str]], list[list[float]]]

DEFAULT_MODEL = "openai/text-embedding-3-small"
BATCH = 64


def llm_embedder(model: str = DEFAULT_MODEL) -> Embedder:
    from django_cfg.modules.django_llm.features.embeddings import EMBEDDING_DIMENSIONS, embed_texts

    def embed(texts: list[str]) -> list[list[float]]:
        return embed_texts(texts, model=model, dimensions=EMBEDDING_DIMENSIONS)

    return embed


def embed_batched(embed: Embedder, texts: list[str], batch: int = BATCH) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), batch):
        part = texts[i : i + batch]
        vectors = embed(part)
        if len(vectors) != len(part):
            raise ValueError("the embedder must return one vector per text")
        out.extend(vectors)
    return out
