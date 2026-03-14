"""Coordinates display utility."""
from __future__ import annotations

from typing import Any

from django.utils.html import format_html
from django.utils.safestring import SafeString

from .._types import CoordinatesDisplayConfig


class CoordinatesDisplay:
    """
    Display coordinates in admin list views.

    Shows: 37.5665, 126.9780  (optionally linked to Google Maps)
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: CoordinatesDisplayConfig | None = None) -> SafeString:
        """
        Render coordinates field.

        Config: lat_field ("latitude"), lon_field ("longitude"), precision (4), show_link (False)
        """
        cfg: CoordinatesDisplayConfig = config or {}

        lat_field = cfg.get("lat_field", "latitude")
        lon_field = cfg.get("lon_field", "longitude")
        precision = cfg.get("precision", 4)
        show_link = cfg.get("show_link", False)

        lat = getattr(obj, lat_field, None)
        lon = getattr(obj, lon_field, None)

        if lat is None or lon is None:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        formatted = f"{lat:.{precision}f}, {lon:.{precision}f}"

        if show_link:
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            return format_html(
                '<a href="{}" target="_blank" class="text-primary-600 hover:underline font-mono text-sm">{}</a>',
                maps_url, formatted,
            )

        return format_html('<span class="font-mono text-sm">{}</span>', formatted)
