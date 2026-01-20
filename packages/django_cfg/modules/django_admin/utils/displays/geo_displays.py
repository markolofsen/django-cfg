"""
Geographic data display utilities for admin list views.

Provides formatted display of country, city, and location data with flags and styling.
"""

from typing import Any, Dict, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class CountryDisplay:
    """
    Display country with flag emoji in admin list views.

    Shows: 🇰🇷 South Korea
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: Dict[str, Any]) -> SafeString:
        """
        Render country field with flag.

        Config options:
            show_flag: bool - Show flag emoji (default: True)
            show_name: bool - Show full country name (default: True)
            show_code: bool - Show ISO2 code (default: False)
        """
        value = getattr(obj, field_name, None)

        if not value:
            return format_html(
                '<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>'
            )

        show_flag = config.get("show_flag", True)
        show_name = config.get("show_name", True)
        show_code = config.get("show_code", False)

        # Handle Country model instance
        if hasattr(value, "iso2"):
            return cls._format_model(value, show_flag, show_name, show_code)

        # Handle ISO2 code string
        if isinstance(value, str) and len(value) == 2:
            return cls._format_code(value, show_flag, show_name, show_code)

        return format_html('<span>{}</span>', escape(str(value)))

    @classmethod
    def _format_model(
        cls,
        country: Any,
        show_flag: bool,
        show_name: bool,
        show_code: bool,
    ) -> SafeString:
        """Format from Country model instance."""
        parts = []

        if show_flag:
            emoji = getattr(country, "emoji", "")
            if emoji:
                parts.append(format_html('<span>{}</span>', emoji))

        if show_name:
            parts.append(format_html('<span class="font-medium">{}</span>', country.name))
        elif show_code:
            parts.append(format_html('<span class="font-medium">{}</span>', country.iso2))

        if show_code and show_name:
            parts.append(
                format_html('<span class="text-base-400">({})</span>', country.iso2)
            )

        return format_html(
            '<span class="flex items-center gap-2">{}</span>',
            format_html(" ".join(str(p) for p in parts)),
        )

    @classmethod
    def _format_code(
        cls,
        code: str,
        show_flag: bool,
        show_name: bool,
        show_code: bool,
    ) -> SafeString:
        """Format from ISO2 code by looking up country."""
        try:
            from django_cfg.apps.tools.geo.services.database import get_geo_db

            country = get_geo_db().get_country(code)
            if country:
                parts = []

                if show_flag and country.emoji:
                    parts.append(format_html('<span>{}</span>', country.emoji))

                if show_name:
                    parts.append(
                        format_html('<span class="font-medium">{}</span>', country.name)
                    )
                elif show_code:
                    parts.append(
                        format_html('<span class="font-medium">{}</span>', code)
                    )

                if show_code and show_name:
                    parts.append(
                        format_html('<span class="text-base-400">({})</span>', code)
                    )

                return format_html(
                    '<span class="flex items-center gap-2">{}</span>',
                    format_html(" ".join(str(p) for p in parts)),
                )
        except Exception:
            pass

        return format_html('<span class="font-medium">{}</span>', code)


class CityDisplay:
    """
    Display city with state and country in admin list views.

    Shows: Seoul, KR  or  🇰🇷 Seoul, 11, KR
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: Dict[str, Any]) -> SafeString:
        """
        Render city field with location hierarchy.

        Config options:
            show_flag: bool - Show country flag (default: True)
            show_state: bool - Show state code (default: True)
            show_country: bool - Show country code (default: True)
            show_coordinates: bool - Show lat/lon (default: False)
        """
        value = getattr(obj, field_name, None)

        if not value:
            return format_html(
                '<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>'
            )

        show_flag = config.get("show_flag", True)
        show_state = config.get("show_state", True)
        show_country = config.get("show_country", True)
        show_coordinates = config.get("show_coordinates", False)

        # Handle City model instance (FK)
        if hasattr(value, "name") and hasattr(value, "country"):
            return cls._format_model(
                value, show_flag, show_state, show_country, show_coordinates
            )

        # Handle city ID (int)
        if isinstance(value, int):
            return cls._format_id(
                value, show_flag, show_state, show_country, show_coordinates
            )

        return format_html('<span>{}</span>', escape(str(value)))

    @classmethod
    def _format_model(
        cls,
        city: Any,
        show_flag: bool,
        show_state: bool,
        show_country: bool,
        show_coordinates: bool,
    ) -> SafeString:
        """Format from City model instance."""
        parts = []

        # Flag
        if show_flag and hasattr(city, "country") and city.country:
            emoji = getattr(city.country, "emoji", "")
            if emoji:
                parts.append(format_html('<span>{}</span>', emoji))

        # City name
        parts.append(format_html('<span class="font-medium">{}</span>', city.name))

        # State
        if show_state and hasattr(city, "state") and city.state:
            state_code = getattr(city.state, "state_code", None) or city.state.name
            parts.append(
                format_html('<span class="text-base-400">{}</span>', state_code)
            )

        # Country
        if show_country and hasattr(city, "country") and city.country:
            parts.append(
                format_html('<span class="text-base-400">{}</span>', city.country.iso2)
            )

        # Coordinates
        if show_coordinates:
            lat = getattr(city, "latitude", None)
            lon = getattr(city, "longitude", None)
            if lat is not None and lon is not None:
                parts.append(
                    format_html(
                        '<span class="text-xs text-base-400">({:.4f}, {:.4f})</span>',
                        lat,
                        lon,
                    )
                )

        # Join parts - flag gets space, rest get comma
        if parts and show_flag and hasattr(city, "country") and city.country and city.country.emoji:
            flag_part = str(parts[0])
            rest_parts = ", ".join(str(p) for p in parts[1:])
            content = f"{flag_part} {rest_parts}"
        else:
            content = ", ".join(str(p) for p in parts)

        return format_html('<span class="flex items-center gap-1">{}</span>', content)

    @classmethod
    def _format_id(
        cls,
        city_id: int,
        show_flag: bool,
        show_state: bool,
        show_country: bool,
        show_coordinates: bool,
    ) -> SafeString:
        """Format from city ID by looking up city."""
        try:
            from django_cfg.apps.tools.geo.services.database import get_geo_db

            db = get_geo_db()
            city = db.get_city(city_id)

            if city:
                parts = []
                country = db.get_country(city.country_iso2) if city.country_iso2 else None
                state = db.get_state(city.state_id) if city.state_id else None

                # Flag
                if show_flag and country and country.emoji:
                    parts.append(format_html('<span>{}</span>', country.emoji))

                # City name
                parts.append(
                    format_html('<span class="font-medium">{}</span>', city.name)
                )

                # State
                if show_state and state:
                    state_code = state.iso2 or state.name
                    parts.append(
                        format_html('<span class="text-base-400">{}</span>', state_code)
                    )

                # Country
                if show_country and country:
                    parts.append(
                        format_html('<span class="text-base-400">{}</span>', country.iso2)
                    )

                # Coordinates
                if show_coordinates and city.coordinates:
                    lat, lon = city.coordinates
                    parts.append(
                        format_html(
                            '<span class="text-xs text-base-400">({:.4f}, {:.4f})</span>',
                            lat,
                            lon,
                        )
                    )

                # Join
                if parts and show_flag and country and country.emoji:
                    flag_part = str(parts[0])
                    rest_parts = ", ".join(str(p) for p in parts[1:])
                    content = f"{flag_part} {rest_parts}"
                else:
                    content = ", ".join(str(p) for p in parts)

                return format_html(
                    '<span class="flex items-center gap-1">{}</span>', content
                )
        except Exception:
            pass

        return format_html('<span>{}</span>', city_id)


