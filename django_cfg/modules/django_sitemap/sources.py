"""Pydantic model for declaring a sitemap source.

Apps register `SitemapSource` instances by calling `register(...)` from
their `sitemap_sources.py` module. The registry is read at request time
by the index/feed views.
"""
from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SitemapSource(BaseModel):
    """One queryset → many sitemap URLs.

    The `queryset_factory` is a zero-arg callable that returns a fresh
    queryset on every call. Lazy by design — apps register sources at
    import time, but database access happens only when a request hits.
    """

    name: str = Field(..., min_length=1, max_length=64)
    url_template: str = Field(..., min_length=1)
    queryset_factory: Callable[[], Any]
    fields: dict[str, str] = Field(default_factory=dict)
    lastmod_field: str | None = None
    cursor_fields: tuple[str, ...] = Field(..., min_length=1)
    order: str
    page_size: int = Field(default=50_000, ge=1, le=50_000)
    enabled: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("name")
    @classmethod
    def _name_slug(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("source name must be alphanumeric / underscore / hyphen")
        return v


def resolve_field(obj: Any, dotted: str) -> Any:
    """Walk a dotted attribute path. No defaults — missing field raises."""
    for part in dotted.split("."):
        obj = getattr(obj, part)
    return obj
