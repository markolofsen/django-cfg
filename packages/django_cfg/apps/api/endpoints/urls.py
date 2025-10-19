"""
Django CFG Endpoints Status URLs.
"""

from django.urls import path

from . import drf_views, views

urlpatterns = [
    # Original JSON endpoint
    path('', views.EndpointsStatusView.as_view(), name='endpoints_status'),

    # DRF Browsable API endpoint with Tailwind theme
    path('drf/', drf_views.DRFEndpointsStatusView.as_view(), name='endpoints_status_drf'),
]
