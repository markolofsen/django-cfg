"""
Geocoding service.

Provides address-to-coordinates (geocode) and coordinates-to-address (reverse geocode)
functionality using Nominatim (OpenStreetMap) with caching and rate limiting.
"""

import hashlib
import logging
import time
from threading import Lock
from typing import List, Optional

import httpx
from django.core.cache import cache

from .schemas import (
    AddressComponents,
    AutocompleteResult,
    GeocodingResult,
    ReverseGeocodingResult,
)

logger = logging.getLogger(__name__)

# Nominatim API
NOMINATIM_URL = "https://nominatim.openstreetmap.org"

# Photon API (Komoot) - faster, typo-tolerant, no strict rate limit
PHOTON_URL = "https://photon.komoot.io/api/"

USER_AGENT = "django-cfg/1.0 (https://djangocfg.com)"

# Cache settings
CACHE_PREFIX = "geo:geocoding:"
CACHE_TTL_GEOCODE = 86400 * 30  # 30 days
CACHE_TTL_REVERSE = 86400 * 7   # 7 days
CACHE_TTL_AUTOCOMPLETE = 3600   # 1 hour


class RateLimiter:
    """
    Thread-safe rate limiter for API requests.

    Nominatim requires max 1 request/second.
    """

    def __init__(self, requests_per_second: float = 1.0):
        self._min_interval = 1.0 / requests_per_second
        self._last_request = 0.0
        self._lock = Lock()

    def wait(self) -> None:
        """Wait until we can make the next request."""
        with self._lock:
            elapsed = time.time() - self._last_request
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_request = time.time()


# Global rate limiter for Nominatim
_nominatim_limiter = RateLimiter(requests_per_second=1.0)


