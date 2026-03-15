"""
Geographic database service.

PostgreSQL-based geographic database with LRU caching and geodesic distance calculations.
"""

from functools import lru_cache
from typing import Optional, Sequence

from .schemas import CityDTO, CountryDTO, NearbyResult, StateDTO


class GeoDatabase:
    """
    PostgreSQL-based geographic database service.

    Features:
    - LRU caching for frequently accessed data
    - Geodesic distance calculations via geopy
    - Bounding box pre-filtering for proximity searches

    Usage:
        db = get_geo_db()
        country = db.get_country("KR")
        cities = db.search_cities("Seoul", country_code="KR")
        nearby = db.get_nearby_cities(37.5665, 126.978, radius_km=50)
    """

    _instance: Optional["GeoDatabase"] = None

    @classmethod
    def get_instance(cls) -> "GeoDatabase":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @lru_cache(maxsize=300)
    def get_country(self, code: str) -> Optional[CountryDTO]:
        """
        Get country by ISO2 code (cached).

        Args:
            code: ISO2 country code (e.g., 'KR', 'US')

        Returns:
            CountryDTO or None if not found
        """
        from ..models import Country

        try:
            country = Country.objects.get(iso2=code.upper(), is_active=True)
            return CountryDTO.model_validate(country)
        except Country.DoesNotExist:
            return None

    @lru_cache(maxsize=1)
    def get_all_countries(self) -> Sequence[CountryDTO]:
        """Get all active countries (cached)."""
        from ..models import Country

        countries = Country.objects.filter(is_active=True).order_by("name")
        return tuple(CountryDTO.model_validate(c) for c in countries)

    def search_countries(self, term: str, limit: int = 10) -> Sequence[CountryDTO]:
        """
        Search countries by name or ISO code.

        Args:
            term: Search term
            limit: Maximum results

        Returns:
            List of matching CountryDTOs
        """
        from django.db.models import Q

        from ..models import Country

        qs = Country.objects.filter(
            Q(name__icontains=term) | Q(iso2__icontains=term) | Q(iso3__icontains=term),
            is_active=True
        )[:limit]
        return [CountryDTO.model_validate(c) for c in qs]

    @lru_cache(maxsize=1000)
    def get_state(self, state_id: int) -> Optional[StateDTO]:
        """
        Get state by ID (cached).

        Args:
            state_id: State database ID

        Returns:
            StateDTO or None if not found
        """
        from ..models import State

        try:
            state = State.objects.select_related("country").get(id=state_id, is_active=True)
            return self._state_to_dto(state)
        except State.DoesNotExist:
            return None

    def get_states_by_country(self, country_code: str) -> Sequence[StateDTO]:
        """
        Get all states for a country.

        Args:
            country_code: ISO2 country code

        Returns:
            List of StateDTO for the country
        """
        from ..models import State

        states = State.objects.filter(
            country__iso2=country_code.upper(),
            is_active=True
        ).select_related("country").order_by("name")
        return [self._state_to_dto(s) for s in states]

    @lru_cache(maxsize=5000)
    def get_city(self, city_id: int) -> Optional[CityDTO]:
        """
        Get city by ID (cached).

        Args:
            city_id: City database ID

        Returns:
            CityDTO or None if not found
        """
        from ..models import City

        try:
            city = City.objects.select_related("state", "country").get(id=city_id, is_active=True)
            return self._city_to_dto(city)
        except City.DoesNotExist:
            return None

    def search_cities(
        self,
        term: str,
        country_code: Optional[str] = None,
        limit: int = 20
    ) -> Sequence[CityDTO]:
        """
        Search cities with smart multi-word support.

        Supports:
        - Single word: "bali" -> searches city name
        - Multi-word: "indonesia bali" -> searches city + context (country/state)

        Ranking: context match > exact match > starts with > contains

        Args:
            term: Search term (can be multi-word)
            country_code: Optional ISO2 country code to filter
            limit: Maximum results

        Returns:
            List of matching CityDTOs sorted by relevance
        """
        from django.db.models import Case, IntegerField, Q, Value, When

        from ..models import City

        term = term.strip()
        if not term:
            return []

        words = term.split()
        qs = City.objects.filter(is_active=True)

        if len(words) == 1:
            # Single word: simple city name search
            qs = qs.filter(name__icontains=term)
            primary_term = term
            context_words: list[str] = []
        else:
            # Multi-word: search across city + country/state
            # Build filter: city name matches any word
            city_filter = Q()
            for word in words:
                if len(word) >= 2:
                    city_filter |= Q(name__icontains=word)

            qs = qs.filter(city_filter)

            # Last word is likely the city name, others are context
            primary_term = words[-1]
            context_words = [w for w in words[:-1] if len(w) >= 2]

        # Apply country filter if provided
        if country_code:
            qs = qs.filter(country__iso2=country_code.upper())

        # Build relevance scoring
        relevance_whens = []

        # Highest priority: city name matches AND context (country/state) matches
        if context_words:
            context_q = Q()
            for word in context_words:
                context_q |= (
                    Q(country__name__icontains=word) |
                    Q(country__iso2__iexact=word) |
                    Q(state__name__icontains=word) |
                    Q(state__iso2__iexact=word)
                )
            relevance_whens.append(
                When(Q(name__icontains=primary_term) & context_q, then=Value(-1))
            )

        # Standard relevance: exact > starts with > contains
        relevance_whens.extend([
            When(name__iexact=primary_term, then=Value(0)),
            When(name__istartswith=primary_term, then=Value(1)),
        ])

        qs = qs.annotate(
            relevance=Case(
                *relevance_whens,
                default=Value(2),
                output_field=IntegerField(),
            )
        ).order_by("relevance", "name")

        qs = qs.select_related("state", "country")[:limit]
        return [self._city_to_dto(c) for c in qs]

    def get_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        limit: int = 10,
    ) -> Sequence[NearbyResult]:
        """
        Find cities within radius using bounding box pre-filter.

        Uses geodesic distance calculation for accuracy.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            limit: Maximum results

        Returns:
            List of NearbyResult sorted by distance
        """
        from ..models import City

        try:
            from geopy.distance import geodesic
        except ImportError:
            # geopy not installed - return empty
            return []

        # Approximate degree radius for bounding box pre-filter
        # 1 degree ≈ 111 km at equator
        degree_radius = radius_km / 111.0

        qs = City.objects.filter(
            is_active=True,
            latitude__range=(latitude - degree_radius, latitude + degree_radius),
            longitude__range=(longitude - degree_radius, longitude + degree_radius),
        ).select_related("state", "country")

        results = []
        point = (latitude, longitude)

        for city in qs:
            city_coords = (city.latitude, city.longitude)
            distance = geodesic(point, city_coords).kilometers
            if distance <= radius_km:
                city_dto = self._city_to_dto(city)
                results.append(NearbyResult(city=city_dto, distance_km=distance))

        results.sort(key=lambda x: x.distance_km)
        return results[:limit]

    def calculate_distance(
        self,
        point1: tuple[float, float],
        point2: tuple[float, float],
    ) -> float:
        """
        Calculate geodesic distance between two points.

        Args:
            point1: (latitude, longitude) tuple
            point2: (latitude, longitude) tuple

        Returns:
            Distance in kilometers
        """
        try:
            from geopy.distance import geodesic
            return geodesic(point1, point2).kilometers
        except ImportError:
            # Fallback to simple Euclidean approximation
            lat_diff = point2[0] - point1[0]
            lon_diff = point2[1] - point1[1]
            return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111

    def get_statistics(self) -> dict:
        """Get database statistics."""
        from ..models import City, Country, State

        return {
            "countries": Country.objects.filter(is_active=True).count(),
            "states": State.objects.filter(is_active=True).count(),
            "cities": City.objects.filter(is_active=True).count(),
        }

    def clear_cache(self) -> None:
        """Clear all LRU caches."""
        self.get_country.cache_clear()
        self.get_all_countries.cache_clear()
        self.get_state.cache_clear()
        self.get_city.cache_clear()

    # Private helpers

    def _state_to_dto(self, state) -> StateDTO:
        """Convert State model to StateDTO."""
        return StateDTO(
            id=state.id,
            name=state.name,
            country_id=state.country_id,
            iso2=state.iso2,
            type=state.type,
            latitude=state.latitude,
            longitude=state.longitude,
            country_iso2=state.country.iso2 if state.country else None,
        )

    def _city_to_dto(self, city) -> CityDTO:
        """Convert City model to CityDTO."""
        return CityDTO(
            id=city.id,
            name=city.name,
            state_id=city.state_id,
            country_id=city.country_id,
            latitude=city.latitude,
            longitude=city.longitude,
            state_iso2=city.state.iso2 if city.state else None,
            country_iso2=city.country.iso2 if city.country else None,
        )


def get_geo_db() -> GeoDatabase:
    """Get shared GeoDatabase instance."""
    return GeoDatabase.get_instance()


__all__ = ["GeoDatabase", "get_geo_db"]
