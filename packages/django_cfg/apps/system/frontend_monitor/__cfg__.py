"""
Frontend Monitor internal settings accessor.

All services and commands call get_settings() to read runtime config.
"""

from django_cfg.models.django.frontend_monitor import FrontendMonitorConfig


def get_settings() -> FrontendMonitorConfig:
    """
    Return the current FrontendMonitorConfig from DjangoConfig.

    Falls back to defaults if config is not set or DjangoConfig is not loaded yet
    (e.g. during makemigrations).
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if config and config.frontend_monitor:
            return config.frontend_monitor
    except Exception:
        pass
    return FrontendMonitorConfig()
