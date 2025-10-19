"""
Main URL Configuration for Payments v2.0.

Mounts API under /api/v1/payments/
"""

from django.urls import path, include

app_name = 'django_cfg_payments'

urlpatterns = [
    # API endpoints
    path('', include('django_cfg.apps.payments.api.urls')),
]
