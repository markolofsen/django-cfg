"""
Geographic data app for django-cfg.

Provides models, fields, widgets, and services for handling countries, states, and cities.

Quick Start:
    # In your model
    from django_cfg.apps.tools.geo import CountryField, CityField

    class Location(models.Model):
        country = CountryField()
        city = CityField()

    # Access data
    location = Location.objects.first()
    print(location.country)          # "KR"
    print(location.country_display)  # "South Korea"
    print(location.country_emoji)    # "🇰🇷"

    print(location.city)              # 1835848
    print(location.city_display)      # "Seoul, KR"
    print(location.city_coordinates)  # (37.566, 126.9784)

Features:
    - 250+ countries with ISO codes, currencies, flags
    - 5000+ states/provinces
    - 150,000+ cities with coordinates
    - Proximity search (find nearby cities)
    - Select2-compatible AJAX widgets
    - Unfold admin integration

Management Commands:
    python manage.py geo_populate  # Load initial data

Configuration (in settings.py):
    DJANGO_CFG = {
        "geo": {
            "enabled": True,
            "auto_populate": True,  # Auto-load data on startup
        }
    }
"""

from .apps import GeoAppConfig
from .fields import CityField, CountryField, LocationField

# Lazy imports for models (to avoid AppRegistryNotReady)
# Models should be imported after Django apps are loaded
# Use: from django_cfg.apps.tools.geo.models import Country, State, City

from .services import (
    CityDTO,
    CountryDTO,
    GeoDatabase,
    GeoSearchService,
    LocationDTO,
    NearbyResult,
    StateDTO,
    coordinates_to_string,
    distance,
    find_nearby,
    format_location,
    get_geo_db,
    get_search_service,
    parse_coordinates,
    resolve_location,
    validate_coordinates,
)
from .widgets import CitySelectWidget, CountrySelectWidget, GeoAutocompleteWidget, LocationFieldWidget

default_app_config = "django_cfg.apps.tools.geo.apps.GeoAppConfig"


def __getattr__(name: str):
    """Lazy import for models to avoid AppRegistryNotReady."""
    if name in ("Country", "State", "City"):
        from . import models
        return getattr(models, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # App config
    "GeoAppConfig",
    # Models
    "Country",
    "State",
    "City",
    # Fields
    "CountryField",
    "CityField",
    "LocationField",
    # Widgets
    "GeoAutocompleteWidget",
    "CountrySelectWidget",
    "CitySelectWidget",
    # DTOs
    "CountryDTO",
    "StateDTO",
    "CityDTO",
    "LocationDTO",
    "NearbyResult",
    # Database service
    "GeoDatabase",
    "get_geo_db",
    # Search service
    "GeoSearchService",
    "get_search_service",
    "find_nearby",
    "distance",
    # Utils
    "format_location",
    "resolve_location",
    "parse_coordinates",
    "validate_coordinates",
    "coordinates_to_string",
]
