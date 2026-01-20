"""
Location utility functions.

Provides formatting, resolution, and coordinate parsing utilities.
"""

import re
from typing import Optional, Tuple

from .database import get_geo_db
from .schemas import CityDTO, CountryDTO, LocationDTO


def format_location(
    city: Optional[CityDTO] = None,
    country: Optional[CountryDTO] = None,
    include_country_name: bool = True,
    include_flag: bool = False,
) -> str:
    """
    Format location for display.

    Args:
        city: CityDTO object
        country: CountryDTO object
        include_country_name: Use full country name instead of ISO2
        include_flag: Include country flag emoji

    Returns:
        Formatted location string

    Examples:
        "Seoul, KR"
        "Seoul, South Korea"
        "🇰🇷 Seoul, South Korea"
    """
    parts = []

    if include_flag and country and country.emoji:
        parts.append(country.emoji)

    if city:
        parts.append(city.name)

    if country:
        if include_country_name:
            parts.append(country.name)
        else:
            parts.append(country.iso2)

    if not parts:
        return "Unknown"

    # Format: "🇰🇷 Seoul, South Korea" or "Seoul, South Korea"
    if include_flag and parts and country and country.emoji:
        return f"{parts[0]} {', '.join(parts[1:])}"

    return ", ".join(parts)


def resolve_location(city_id: int) -> Optional[LocationDTO]:
    """
    Resolve full location from city ID.

    Args:
        city_id: City database ID

    Returns:
        LocationDTO with city, state, and country populated, or None
    """
    db = get_geo_db()

    city = db.get_city(city_id)
    if not city:
        return None

    state = db.get_state(city.state_id) if city.state_id else None
    country = db.get_country(city.country_iso2) if city.country_iso2 else None

    return LocationDTO(
        city=city,
        state=state,
        country=country,
        latitude=city.latitude,
        longitude=city.longitude,
    )


def parse_coordinates(value: str) -> Optional[Tuple[float, float]]:
    """
    Parse coordinates from string.

    Args:
        value: Coordinate string

    Returns:
        (latitude, longitude) tuple or None

    Accepts formats:
        "37.5665, 126.978"
        "37.5665,126.978"
        "(37.5665, 126.978)"
        "37.5665 126.978"
    """
    # Remove parentheses and brackets
    cleaned = re.sub(r"[()[\]]", "", value).strip()

    # Split by comma or whitespace
    parts = re.split(r"[,\s]+", cleaned)

    if len(parts) >= 2:
        try:
            lat = float(parts[0])
            lon = float(parts[1])
            if validate_coordinates(lat, lon):
                return (lat, lon)
        except ValueError:
            pass

    return None


def validate_coordinates(
    latitude: float,
    longitude: float
) -> bool:
    """
    Check if coordinates are valid.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if valid, False otherwise
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def coordinates_to_string(
    latitude: float,
    longitude: float,
    precision: int = 6
) -> str:
    """
    Format coordinates as string.

    Args:
        latitude: Latitude value
        longitude: Longitude value
        precision: Decimal places

    Returns:
        Formatted string like "37.566500, 126.978000"
    """
    return f"{latitude:.{precision}f}, {longitude:.{precision}f}"


def resolve_city_from_coordinates(
    latitude: float,
    longitude: float,
    radius_km: float = 50,
) -> Optional[int]:
    """
    Find nearest city ID by coordinates.

    Useful for auto-populating LocationField from coordinates
    during data ingestion/normalization.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        radius_km: Search radius in kilometers (default 50)

    Returns:
        City ID if found within radius, None otherwise

    Example:
        city_id = resolve_city_from_coordinates(-8.6908, 115.1688)
        # Returns city ID for Seminyak/Denpasar area in Bali

        property.geo = resolve_city_from_coordinates(lat, lng)
    """
    if not validate_coordinates(latitude, longitude):
        return None

    db = get_geo_db()
    nearby = db.get_nearby_cities(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=1,
    )

    if nearby:
        return nearby[0].city.id
    return None


__all__ = [
    "format_location",
    "resolve_location",
    "resolve_city_from_coordinates",
    "parse_coordinates",
    "validate_coordinates",
    "coordinates_to_string",
]
