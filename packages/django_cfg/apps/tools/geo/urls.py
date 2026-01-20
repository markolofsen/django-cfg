"""
URL configuration for geo app.

Provides DRF API endpoints and Select2-compatible search endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CountryViewSet,
    StateViewSet,
    CityViewSet,
)

app_name = "cfg_geo"

router = DefaultRouter()
router.register('countries', CountryViewSet, basename='country')
router.register('states', StateViewSet, basename='state')
router.register('cities', CityViewSet, basename='city')

urlpatterns = [
    # DRF router URLs
    path('', include(router.urls)),

    # Backward-compatible aliases for widget (Select2-style endpoints)
    # These are redirects to the new API endpoints
    path(
        'search/countries/',
        CountryViewSet.as_view({'get': 'select2'}),
        name='search-countries'
    ),
    path(
        'search/states/',
        StateViewSet.as_view({'get': 'select2'}),
        name='search-states'
    ),
    path(
        'search/cities/',
        CityViewSet.as_view({'get': 'list'}),
        name='search-cities'
    ),
    path(
        'search/nearby/',
        CityViewSet.as_view({'get': 'nearby'}),
        name='search-nearby'
    ),
    path(
        'search/autocomplete/',
        CityViewSet.as_view({'get': 'autocomplete'}),
        name='search-autocomplete'
    ),

    # Geocoding endpoints
    path(
        'cities/geocode/',
        CityViewSet.as_view({'get': 'geocode'}),
        name='city-geocode'
    ),
    path(
        'cities/reverse_geocode/',
        CityViewSet.as_view({'get': 'reverse_geocode'}),
        name='city-reverse-geocode'
    ),

    # Single item endpoints (backward compatible)
    path(
        'city/<int:pk>/',
        CityViewSet.as_view({'get': 'retrieve'}),
        name='get-city'
    ),
    path(
        'country/<str:iso2>/',
        CountryViewSet.as_view({'get': 'retrieve'}),
        name='get-country'
    ),
]