class LocationDisplay:
    """
    Display full location with city, state, country in admin list views.

    Alias for CityDisplay with full options enabled.
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: Dict[str, Any]) -> SafeString:
        """
        Render location field with full hierarchy.

        Config options: Same as CityDisplay
        """
        # Default to showing all components
        config.setdefault("show_flag", True)
        config.setdefault("show_state", True)
        config.setdefault("show_country", True)
        return CityDisplay.from_field(obj, field_name, config)


class CoordinatesDisplay:
    """
    Display coordinates in admin list views.

    Shows: 37.5665, 126.9780
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: Dict[str, Any]) -> SafeString:
        """
        Render coordinates field.

        Config options:
            lat_field: str - Latitude field name (default: "latitude")
            lon_field: str - Longitude field name (default: "longitude")
            precision: int - Decimal places (default: 4)
            show_link: bool - Link to Google Maps (default: False)
        """
        lat_field = config.get("lat_field", "latitude")
        lon_field = config.get("lon_field", "longitude")
        precision = config.get("precision", 4)
        show_link = config.get("show_link", False)

        lat = getattr(obj, lat_field, None)
        lon = getattr(obj, lon_field, None)

        if lat is None or lon is None:
            return format_html(
                '<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>'
            )

        formatted = f"{lat:.{precision}f}, {lon:.{precision}f}"

        if show_link:
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            return format_html(
                '<a href="{}" target="_blank" class="text-primary-600 hover:underline font-mono text-sm">{}</a>',
                maps_url,
                formatted,
            )

        return format_html('<span class="font-mono text-sm">{}</span>', formatted)


__all__ = [
    "CountryDisplay",
    "CityDisplay",
    "LocationDisplay",
    "CoordinatesDisplay",
]
