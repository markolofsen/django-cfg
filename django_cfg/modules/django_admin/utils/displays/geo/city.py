"""City display utility."""
from __future__ import annotations

from typing import Any

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from .._types import CityDisplayConfig


class CityDisplay:
    """
    Display city with state and country in admin list views.

    Shows: Seoul, KR  or  🇰🇷 Seoul, 11, KR
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: CityDisplayConfig | None = None) -> SafeString:
        """
        Render city field with location hierarchy.

        Config: show_flag (True), show_state (True), show_country (True), show_coordinates (False)
        """
        cfg: CityDisplayConfig = config or {}
        value = getattr(obj, field_name, None)

        if not value:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        show_flag = cfg.get("show_flag", True)
        show_state = cfg.get("show_state", True)
        show_country = cfg.get("show_country", True)
        show_coordinates = cfg.get("show_coordinates", False)

        if hasattr(value, "name") and hasattr(value, "country"):
            return cls._format_model(value, show_flag, show_state, show_country, show_coordinates)
        if isinstance(value, int):
            return cls._format_id(value, show_flag, show_state, show_country, show_coordinates)

        return format_html('<span>{}</span>', escape(str(value)))

    @classmethod
    def _format_model(
        cls, city: Any, show_flag: bool, show_state: bool, show_country: bool, show_coordinates: bool,
    ) -> SafeString:
        parts = []

        if show_flag and hasattr(city, "country") and city.country:
            emoji = getattr(city.country, "emoji", "")
            if emoji:
                parts.append(format_html('<span>{}</span>', emoji))

        parts.append(format_html('<span class="font-medium">{}</span>', city.name))

        if show_state and hasattr(city, "state") and city.state:
            state_code = getattr(city.state, "state_code", None) or city.state.name
            parts.append(format_html('<span class="text-base-400">{}</span>', state_code))

        if show_country and hasattr(city, "country") and city.country:
            parts.append(format_html('<span class="text-base-400">{}</span>', city.country.iso2))

        if show_coordinates:
            lat = getattr(city, "latitude", None)
            lon = getattr(city, "longitude", None)
            if lat is not None and lon is not None:
                parts.append(format_html(
                    '<span class="text-xs text-base-400">({:.4f}, {:.4f})</span>', lat, lon,
                ))

        if parts and show_flag and hasattr(city, "country") and city.country and city.country.emoji:
            content = f"{parts[0]} {', '.join(str(p) for p in parts[1:])}"
        else:
            content = ", ".join(str(p) for p in parts)

        return format_html('<span class="flex items-center gap-1">{}</span>', content)

    @classmethod
    def _format_id(
        cls, city_id: int, show_flag: bool, show_state: bool, show_country: bool, show_coordinates: bool,
    ) -> SafeString:
        try:
            from django_cfg.apps.tools.geo.services.database import get_geo_db
            db = get_geo_db()
            city = db.get_city(city_id)
            if city:
                parts = []
                country = db.get_country(city.country_iso2) if city.country_iso2 else None
                state = db.get_state(city.state_id) if city.state_id else None

                if show_flag and country and country.emoji:
                    parts.append(format_html('<span>{}</span>', country.emoji))
                parts.append(format_html('<span class="font-medium">{}</span>', city.name))

                if show_state and state:
                    state_code = state.iso2 or state.name
                    parts.append(format_html('<span class="text-base-400">{}</span>', state_code))
                if show_country and country:
                    parts.append(format_html('<span class="text-base-400">{}</span>', country.iso2))
                if show_coordinates and city.coordinates:
                    lat, lon = city.coordinates
                    parts.append(format_html(
                        '<span class="text-xs text-base-400">({:.4f}, {:.4f})</span>', lat, lon,
                    ))

                if parts and show_flag and country and country.emoji:
                    content = f"{parts[0]} {', '.join(str(p) for p in parts[1:])}"
                else:
                    content = ", ".join(str(p) for p in parts)
                return format_html('<span class="flex items-center gap-1">{}</span>', content)
        except Exception:
            pass
        return format_html('<span>{}</span>', city_id)
