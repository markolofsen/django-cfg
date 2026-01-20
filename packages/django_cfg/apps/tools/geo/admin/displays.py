"""
Display classes for geo data in admin list views.

Provides formatted display of location data with flags and coordinates.
Similar to MoneyFieldDisplay in currency app.
"""

from typing import Any, Optional

from django.utils.html import format_html
from django.utils.safestring import mark_safe


class GeoLocationDisplay:
    """
    Display city location with flag emoji in admin list views.

    Shows: 🇰🇷 Seoul, 11, KR

    Usage in PydanticAdmin:
        from django_cfg.apps.tools.geo.admin import GeoLocationDisplay

        class PropertyAdmin(PydanticAdmin):
            config = AdminConfig(
                model=Property,
                display_fields=[
                    GeoLocationDisplay(name="city"),
                ],
            )

    Usage as admin method:
        @admin.display(description="Location")
        def location_display(self, obj):
            return GeoLocationDisplay(name="city").format_value(obj)
    """

    def __init__(
        self,
        name: str,
        title: str = "Location",
        show_flag: bool = True,
        show_state: bool = True,
        show_coordinates: bool = False,
    ):
        """
        Initialize location display.

        Args:
            name: Field name on the model (city FK or city_id)
            title: Column header title
            show_flag: Include country flag emoji
            show_state: Include state/province code
            show_coordinates: Include lat/lon coordinates
        """
        self.name = name
        self.title = title
        self.show_flag = show_flag
        self.show_state = show_state
        self.show_coordinates = show_coordinates

    def format_value(self, obj: Any) -> str:
        """Format the location for display."""
        city = getattr(obj, self.name, None)
        if not city:
            return mark_safe('<span class="text-base-400">—</span>')

        # Handle both FK (City object) and city_id (int)
        if isinstance(city, int):
            from ..services.database import get_geo_db

            db = get_geo_db()
            city_dto = db.get_city(city)
            if not city_dto:
                return str(city)

            country = db.get_country(city_dto.country_iso2) if city_dto.country_iso2 else None
            state = db.get_state(city_dto.state_id) if city_dto.state_id else None

            return self._format_dto(city_dto, state, country)
        else:
            # City is a model instance (FK)
            return self._format_model(city)

    def _format_model(self, city: Any) -> str:
        """Format from City model instance."""
        parts = []

        # Flag
        if self.show_flag and hasattr(city, "country") and city.country:
            flag = getattr(city.country, "emoji", "")
            if flag:
                parts.append(f'<span>{flag}</span>')

        # City name
        parts.append(f'<span class="font-medium">{city.name}</span>')

        # State
        if self.show_state and hasattr(city, "state") and city.state:
            state_code = getattr(city.state, "state_code", None) or city.state.name
            parts.append(f'<span class="text-base-400">{state_code}</span>')

        # Country
        if hasattr(city, "country") and city.country:
            parts.append(f'<span class="text-base-400">{city.country.iso2}</span>')

        # Coordinates
        if self.show_coordinates:
            lat = getattr(city, "latitude", None)
            lon = getattr(city, "longitude", None)
            if lat is not None and lon is not None:
                parts.append(
                    f'<span class="text-xs text-base-400">({lat:.4f}, {lon:.4f})</span>'
                )

        result = self._join_parts(parts)
        return mark_safe(f'<span class="flex items-center gap-1">{result}</span>')

    def _format_dto(
        self,
        city: Any,
        state: Optional[Any],
        country: Optional[Any],
    ) -> str:
        """Format from DTOs."""
        parts = []

        # Flag
        if self.show_flag and country and country.emoji:
            parts.append(f'<span>{country.emoji}</span>')

        # City name
        parts.append(f'<span class="font-medium">{city.name}</span>')

        # State
        if self.show_state and state:
            state_code = state.iso2 or state.name
            parts.append(f'<span class="text-base-400">{state_code}</span>')

        # Country
        if country:
            parts.append(f'<span class="text-base-400">{country.iso2}</span>')

        # Coordinates
        if self.show_coordinates and city.coordinates:
            lat, lon = city.coordinates
            parts.append(
                f'<span class="text-xs text-base-400">({lat:.4f}, {lon:.4f})</span>'
            )

        result = self._join_parts(parts)
        return mark_safe(f'<span class="flex items-center gap-1">{result}</span>')

    def _join_parts(self, parts: list) -> str:
        """Join parts with proper separators."""
        if not parts:
            return ""

        # First part (flag) gets space separator, rest get comma
        if len(parts) == 1:
            return parts[0]

        # Check if first is flag (no class)
        if 'class="font' not in parts[0] and 'text-base-400' not in parts[0]:
            # First is flag
            return f"{parts[0]} {', '.join(parts[1:])}"

        return ", ".join(parts)

    def __call__(self, obj: Any) -> str:
        """Allow using as callable."""
        return self.format_value(obj)


