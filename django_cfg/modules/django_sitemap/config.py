"""SitemapConfig — runtime knobs for the sitemap module."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SitemapConfig(BaseModel):
    enabled: bool = True
    default_page_size: int = Field(default=50_000, ge=1, le=50_000)
    cache_index_seconds: int = Field(default=300, ge=0)
    cache_feed_seconds: int = Field(default=3600, ge=0)
    cache_version: str = "v1"
    use_reltuples_threshold: int = Field(default=100_000, ge=0)


_INSTANCE: SitemapConfig | None = None


def get_sitemap_config() -> SitemapConfig:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = SitemapConfig()
    return _INSTANCE


def set_sitemap_config(cfg: SitemapConfig) -> None:
    global _INSTANCE
    _INSTANCE = cfg
