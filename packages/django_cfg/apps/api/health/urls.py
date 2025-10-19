"""
Django CFG Health Check URLs.
"""

from django.urls import path

from . import drf_views, views

urlpatterns = [
    # Original JSON endpoints
    path('', views.HealthCheckView.as_view(), name='django_cfg_health'),
    path('quick/', views.QuickHealthView.as_view(), name='django_cfg_quick_health'),

    # DRF Browsable API endpoints with Tailwind theme
    path('drf/', drf_views.DRFHealthCheckView.as_view(), name='django_cfg_drf_health'),
    path('drf/quick/', drf_views.DRFQuickHealthView.as_view(), name='django_cfg_drf_quick_health'),
]
