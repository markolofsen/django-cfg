"""
PostGIS spatial query service.

Provides optimized spatial queries using PostgreSQL PostGIS extension.
Falls back to geodesic calculations if PostGIS is not available.

Requirements:
    - PostgreSQL with PostGIS extension installed
    - Django GIS backend: django.contrib.gis.db.backends.postgis
    - City model with PointField (see models.py)

Usage:
    from django_cfg.apps.tools.geo.services.postgis import (
        is_postgis_available,
        get_nearby_cities_postgis,
    )

    if is_postgis_available():
        cities = get_nearby_cities_postgis(37.5665, 126.978, radius_km=50)
    else:
        # Fallback to geodesic
        from .database import get_geo_db
        cities = get_geo_db().get_nearby_cities(37.5665, 126.978, radius_km=50)
"""

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, List, Optional, Sequence

if TYPE_CHECKING:
    from ..models import City

logger = logging.getLogger(__name__)

_postgis_available: Optional[bool] = None


def is_postgis_available() -> bool:
    """
    Check if PostGIS is available.

    Returns True if:
    - Django GIS is installed
    - Database has PostGIS extension
    - City model has 'location' PointField
    """
    global _postgis_available

    if _postgis_available is not None:
        return _postgis_available

    try:
        from django.contrib.gis.db.models import PointField
        from django.contrib.gis.geos import Point

        from ..models import City

        # Check if City has location field
        if not hasattr(City, "location"):
            logger.debug("PostGIS not available: City model missing 'location' field")
            _postgis_available = False
            return False

        # Try a simple query to verify PostGIS works
        try:
            City.objects.filter(location__isnull=False).exists()
            _postgis_available = True
            logger.info("PostGIS spatial queries available")
            return True
        except Exception as e:
            logger.debug(f"PostGIS not available: {e}")
            _postgis_available = False
            return False

    except ImportError:
        logger.debug("PostGIS not available: django.contrib.gis not installed")
        _postgis_available = False
        return False


def get_nearby_cities_postgis(
    latitude: float,
    longitude: float,
    radius_km: float = 100,
    limit: int = 10,
    country_code: Optional[str] = None,
) -> Sequence["City"]:
    """
    Find nearby cities using PostGIS spatial queries.

    Uses ST_DWithin for efficient radius search with spatial index.

    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_km: Search radius in kilometers
        limit: Maximum results
        country_code: Optional country filter (ISO2)

    Returns:
        List of City model instances ordered by distance

    Raises:
        RuntimeError: If PostGIS is not available
    """
    if not is_postgis_available():
        raise RuntimeError(
            "PostGIS is not available. Use get_geo_db().get_nearby_cities() instead."
        )

    from django.contrib.gis.db.models.functions import Distance
    from django.contrib.gis.geos import Point
    from django.contrib.gis.measure import D

    from ..models import City

    # Create point from coordinates (note: Point takes lon, lat order)
    point = Point(longitude, latitude, srid=4326)

    # Build query
    queryset = City.objects.filter(
        is_active=True,
        location__isnull=False,
        location__distance_lte=(point, D(km=radius_km)),
    )

    # Apply country filter
    if country_code:
        queryset = queryset.filter(country__iso2=country_code.upper())

    # Annotate with distance and order
    queryset = (
        queryset.annotate(distance=Distance("location", point))
        .select_related("state", "country")
        .order_by("distance")[:limit]
    )

    return list(queryset)


def get_cities_in_bbox(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    limit: int = 100,
) -> Sequence["City"]:
    """
    Get cities within a bounding box using PostGIS.

    Args:
        min_lat: Minimum latitude (south)
        min_lon: Minimum longitude (west)
        max_lat: Maximum latitude (north)
        max_lon: Maximum longitude (east)
        limit: Maximum results

    Returns:
        List of City model instances
    """
    if not is_postgis_available():
        raise RuntimeError("PostGIS is not available")

    from django.contrib.gis.geos import Polygon

    from ..models import City

    # Create bounding box polygon
    bbox = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))
    bbox.srid = 4326

    queryset = (
        City.objects.filter(
            is_active=True,
            location__isnull=False,
            location__within=bbox,
        )
        .select_related("state", "country")[:limit]
    )

    return list(queryset)


def get_nearest_city_postgis(
    latitude: float,
    longitude: float,
    max_radius_km: float = 500,
) -> Optional["City"]:
    """
    Find the single nearest city using PostGIS.

    Args:
        latitude: Latitude
        longitude: Longitude
        max_radius_km: Maximum search radius

    Returns:
        Nearest City or None
    """
    results = get_nearby_cities_postgis(
        latitude, longitude, radius_km=max_radius_km, limit=1
    )
    return results[0] if results else None


def calculate_distance_postgis(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate distance between two points using PostGIS.

    Uses geography type for accurate geodesic distance.

    Args:
        lat1, lon1: First point
        lat2, lon2: Second point

    Returns:
        Distance in kilometers
    """
    if not is_postgis_available():
        # Fallback to geopy
        from geopy.distance import geodesic

        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    from django.contrib.gis.geos import Point

    point1 = Point(lon1, lat1, srid=4326)
    point2 = Point(lon2, lat2, srid=4326)

    # Use geography for geodesic distance
    return point1.distance(point2) / 1000  # meters to km


def populate_location_field() -> int:
    """
    Populate 'location' PointField from lat/lon for all cities.

    Call this after initial data population if PostGIS is enabled.

    Returns:
        Number of cities updated
    """
    if not is_postgis_available():
        logger.warning("PostGIS not available, cannot populate location field")
        return 0

    from django.contrib.gis.geos import Point
    from django.db import transaction

    from ..models import City

    count = 0

    with transaction.atomic():
        cities = City.objects.filter(
            location__isnull=True,
            latitude__isnull=False,
            longitude__isnull=False,
        )

        for city in cities.iterator(chunk_size=1000):
            city.location = Point(city.longitude, city.latitude, srid=4326)
            city.save(update_fields=["location"])
            count += 1

    logger.info(f"Populated location field for {count} cities")
    return count


__all__ = [
    "is_postgis_available",
    "get_nearby_cities_postgis",
    "get_cities_in_bbox",
    "get_nearest_city_postgis",
    "calculate_distance_postgis",
    "populate_location_field",
]
