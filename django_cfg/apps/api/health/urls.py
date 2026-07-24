"""
Django CFG Health Check URLs.
"""

from django.urls import path

from . import drf_views, views

urlpatterns = [
    # Process liveness endpoints. These are deliberately dependency-free.
    path('healthz', views.LiveHealthView.as_view(), name='django_cfg_health'),
    path('healthz/', views.LiveHealthView.as_view()),
    path('healthz/live', views.LiveHealthView.as_view(), name='django_cfg_live_health'),
    path('healthz/live/', views.LiveHealthView.as_view()),

    # Readiness checks dependencies required to serve the Django contract.
    path('healthz/ready', views.HealthCheckView.as_view(), name='django_cfg_ready_health'),
    path('healthz/ready/', views.HealthCheckView.as_view()),

    # DRF Browsable API endpoints with Tailwind theme.
    path('healthz/drf/', drf_views.DRFLiveHealthView.as_view(), name='django_cfg_drf_health'),
    path('healthz/ready/drf/', drf_views.DRFHealthCheckView.as_view(), name='django_cfg_drf_ready_health'),
]
