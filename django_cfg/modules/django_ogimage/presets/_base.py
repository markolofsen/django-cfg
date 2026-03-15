from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class OGImagePreset(BaseModel):
    """
    Frozen, reusable set of visual parameters for OG image rendering.

    Usage:
        url = get_or_create_og_url(DARK_BLUE.to_params(title="Hello"))
        url = get_or_create_og_url(OGImageParams(title="Hello", **DARK_BLUE.as_dict()))
    """

    model_config = ConfigDict(frozen=True)

    name: str
    bg_color: str
    bg_color2: str
    text_color: str
    accent_color: str
    style: Literal["dark", "light"] = "dark"
    size: Literal["1200x630", "1200x600", "800x418", "1200x1200"] = "1200x630"

    @field_validator("bg_color", "bg_color2", "text_color", "accent_color", mode="before")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("#") or len(v) not in (4, 7):
            raise ValueError(f"Invalid hex color: {v!r}")
        return v.lower()

    def as_dict(self) -> dict:
        """Visual fields only (no name) — safe to spread into OGImageParams."""
        return self.model_dump(exclude={"name"})

    def to_params(
        self,
        title: str,
        description: str = "",
        locale: str = "en",
    ):
        """Create OGImageParams from this preset + content fields."""
        from django_cfg.modules.django_ogimage.core.params import OGImageParams
        return OGImageParams(
            title=title,
            description=description,
            locale=locale,
            **self.as_dict(),
        )
