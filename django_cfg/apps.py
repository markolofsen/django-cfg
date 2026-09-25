"""
Django app configuration for django_cfg.

Each startup concern lives in its own module under django_cfg/startup/:
  constance.py          — Constance + Unfold admin registration
  drf_patch.py          — JWT-aware DRF authentication patch
  mime_types.py         — Media types a slim container image leaves out
  type_stubs.py         — Auto-install DRF validated_data type stubs (dev only)
  registry_validation.py — Validate DJANGO_CFG_REGISTRY entries at startup
"""

from django.apps import AppConfig


class DjangoCfgConfig(AppConfig):
    """Configuration for django_cfg app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg"
    verbose_name = "Django Configuration"

    def ready(self) -> None:
        """Called when Django is ready — run all startup hooks."""
        from django_cfg.startup.constance import register_constance_admin
        from django_cfg.startup.drf_patch import patch_drf_authentication
        from django_cfg.startup.mime_types import register_media_types
        from django_cfg.startup.type_stubs import install_type_stubs
        from django_cfg.startup.registry_validation import validate_registry

        # First: django-storages reads `mimetypes` when it uploads, so the
        # table has to be complete before anything can write a file.
        register_media_types()

        register_constance_admin()
        install_type_stubs()
        patch_drf_authentication()
        validate_registry()
