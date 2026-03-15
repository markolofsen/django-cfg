from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from django_cfg.core.utils.cache import CacheKey


class OGImageParams(BaseModel):
    """Parameters that define a unique OG image.

    Excluded from cache_key: page_url.
    """

    # Content
    title: str = Field(..., max_length=300)
    description: str = Field("", max_length=600)
    locale: str = Field("en", max_length=10)  # BCP 47: "en", "ko", "ar", "ja"

    # Canvas style
    bg_color: str = "#1a1a2e"
    bg_color2: str = "#16213e"
    text_color: str = "#ffffff"
    accent_color: str = "#3b82f6"
    style: Literal["dark", "light"] = "dark"

    # Canvas size
    size: str = "1200x630"

    # Logging only — excluded from cache_key
    page_url: str = Field("", max_length=2048)

    @field_validator("locale")
    @classmethod
    def normalize_locale(cls, v: str) -> str:
        return v.strip().lower().replace("_", "-")

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: str) -> str:
        allowed = {"1200x630", "1200x600", "800x418", "1200x1200"}
        return v if v in allowed else "1200x630"

    def cache_stable_dict(self) -> dict:
        """Dict used for cache key — excludes page_url."""
        return self.model_dump(exclude={"page_url"}, mode="json")

    @property
    def width(self) -> int:
        return int(self.size.split("x")[0])

    @property
    def height(self) -> int:
        return int(self.size.split("x")[1])


def compute_cache_key(params: OGImageParams) -> str:
    """SHA256[:40] of the stable (non-logging) params."""
    return CacheKey.from_dict(params.cache_stable_dict())