class CountryDisplay:
    """
    Display country with flag emoji in admin list views.

    Shows: 🇰🇷 South Korea

    Usage in PydanticAdmin:
        from django_cfg.apps.tools.geo.admin import CountryDisplay

        class PropertyAdmin(PydanticAdmin):
            config = AdminConfig(
                model=Property,
                display_fields=[
                    CountryDisplay(name="country"),
                ],
            )

    Usage as admin method:
        @admin.display(description="Country")
        def country_display(self, obj):
            return CountryDisplay(name="country").format_value(obj)
    """

    def __init__(
        self,
        name: str,
        title: str = "Country",
        show_flag: bool = True,
        show_name: bool = True,
    ):
        """
        Initialize country display.

        Args:
            name: Field name on the model (iso2 code or Country FK)
            title: Column header title
            show_flag: Include flag emoji
            show_name: Include country name (False = just flag + code)
        """
        self.name = name
        self.title = title
        self.show_flag = show_flag
        self.show_name = show_name

    def format_value(self, obj: Any) -> str:
        """Format the country for display."""
        value = getattr(obj, self.name, None)
        if not value:
            return mark_safe('<span class="text-base-400">—</span>')

        # Handle Country model instance
        if hasattr(value, "iso2"):
            return self._format_model(value)

        # Handle ISO2 code string
        if isinstance(value, str) and len(value) == 2:
            return self._format_code(value)

        return str(value)

    def _format_model(self, country: Any) -> str:
        """Format from Country model instance."""
        parts = []

        if self.show_flag:
            emoji = getattr(country, "emoji", "")
            if emoji:
                parts.append(emoji)

        if self.show_name:
            parts.append(country.name)
        else:
            parts.append(country.iso2)

        return mark_safe(
            f'<span class="flex items-center gap-2">'
            f'{" ".join(parts)}'
            f'</span>'
        )

    def _format_code(self, code: str) -> str:
        """Format from ISO2 code."""
        from ..services.database import get_geo_db

        db = get_geo_db()
        country = db.get_country(code)

        if not country:
            return code

        parts = []

        if self.show_flag and country.emoji:
            parts.append(country.emoji)

        if self.show_name:
            parts.append(country.name)
        else:
            parts.append(country.iso2)

        return mark_safe(
            f'<span class="flex items-center gap-2">'
            f'{" ".join(parts)}'
            f'</span>'
        )

    def __call__(self, obj: Any) -> str:
        """Allow using as callable."""
        return self.format_value(obj)


class CoordinatesDisplay:
    """
    Display coordinates in admin list views.

    Shows: 37.5665, 126.9780

    Usage:
        @admin.display(description="Coordinates")
        def coords_display(self, obj):
            return CoordinatesDisplay(lat_field="latitude", lon_field="longitude").format_value(obj)
    """

    def __init__(
        self,
        lat_field: str = "latitude",
        lon_field: str = "longitude",
        title: str = "Coordinates",
        precision: int = 4,
        show_link: bool = False,
    ):
        """
        Initialize coordinates display.

        Args:
            lat_field: Latitude field name
            lon_field: Longitude field name
            title: Column header title
            precision: Decimal places
            show_link: Include Google Maps link
        """
        self.lat_field = lat_field
        self.lon_field = lon_field
        self.title = title
        self.precision = precision
        self.show_link = show_link

    def format_value(self, obj: Any) -> str:
        """Format coordinates for display."""
        lat = getattr(obj, self.lat_field, None)
        lon = getattr(obj, self.lon_field, None)

        if lat is None or lon is None:
            return mark_safe('<span class="text-base-400">—</span>')

        formatted = f"{lat:.{self.precision}f}, {lon:.{self.precision}f}"

        if self.show_link:
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            return format_html(
                '<a href="{}" target="_blank" class="text-primary-600 hover:underline">{}</a>',
                maps_url,
                formatted,
            )

        return mark_safe(f'<span class="font-mono text-sm">{formatted}</span>')

    def __call__(self, obj: Any) -> str:
        """Allow using as callable."""
        return self.format_value(obj)


__all__ = [
    "GeoLocationDisplay",
    "CountryDisplay",
    "CoordinatesDisplay",
]
