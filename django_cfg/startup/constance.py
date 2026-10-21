"""
django_cfg.startup.constance — Register Constance admin with Unfold integration.
"""

import logging

logger = logging.getLogger("django_cfg.startup")

_admin_class = None


def _get_admin_class():
    """Build the Unfold-flavoured Constance admin once (None if deps are missing)."""
    global _admin_class
    if _admin_class is None:
        from constance.admin import ConstanceAdmin
        from unfold.admin import ModelAdmin

        class ConstanceConfigAdmin(ConstanceAdmin, ModelAdmin):
            """Constance admin with Unfold integration."""

        _admin_class = ConstanceConfigAdmin
    return _admin_class


def register_constance_admin() -> None:
    """Register Constance admin using Unfold ModelAdmin if both are installed. Idempotent."""
    try:
        from django.apps import apps
        from django.conf import settings
        from django.contrib import admin

        if not (hasattr(settings, "CONSTANCE_CONFIG") and settings.CONSTANCE_CONFIG):
            return
        if not apps.is_installed("constance"):
            return

        from constance.admin import Config

        admin_class = _get_admin_class()
        current = admin.site._registry.get(Config)
        if isinstance(current, admin_class):
            return  # already ours; never register twice

        # Constance registered its own admin on import; swap it for ours.
        # The private registry is touched directly: unregister()+register()
        # would raise NotRegistered/AlreadyRegistered depending on load order.
        admin.site._registry[Config] = admin_class(Config, admin.site)

    except ImportError:
        pass  # constance or unfold not installed
    except Exception as exc:
        logger.warning("django-cfg: could not register Constance admin: %s", exc)
