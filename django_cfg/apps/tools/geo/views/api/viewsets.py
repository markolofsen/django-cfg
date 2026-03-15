"""
Geo API ViewSets (Read-Only)

Provides REST API and Select2-compatible endpoints for:
- Countries (list, retrieve, search)
- States (list by country)
- Cities (search, retrieve, nearby)
"""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...models import Country, State, City
from ...services.database import get_geo_db
from ...services.geocoding import get_geocoding_service
from ..serializers import (
    CountryListSerializer,
    CountryDetailSerializer,
    CountrySelect2Serializer,
    StateListSerializer,
    StateDetailSerializer,
    StateSelect2Serializer,
    CityListSerializer,
    CityDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List countries",
        description="Get list of all active countries with search and filtering",
        parameters=[
            OpenApiParameter(name='search', description='Search by name or ISO code', type=str),
            OpenApiParameter(name='region', description='Filter by region', type=str),
            OpenApiParameter(name='ordering', description='Order by field (name, -name)', type=str),
        ],
    ),
    retrieve=extend_schema(
        summary="Get country details",
        description="Get full country details including states and cities count",
    ),
)
class CountryViewSet(ReadOnlyModelViewSet):
    """
    Read-only ViewSet for countries.

    Endpoints:
    - GET /countries/ - List all countries
    - GET /countries/{iso2}/ - Get country by ISO2 code
    - GET /countries/select2/ - Select2-compatible format
    """

    queryset = Country.objects.none()
    serializer_class = CountryListSerializer
    lookup_field = 'iso2'
    lookup_value_regex = '[A-Z]{2}'

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'iso2', 'iso3']
    ordering_fields = ['name', 'region']
    ordering = ['name']
    filterset_fields = ['region', 'subregion']

    def get_queryset(self):
        """Get active countries."""
        return Country.objects.filter(is_active=True)

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return CountryDetailSerializer
        if self.action == 'select2':
            return CountrySelect2Serializer
        return CountryListSerializer

    @extend_schema(
        summary="Select2 format",
        description="Get countries in Select2-compatible format with pagination",
        parameters=[
            OpenApiParameter(name='term', description='Search term', type=str),
            OpenApiParameter(name='page', description='Page number', type=int),
        ],
        responses={200: CountrySelect2Serializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def select2(self, request):
        """Select2-compatible endpoint for country dropdown."""
        term = request.GET.get('term', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = 20

        qs = self.get_queryset()
        if term:
            qs = qs.filter(name__icontains=term) | qs.filter(iso2__icontains=term)

        total = qs.count()
        start = (page - 1) * per_page
        end = start + per_page
        results = qs[start:end]

        serializer = CountrySelect2Serializer(results, many=True)
        return Response({
            'results': [{'id': c['id'], 'text': c['text']} for c in serializer.data],
            'pagination': {'more': end < total},
        })


@extend_schema_view(
    list=extend_schema(
        summary="List states",
        description="Get list of states/provinces, optionally filtered by country",
        parameters=[
            OpenApiParameter(name='country', description='Country ISO2 code', type=str, required=True),
            OpenApiParameter(name='search', description='Search by name', type=str),
        ],
    ),
    retrieve=extend_schema(
        summary="Get state details",
        description="Get full state details with cities count",
    ),
)
class StateViewSet(ReadOnlyModelViewSet):
    """
    Read-only ViewSet for states/provinces.

    Endpoints:
    - GET /states/?country=KR - List states by country
    - GET /states/{id}/ - Get state details
    - GET /states/select2/?country=KR - Select2-compatible format
    """

    queryset = State.objects.none()
    serializer_class = StateListSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'iso2']
    ordering_fields = ['name']
    ordering = ['name']

    def get_queryset(self):
        """Get active states, filtered by country."""
        qs = State.objects.filter(is_active=True).select_related('country')

        country = self.request.GET.get('country', '').strip().upper()
        if country:
            qs = qs.filter(country__iso2=country)

        return qs

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return StateDetailSerializer
        if self.action == 'select2':
            return StateSelect2Serializer
        return StateListSerializer

    @extend_schema(
        summary="Select2 format",
        description="Get states in Select2-compatible format",
        parameters=[
            OpenApiParameter(name='country', description='Country ISO2 code', type=str, required=True),
        ],
        responses={200: StateSelect2Serializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def select2(self, request):
        """Select2-compatible endpoint for state dropdown."""
        country = request.GET.get('country', '').strip().upper()

        if not country:
            return Response({
                'results': [],
                'pagination': {'more': False},
            })

        qs = State.objects.filter(
            is_active=True,
            country__iso2=country,
        ).order_by('name')

        serializer = StateSelect2Serializer(qs, many=True)
        return Response({
            'results': [{'id': s['id'], 'text': s['text']} for s in serializer.data],
            'pagination': {'more': False},
        })


@extend_schema_view(
    list=extend_schema(
        summary="Search cities",
        description="Search cities by name with relevance ranking. Returns Select2-compatible format.",
        parameters=[
            OpenApiParameter(name='term', description='Search term (min 2 chars)', type=str, required=True),
            OpenApiParameter(name='country', description='Filter by country ISO2 code', type=str),
            OpenApiParameter(name='page', description='Page number', type=int),
        ],
    ),
    retrieve=extend_schema(
        summary="Get city details",
        description="Get full city details with country and state info",
    ),
)
class CityViewSet(ReadOnlyModelViewSet):
    """
    Read-only ViewSet for cities.

    Endpoints:
    - GET /cities/?term=Bali - Search cities (Select2 compatible)
    - GET /cities/{id}/ - Get city details
    - GET /cities/nearby/?lat=...&lng=... - Find nearby cities
    """

    queryset = City.objects.none()
    serializer_class = CityListSerializer

    def get_queryset(self):
        """Get active cities with related data."""
        return City.objects.filter(is_active=True).select_related('state', 'country')

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return CityDetailSerializer
        return CityListSerializer

    def list(self, request, *args, **kwargs):
        """
        Search cities - Select2 compatible.

        Supports multi-word search via GeoDatabase.search_cities().

        Query params:
            term: Search term (min 2 chars)
            country: Country ISO2 filter
            page: Page number
        """
        term = request.GET.get('term', '').strip()
        country = request.GET.get('country', '').strip().upper() or None
        page = int(request.GET.get('page', 1))
        per_page = 20

        if not term or len(term) < 2:
            return Response({
                'results': [],
                'pagination': {'more': False},
            })

        # Use service for search
        db = get_geo_db()
        cities = db.search_cities(term, country_code=country, limit=100)

        # Paginate
        total = len(cities)
        start = (page - 1) * per_page
        end = start + per_page
        results = cities[start:end]

        # Build Select2-compatible response
        data = [
            {
                'id': city.id,
                'text': city.display_name,
                'latitude': city.latitude,
                'longitude': city.longitude,
            }
            for city in results
        ]

        return Response({
            'results': data,
            'pagination': {'more': end < total},
        })

    @extend_schema(
        summary="Find nearby cities",
        description="Find cities within radius of given coordinates",
        parameters=[
            OpenApiParameter(name='lat', description='Latitude', type=float, required=True),
            OpenApiParameter(name='lng', description='Longitude', type=float, required=True),
            OpenApiParameter(name='radius', description='Search radius in km (default: 100)', type=float),
            OpenApiParameter(name='limit', description='Maximum results (default: 5)', type=int),
        ],
    )
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearest cities by coordinates."""
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        limit = int(request.GET.get('limit', 5))
        radius = float(request.GET.get('radius', 100))

        if not lat or not lng:
            return Response(
                {'results': [], 'error': 'lat and lng are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(lat)
            longitude = float(lng)
        except ValueError:
            return Response(
                {'results': [], 'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )

        db = get_geo_db()
        nearby = db.get_nearby_cities(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius,
            limit=limit,
        )

        results = []
        for item in nearby:
            city = item.city
            country = db.get_country(city.country_iso2) if city.country_iso2 else None
            results.append({
                'id': city.id,
                'name': city.name,
                'country': city.country_iso2 or '',
                'country_name': country.name if country else '',
                'flag': country.emoji if country else '',
                'lat': city.latitude,
                'lng': city.longitude,
                'distance_km': round(item.distance_km, 2),
            })

        return Response({'results': results})

    @extend_schema(
        summary="Geocode address",
        description="Convert address to coordinates using Nominatim (OpenStreetMap)",
        parameters=[
            OpenApiParameter(name='address', description='Address to geocode', type=str, required=True),
            OpenApiParameter(name='country', description='Country ISO2 code to limit search', type=str),
        ],
    )
    @action(detail=False, methods=['get'])
    def geocode(self, request):
        """
        Geocode an address to coordinates.

        GET /cfg/geo/cities/geocode/?address=Seoul, South Korea
        """
        address = request.GET.get('address', '').strip()
        country = request.GET.get('country', '').strip().upper() or None

        if not address:
            return Response(
                {'error': 'address parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = get_geocoding_service()
        result = service.geocode(address, country_code=country)

        if not result:
            return Response(
                {'error': 'Address not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'latitude': result.latitude,
            'longitude': result.longitude,
            'display_name': result.display_name,
            'address': result.address.model_dump(),
            'confidence': result.confidence,
            'source': result.source,
        })

    @extend_schema(
        summary="Autocomplete search",
        description="Fast, typo-tolerant location autocomplete using Photon API",
        parameters=[
            OpenApiParameter(name='q', description='Search query (min 2 chars)', type=str, required=True),
            OpenApiParameter(name='limit', description='Maximum results (default: 5)', type=int),
            OpenApiParameter(name='lang', description='Language code (default: en)', type=str),
        ],
    )
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """
        Autocomplete search using Photon API.

        Fast, typo-tolerant search that returns cities, places, streets, POIs.
        Combines local database results with Photon API results.

        GET /cfg/geo/cities/autocomplete/?q=bali
        """
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 5))
        lang = request.GET.get('lang', 'en').strip()

        if not query or len(query) < 2:
            return Response({'results': []})

        service = get_geocoding_service()
        results = service.autocomplete(query, limit=limit, lang=lang)

        return Response({
            'results': [r.model_dump() for r in results]
        })

    @extend_schema(
        summary="Reverse geocode",
        description="Convert coordinates to address using Nominatim (OpenStreetMap)",
        parameters=[
            OpenApiParameter(name='lat', description='Latitude', type=float, required=True),
            OpenApiParameter(name='lng', description='Longitude', type=float, required=True),
        ],
    )
    @action(detail=False, methods=['get'])
    def reverse_geocode(self, request):
        """
        Reverse geocode coordinates to address.

        GET /cfg/geo/cities/reverse_geocode/?lat=37.5665&lng=126.978
        """
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        if not lat or not lng:
            return Response(
                {'error': 'lat and lng parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(lat)
            longitude = float(lng)
        except ValueError:
            return Response(
                {'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = get_geocoding_service()
        result = service.reverse_geocode(latitude, longitude)

        if not result:
            return Response(
                {'error': 'Location not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'display_name': result.display_name,
            'address': result.address.model_dump(),
            'city_id': result.city_id,
            'city_name': result.city_name,
            'distance_to_city_center': result.distance_to_city_center,
            'source': result.source,
        })
