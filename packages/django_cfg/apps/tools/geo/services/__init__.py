"""
Geo services module.

Provides database access, DTOs, search, and utility functions for geographic data.
"""

from .database import GeoDatabase, get_geo_db
from .schemas import (
    CityDTO,
    CountryDTO,
    LocationDTO,
    NearbyResult,
    StateDTO,
    # Geocoding DTOs
    AddressComponents,
    GeocodingResult,
    ReverseGeocodingResult,
    AutocompleteResult,
)
from .geocoding import GeocodingService, get_geocoding_service
from .search import (
    GeoSearchService,
    distance,
    find_nearby,
    get_search_service,
)
from .utils import (
    coordinates_to_string,
    format_location,
    parse_coordinates,
    resolve_city_from_coordinates,
    resolve_location,
    validate_coordinates,
)
from .postgis import (
    calculate_distance_postgis,
    get_cities_in_bbox,
    get_nearby_cities_postgis,
    get_nearest_city_postgis,
    is_postgis_available,
    populate_location_field,
)

__all__ = [
    # Database
    "GeoDatabase",
    "get_geo_db",
    # DTOs
    "CountryDTO",
    "StateDTO",
    "CityDTO",
    "LocationDTO",
    "NearbyResult",
    # Geocoding DTOs
    "AddressComponents",
    "GeocodingResult",
    "ReverseGeocodingResult",
    "AutocompleteResult",
    # Geocoding Service
    "GeocodingService",
    "get_geocoding_service",
    # Search
    "GeoSearchService",
    "get_search_service",
    "find_nearby",
    "distance",
    # Utils
    "format_location",
    "resolve_location",
    "resolve_city_from_coordinates",
    "parse_coordinates",
    "validate_coordinates",
    "coordinates_to_string",
    # PostGIS
    "is_postgis_available",
    "get_nearby_cities_postgis",
    "get_cities_in_bbox",
    "get_nearest_city_postgis",
    "calculate_distance_postgis",
    "populate_location_field",
]
