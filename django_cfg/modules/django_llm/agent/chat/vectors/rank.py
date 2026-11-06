"""Cosine ranking in Python: the storage strategy of the library (vectors in a JSON column, ranked in memory over a bounded,
owner-scoped candidate set). A host on pgvector overrides the `embedding` column and ranks in SQL; see `@docs/vectorisation.md`."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import TypeVar

T = TypeVar("T")


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def top(query: Sequence[float], items: Iterable[tuple[T, Sequence[float]]], limit: int, min_score: float = 0.0) -> list[tuple[T, float]]:
    scored = [(item, cosine(query, vec)) for item, vec in items]
    scored = [(i, s) for i, s in scored if s > min_score]
    scored.sort(key=lambda p: p[1], reverse=True)
    return scored[:limit]
