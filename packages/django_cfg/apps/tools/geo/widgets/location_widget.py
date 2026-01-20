"""
LocationField widget with MapLibre GL map.

All-in-one location widget that manages:
- City selection (geo field)
- Address field
- Latitude/Longitude fields

Single widget renders everything - no need to add address/lat/lng to admin fieldsets.
"""

import json
from typing import Any, Optional

from django import forms
from django.urls import reverse


class LocationFieldWidget(forms.Widget):
    """
    All-in-one location widget with map, city search, address and coordinates.

    Renders hidden inputs for address, latitude, longitude fields and syncs
    them automatically. Only geo field needs to be in admin fieldset.

    Usage in admin:
        fieldsets = [
            ("Location", {"fields": ["geo"]}),  # Widget handles address, lat, lng
        ]
    """

    template_name = "geo/widgets/location_field.html"

    class Media:
        css = {
            "all": [
                "https://cdn.jsdelivr.net/npm/maplibre-gl@5.6.0/dist/maplibre-gl.min.css",
            ]
        }
        js = [
            "https://cdn.jsdelivr.net/npm/maplibre-gl@5.6.0/dist/maplibre-gl.min.js",
        ]

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        show_map: bool = True,
        map_height: str = "160px",
        default_zoom: int = 12,
        # Related field names (will render hidden inputs + sync)
        address_field: str = "address",
        latitude_field: str = "latitude",
        longitude_field: str = "longitude",
    ) -> None:
        self.show_map = show_map
        self.map_height = map_height
        self.default_zoom = default_zoom
        self.address_field = address_field
        self.latitude_field = latitude_field
        self.longitude_field = longitude_field
        super().__init__(attrs)

    def get_context(
        self,
        name: str,
        value: Any,
        attrs: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)

        # Get city data if value exists
        city_data = None
        if value:
            city_data = self._get_city_data(value)

        # Build URLs
        try:
            search_url = reverse("cfg_geo:search-cities")
            nearby_url = reverse("cfg_geo:search-nearby")
            reverse_geocode_url = reverse("cfg_geo:city-reverse-geocode")
            autocomplete_url = reverse("cfg_geo:search-autocomplete")
        except Exception:
            search_url = "/cfg/geo/search/cities/"
            nearby_url = "/cfg/geo/search/nearby/"
            reverse_geocode_url = "/cfg/geo/cities/reverse_geocode/"
            autocomplete_url = "/cfg/geo/search/autocomplete/"

        # Get initial values for related fields (passed via attrs or form)
        initial_address = attrs.pop("initial_address", "") if attrs else ""
        initial_lat = attrs.pop("initial_latitude", "") if attrs else ""
        initial_lng = attrs.pop("initial_longitude", "") if attrs else ""

        context["widget"].update({
            "show_map": self.show_map,
            "map_height": self.map_height,
            "default_zoom": self.default_zoom,
            "city_data": city_data,
            "city_data_json": json.dumps(city_data) if city_data else "null",
            "search_url": search_url,
            "nearby_url": nearby_url,
            "reverse_geocode_url": reverse_geocode_url,
            "autocomplete_url": autocomplete_url,
            # Related field names for rendering
            "address_field": self.address_field,
            "latitude_field": self.latitude_field,
            "longitude_field": self.longitude_field,
            # Initial values
            "initial_address": initial_address,
            "initial_latitude": str(initial_lat) if initial_lat else "",
            "initial_longitude": str(initial_lng) if initial_lng else "",
        })
        return context

    def _get_city_data(self, city_id: Any) -> Optional[dict]:
        """Get city data for initial display."""
        try:
            from ..services.database import get_geo_db

            db = get_geo_db()
            city = db.get_city(int(city_id))
            if city:
                country = db.get_country(city.country_iso2) if city.country_iso2 else None
                state = db.get_state(city.state_id) if city.state_id else None
                return {
                    "id": city.id,
                    "name": city.name,
                    "state_name": state.name if state else None,
                    "country_name": country.name if country else "",
                    "country_iso2": city.country_iso2 or "",
                    "flag": country.emoji if country else "",
                    "lat": city.latitude,
                    "lng": city.longitude,
                }
        except Exception:
            pass
        return None

    def value_from_datadict(self, data, files, name):
        """Get value from form data."""
        return data.get(name)


__all__ = ["LocationFieldWidget"]
