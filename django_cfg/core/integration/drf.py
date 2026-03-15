"""DRF integration utilities for django_cfg."""


def reload_drf_api_settings(rest_framework_settings: dict) -> None:
    """Reload DRF api_settings to pick up new REST_FRAMEWORK settings.

    DRF's api_settings is a singleton that caches settings on first access.
    If DRF is imported before django_cfg generates settings, it will cache
    wrong defaults. This resets the cache so DRF picks up correct settings.

    This MUST be called during get_all_settings() before settings are returned,
    because view classes get their schema attribute set when they're imported,
    and that happens during Django app loading which occurs after settings
    are applied via locals().update().

    Args:
        rest_framework_settings: The REST_FRAMEWORK dict to apply
    """
    if not rest_framework_settings:
        return

    try:
        from rest_framework import settings as rf_settings

        # Reset the cached settings and apply our new ones
        rf_settings.api_settings._user_settings = rest_framework_settings
        rf_settings.api_settings._cached_attrs = set()

    except ImportError:
        # DRF not installed
        pass
    except Exception:
        # Any error - silently skip
        pass
