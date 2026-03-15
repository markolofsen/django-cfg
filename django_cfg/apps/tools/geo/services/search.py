"""
Geographic search service.

Provides proximity search and distance calculation utilities.
"""

from typing import List, Optional

from .database import GeoDatabase, get_geo_db
from .schemas import CityDTO, NearbyResult


class GeoSearchService:
    """
    Geographic search service.

    Features:
    - Proximity search with geodesic distance
    - Bounding box optimization
    - Nearest city lookup

    Usage:
        service = get_search_service()
        nearby = service.find_nearby_cities(37.5665, 126.978, radius_km=50)
        nearest = service.find_nearest_city(37.5665, 126.978)
        distance = service.calculate_distance(37.5, 126.9, 35.6, 139.6)
    """

    def __init__(self, db: Optional[GeoDatabase] = None):
        self._db = db or get_geo_db()

    def find_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50,
        limit: int = 10,
        country_code: Optional[str] = None,
    ) -> List[NearbyResult]:
        """
        Find cities within radius of a point.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            limit: Maximum results
            country_code: Filter by country (optional)

        Returns:
            List of NearbyResult sorted by distance
        """
        results = list(self._db.get_nearby_cities(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
        ))

        # Filter by country if specified
        if country_code:
            results = [r for r in results if r.city.country_iso2 == country_code.upper()]

        return results

    def find_nearest_city(
        self,
        latitude: float,
        longitude: float,
        max_radius_km: float = 500,
    ) -> Optional[CityDTO]:
        """
        Find the single nearest city to coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude
            max_radius_km: Maximum search radius (for sparse areas)

        Returns:
            CityDTO or None if no city found
        """
        results = self.find_nearby_cities(
            latitude=latitude,
            longitude=longitude,
            radius_km=max_radius_km,
            limit=1,
        )
        return results[0].city if results else None

    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate distance between two points in km.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        return self._db.calculate_distance((lat1, lon1), (lat2, lon2))


# Singleton instance
_search_service: Optional[GeoSearchService] = None


def get_search_service() -> GeoSearchService:
    """Get shared search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = GeoSearchService()
    return _search_service


def find_nearby(
    latitude: float,
    longitude: float,
    radius_km: float = 50,
    limit: int = 10,
) -> List[NearbyResult]:
    """
    Find nearby cities (convenience function).

    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_km: Search radius in kilometers
        limit: Maximum results

    Returns:
        List of NearbyResult sorted by distance
    """
    return get_search_service().find_nearby_cities(
        latitude, longitude, radius_km, limit
    )


def distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate distance in km (convenience function).

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    return get_search_service().calculate_distance(lat1, lon1, lat2, lon2)


__all__ = [
    "GeoSearchService",
    "get_search_service",
    "find_nearby",
    "distance",
]