class GeocodingService:
    """
    Geocoding service with caching and rate limiting.

    Features:
    - Address to coordinates (geocode)
    - Coordinates to address (reverse_geocode)
    - Django cache integration
    - Rate limiting (1 req/sec for Nominatim)
    - Fallback to local database when possible

    Usage:
        service = get_geocoding_service()
        result = service.geocode("Seoul, South Korea")
        reverse = service.reverse_geocode(37.5665, 126.978)
    """

    _instance: Optional["GeocodingService"] = None

    @classmethod
    def get_instance(cls) -> "GeocodingService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._client = httpx.Client(
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
        )

    def geocode(
        self,
        address: str,
        country_code: Optional[str] = None,
    ) -> Optional[GeocodingResult]:
        """
        Convert address to coordinates.

        Args:
            address: Address string (e.g., "Seoul, South Korea")
            country_code: Optional ISO2 country code to limit search

        Returns:
            GeocodingResult or None if not found
        """
        if not address or len(address.strip()) < 2:
            return None

        address = address.strip()
        cache_key = self._cache_key("geocode", address, country_code)

        # Check cache
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Geocode cache hit: {address}")
            return GeocodingResult(**cached, source="cache")

        # Try local database first
        local_result = self._geocode_local(address, country_code)
        if local_result:
            self._cache_result(cache_key, local_result, CACHE_TTL_GEOCODE)
            return local_result

        # Query Nominatim
        result = self._geocode_nominatim(address, country_code)
        if result:
            self._cache_result(cache_key, result, CACHE_TTL_GEOCODE)

        return result

    def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[ReverseGeocodingResult]:
        """
        Convert coordinates to address.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            ReverseGeocodingResult or None if not found
        """
        # Round coordinates for caching (6 decimal places ≈ 0.1m precision)
        lat_rounded = round(latitude, 6)
        lng_rounded = round(longitude, 6)
        cache_key = self._cache_key("reverse", f"{lat_rounded},{lng_rounded}")

        # Check cache
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Reverse geocode cache hit: {lat_rounded},{lng_rounded}")
            return ReverseGeocodingResult(**cached, source="cache")

        # Try to match local city first
        local_result = self._reverse_local(latitude, longitude)

        # Query Nominatim for full address
        nominatim_result = self._reverse_nominatim(latitude, longitude)

        # Merge results
        if nominatim_result:
            result = ReverseGeocodingResult(
                display_name=nominatim_result.display_name,
                address=nominatim_result.address,
                city_id=local_result.city_id if local_result else None,
                city_name=local_result.city_name if local_result else None,
                distance_to_city_center=local_result.distance_to_city_center if local_result else None,
                source="nominatim",
            )
            self._cache_result(cache_key, result, CACHE_TTL_REVERSE)
            return result
        elif local_result:
            self._cache_result(cache_key, local_result, CACHE_TTL_REVERSE)
            return local_result

        return None

    def autocomplete(
        self,
        query: str,
        limit: int = 5,
        lang: str = "en",
    ) -> List[AutocompleteResult]:
        """
        Autocomplete search using Photon API.

        Photon is faster and more typo-tolerant than Nominatim.
        Returns places, cities, streets, POIs.

        Args:
            query: Search query (e.g., "seoul", "bali ind")
            limit: Max results (default 5)
            lang: Language code (default "en")

        Returns:
            List of AutocompleteResult
        """
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip()
        cache_key = self._cache_key("autocomplete", query, limit, lang)

        # Check cache
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Autocomplete cache hit: {query}")
            return [AutocompleteResult(**r) for r in cached]

        # Try local database first for city matches
        local_results = self._autocomplete_local(query, limit)

        # Query Photon for additional results
        photon_results = self._autocomplete_photon(query, limit, lang)

        # Merge and deduplicate (local first, then photon)
        results = local_results.copy()
        seen_coords = {(r.latitude, r.longitude) for r in results}

        for r in photon_results:
            coord = (r.latitude, r.longitude)
            if coord not in seen_coords:
                results.append(r)
                seen_coords.add(coord)
                if len(results) >= limit:
                    break

        # Cache results
        if results:
            cache.set(cache_key, [r.model_dump() for r in results], CACHE_TTL_AUTOCOMPLETE)

        return results[:limit]

    def _autocomplete_local(
        self,
        query: str,
        limit: int = 5,
    ) -> List[AutocompleteResult]:
        """Search local city database for autocomplete."""
        from .database import get_geo_db

        db = get_geo_db()
        cities = db.search_cities(query, limit=limit)

        results = []
        for city in cities:
            results.append(AutocompleteResult(
                text=city.display_name,
                place_id=f"local:{city.id}",
                latitude=city.latitude,
                longitude=city.longitude,
                type="city",
            ))

        return results

    def _autocomplete_photon(
        self,
        query: str,
        limit: int = 5,
        lang: str = "en",
    ) -> List[AutocompleteResult]:
        """Query Photon API for autocomplete suggestions."""
        params = {
            "q": query,
            "limit": limit,
            "lang": lang,
        }

        try:
            response = self._client.get(PHOTON_URL, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                coords = feature.get("geometry", {}).get("coordinates", [])

                if len(coords) < 2:
                    continue

                # Build display text
                parts = []
                if props.get("name"):
                    parts.append(props["name"])
                if props.get("city") and props.get("city") != props.get("name"):
                    parts.append(props["city"])
                if props.get("state"):
                    parts.append(props["state"])
                if props.get("country"):
                    parts.append(props["country"])

                text = ", ".join(parts) if parts else props.get("name", "Unknown")

                # Determine type
                osm_type = props.get("osm_value") or props.get("type") or "place"
                place_type = "city" if osm_type in ("city", "town", "village") else "address"

                results.append(AutocompleteResult(
                    text=text,
                    place_id=f"photon:{props.get('osm_id', '')}",
                    latitude=coords[1],  # GeoJSON is [lng, lat]
                    longitude=coords[0],
                    type=place_type,
                ))

            return results

        except httpx.HTTPError as e:
            logger.warning(f"Photon autocomplete error: {e}")
            return []

    def _geocode_local(
        self,
        address: str,
        country_code: Optional[str] = None,
    ) -> Optional[GeocodingResult]:
        """Try to geocode using local city database."""
        from .database import get_geo_db

        db = get_geo_db()
        cities = db.search_cities(address, country_code=country_code, limit=1)

        if cities:
            city = cities[0]
            return GeocodingResult(
                latitude=city.latitude,
                longitude=city.longitude,
                display_name=city.display_name,
                address=AddressComponents(
                    city=city.name,
                    state=city.state_iso2,
                    country_code=city.country_iso2,
                ),
                confidence=0.8,
                source="local",
            )

        return None

    def _reverse_local(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[ReverseGeocodingResult]:
        """Try to find nearest city in local database."""
        from .database import get_geo_db

        db = get_geo_db()
        nearby = db.get_nearby_cities(latitude, longitude, radius_km=50, limit=1)

        if nearby:
            result = nearby[0]
            return ReverseGeocodingResult(
                display_name=result.city.display_name,
                address=AddressComponents(
                    city=result.city.name,
                    state=result.city.state_iso2,
                    country_code=result.city.country_iso2,
                ),
                city_id=result.city.id,
                city_name=result.city.name,
                distance_to_city_center=result.distance_km,
                source="local",
            )

        return None

    def _geocode_nominatim(
        self,
        address: str,
        country_code: Optional[str] = None,
    ) -> Optional[GeocodingResult]:
        """Query Nominatim for geocoding."""
        _nominatim_limiter.wait()

        params = {
            "q": address,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 1,
        }
        if country_code:
            params["countrycodes"] = country_code.lower()

        try:
            response = self._client.get(f"{NOMINATIM_URL}/search", params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.debug(f"Nominatim: no results for '{address}'")
                return None

            result = data[0]
            addr = result.get("address", {})

            return GeocodingResult(
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
                display_name=result.get("display_name", address),
                address=AddressComponents(
                    house_number=addr.get("house_number"),
                    street=addr.get("road") or addr.get("street"),
                    city=addr.get("city") or addr.get("town") or addr.get("village"),
                    state=addr.get("state") or addr.get("province"),
                    country=addr.get("country"),
                    country_code=addr.get("country_code", "").upper() or None,
                    postal_code=addr.get("postcode"),
                ),
                confidence=1.0,
                source="nominatim",
            )

        except httpx.HTTPError as e:
            logger.warning(f"Nominatim geocode error: {e}")
            return None

    def _reverse_nominatim(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[ReverseGeocodingResult]:
        """Query Nominatim for reverse geocoding."""
        _nominatim_limiter.wait()

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
        }

        try:
            response = self._client.get(f"{NOMINATIM_URL}/reverse", params=params)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                logger.debug(f"Nominatim reverse: {data['error']}")
                return None

            addr = data.get("address", {})

            return ReverseGeocodingResult(
                display_name=data.get("display_name", ""),
                address=AddressComponents(
                    house_number=addr.get("house_number"),
                    street=addr.get("road") or addr.get("street"),
                    city=addr.get("city") or addr.get("town") or addr.get("village"),
                    state=addr.get("state") or addr.get("province"),
                    country=addr.get("country"),
                    country_code=addr.get("country_code", "").upper() or None,
                    postal_code=addr.get("postcode"),
                ),
                source="nominatim",
            )

        except httpx.HTTPError as e:
            logger.warning(f"Nominatim reverse error: {e}")
            return None

    def _cache_key(self, operation: str, *args) -> str:
        """Generate cache key."""
        key_data = f"{operation}:{':'.join(str(a) for a in args if a)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{CACHE_PREFIX}{operation}:{key_hash}"

    def _cache_result(self, key: str, result, ttl: int) -> None:
        """Cache a result, excluding source field."""
        data = result.model_dump(exclude={"source"})
        cache.set(key, data, ttl)


def get_geocoding_service() -> GeocodingService:
    """Get shared GeocodingService instance."""
    return GeocodingService.get_instance()


__all__ = ["GeocodingService", "get_geocoding_service"]
