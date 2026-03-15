"""
django_cf.core.types — shared D1 result type used across all modules.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class D1QueryResult(BaseModel):
    """Result of a D1 query execution."""

    model_config = ConfigDict(extra="ignore")

    success: bool = False
    changes: int = 0
    rows_written: int = 0
    rows_read: int = 0
    duration_ms: float = 0.0
    results: list[Any] = Field(default_factory=list)

    @classmethod
    def from_sdk_page(cls, page: Any) -> "D1QueryResult":
        meta = page.meta
        return cls(
            success=bool(page.success),
            changes=int(meta.changes or 0) if meta else 0,
            rows_written=int(meta.rows_written or 0) if meta else 0,
            rows_read=int(meta.rows_read or 0) if meta else 0,
            duration_ms=float(meta.duration or 0.0) if meta else 0.0,
            results=list(page.results or []),
        )


__all__ = ["D1QueryResult"]
