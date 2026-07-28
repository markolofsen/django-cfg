"""Runtime analytics configuration shared by ingest and server-side emitters."""

from __future__ import annotations


def get_analytics_config():
    """Return the live config, including a safe standalone-app fallback."""
    from django_cfg.core import get_current_config
    from django_cfg.models.django.analytics import AnalyticsConfig

    config = get_current_config()
    if config is None or config.analytics is None:
        return AnalyticsConfig()
    return config.analytics


__all__ = ["get_analytics_config"]
