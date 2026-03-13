"""
OGLayoutPreset — defines the visual layout of an OG image.

Controls *where* elements are placed (accent bar, branding, content).
Does NOT control colors or fonts — those come from OGImageParams / OGImagePreset.

Built-in presets
----------------
DEFAULT  — accent top, content centered, branding bottom-left
HERO     — accent top, branding top-left, large title anchored bottom
ARTICLE  — no accent bar, branding top-left, title + desc centered
MINIMAL  — no accent bar, no branding, pure title + desc centered
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AccentPosition = Literal["top", "bottom", "none"]
BrandPosition = Literal["top-left", "top-right", "bottom-left", "bottom-right", "none"]
ContentAlign = Literal["center", "start", "end"]


@dataclass(frozen=True)
class OGLayoutPreset:
    """Visual layout configuration for an OG image.

    Attributes:
        name:                  Slug identifier used in cache keys.
        accent_position:       Thin colored bar placement, or "none" to hide.
        brand_position:        Corner for logo + site_name, or "none" to hide.
        content_align:         Vertical alignment of title/description block.
        padding_x:             Horizontal padding (left/right) in pixels.
        padding_y:             Vertical padding (top/bottom) in pixels.
        logo_size:             Logo square size in pixels.
        site_name_font_size:   Font size for the site_name label.
        title_font_size:       Font size for the title.
        description_font_size: Font size for the description.
    """

    name: str

    accent_position: AccentPosition = "top"
    brand_position: BrandPosition = "bottom-left"
    content_align: ContentAlign = "center"

    padding_x: int = 60
    padding_y: int = 60

    logo_size: int = 40
    site_name_font_size: int = 26
    title_font_size: int = 68
    description_font_size: int = 30


# ── Built-in presets ──────────────────────────────────────────────────────────

DEFAULT = OGLayoutPreset(
    name="default",
    accent_position="top",
    brand_position="bottom-left",
    content_align="center",
)
"""Accent bar at top. Content centered. Branding bottom-left."""

HERO = OGLayoutPreset(
    name="hero",
    accent_position="top",
    brand_position="top-left",
    content_align="end",
    title_font_size=80,
    description_font_size=32,
)
"""Accent bar at top. Branding top-left. Large title anchored to the bottom."""

ARTICLE = OGLayoutPreset(
    name="article",
    accent_position="none",
    brand_position="top-left",
    content_align="center",
    title_font_size=60,
    description_font_size=28,
)
"""No accent bar. Branding top-left. Title + description centered."""

MINIMAL = OGLayoutPreset(
    name="minimal",
    accent_position="none",
    brand_position="none",
    content_align="center",
    title_font_size=72,
    description_font_size=30,
)
"""No accent bar. No branding. Pure title + description."""


# ── Registry ──────────────────────────────────────────────────────────────────

ALL: dict[str, OGLayoutPreset] = {
    p.name: p for p in [DEFAULT, HERO, ARTICLE, MINIMAL]
}


def get_layout(name: str) -> OGLayoutPreset:
    """Return a layout preset by slug name. Raises ValueError if not found."""
    try:
        return ALL[name]
    except KeyError:
        available = ", ".join(sorted(ALL))
        raise ValueError(f"Unknown layout: {name!r}. Available: {available}")


def corner_to_fixed_pos(position: BrandPosition, px: int, py: int) -> dict[str, int]:
    """Convert a BrandPosition corner name to pictex fixed_position kwargs."""
    edge_y = py + 8
    if position == "top-left":
        return {"top": edge_y, "left": px}
    if position == "top-right":
        return {"top": edge_y, "right": px}
    if position == "bottom-left":
        return {"bottom": edge_y, "left": px}
    # bottom-right
    return {"bottom": edge_y, "right": px}
