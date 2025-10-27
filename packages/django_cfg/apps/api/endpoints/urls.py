"""
Django CFG Endpoints URLs.
"""

from django.urls import path

from .endpoints_status import DRFEndpointsStatusView, EndpointsStatusView
from .urls_list import DRFURLsListCompactView, DRFURLsListView

urlpatterns = [
    # Endpoints Status - Original JSON endpoint
    path('', EndpointsStatusView.as_view(), name='endpoints_status'),

    # Endpoints Status - DRF Browsable API endpoint with Tailwind theme
    path('drf/', DRFEndpointsStatusView.as_view(), name='endpoints_status_drf'),

    # URLs List - Full details
    path('urls/', DRFURLsListView.as_view(), name='urls_list'),

    # URLs List - Compact (pattern + name only)
    path('urls/compact/', DRFURLsListCompactView.as_view(), name='urls_list_compact'),
]
