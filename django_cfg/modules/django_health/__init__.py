"""
Django Health Check Module for django_cfg.

Auto-configuring health check endpoints.
"""

from .service import HealthCheckView, SimpleHealthView, get_health_urls

__all__ = ["HealthCheckView", "SimpleHealthView", "get_health_urls"]
