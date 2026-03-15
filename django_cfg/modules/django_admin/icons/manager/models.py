"""Pydantic v2 models for Material Icons data."""
from __future__ import annotations

from pydantic import BaseModel, Field


class IconMeta(BaseModel):
    """Metadata for a single Material Icon from Google Fonts API."""

    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: int = 1
    popularity: int = 0


# Type aliases
IconCodepoints = dict[str, str]       # icon_name → hex codepoint
IconMetaMap = dict[str, IconMeta]     # icon_name → IconMeta
IconCategories = dict[str, list[str]] # category_name → sorted icon names
