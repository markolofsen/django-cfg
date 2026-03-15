from __future__ import annotations

from typing import Literal

from ._base import OGImagePreset

_DEFAULT_TEXT: dict[str, str] = {
    "dark": "#ffffff",
    "light": "#111827",
}


def build_preset(
    name: str,
    primary_color: str,
    secondary_color: str,
    accent_color: str,
    style: Literal["dark", "light"] = "dark",
    text_color: str | None = None,
    size: Literal["1200x630", "1200x600", "800x418", "1200x1200"] = "1200x630",
) -> OGImagePreset:
    """Build a custom OGImagePreset programmatically.

    Args:
        name:            Unique identifier for this preset.
        primary_color:   Background color (hex).
        secondary_color: Secondary / gradient background color (hex).
        accent_color:    Accent / highlight color (hex).
        style:           "dark" or "light" — controls renderer style mode.
        text_color:      Text color (hex). Auto-inferred from style if None.
        size:            Output size. Default "1200x630".

    Returns:
        Frozen OGImagePreset instance.

    Example::

        MY_BRAND = build_preset("brand", "#0f0c29", "#302b63", "#e91e63")
        url = get_or_create_og_url(MY_BRAND.to_params(title="My Brand Page"))
    """
    resolved_text = text_color if text_color is not None else _DEFAULT_TEXT[style]
    return OGImagePreset(
        name=name,
        bg_color=primary_color,
        bg_color2=secondary_color,
        text_color=resolved_text,
        accent_color=accent_color,
        style=style,
        size=size,
    )
