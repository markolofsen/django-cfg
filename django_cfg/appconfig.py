"""
Django app configuration for django_cfg.

Lives here, not in `apps.py`: the package `django_cfg/apps/` shadows a module of
that name, so Django never saw an AppConfig defined in it and ready() never ran.
`django_cfg/apps/__init__.py` re-exports DjangoCfgConfig, which is what Django
looks for when it resolves the "django_cfg" INSTALLED_APPS entry.

Each startup concern lives in its own module under django_cfg/startup/:
  constance.py          — Constance + Unfold admin registration
  drf_patch.py          — JWT-aware DRF authentication patch
  mime_types.py         — Media types a slim container image leaves out
  type_stubs.py         — Auto-install DRF validated_data type stubs (dev only)
  registry_validation.py — Validate DJANGO_CFG_REGISTRY entries at startup
  command_shadowing.py  — Warn when a project command shares a name with a django-cfg one
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.startup")


def _run_hook(hook) -> None:
    """Run one startup hook; a failure is logged, never raised."""
    try:
        hook()
    except Exception as exc:  # noqa: BLE001 - startup must never crash on an optional hook
        logger.warning("django_cfg startup hook %s failed: %s", getattr(hook, "__name__", hook), exc)


class DjangoCfgConfig(AppConfig):
    """Configuration for django_cfg app."""

    # Explicit: Django picks this config for the bare "django_cfg" entry.
    default = True
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg"
    verbose_name = "Django Configuration"

    def ready(self) -> None:
        """Called when Django is ready — run all startup hooks.

        Every optional hook is isolated: a failure logs a warning and never
        stops the process. Each hook is idempotent (ready() may run twice).
        """
        try:
            # Import registers the check; nothing to call.
            from django_cfg.startup import command_shadowing  # noqa: F401
        except Exception as exc:  # noqa: BLE001
            logger.warning("django_cfg command_shadowing check not registered: %s", exc)
        from django_cfg.startup.constance import register_constance_admin
        from django_cfg.startup.drf_patch import patch_drf_authentication
        from django_cfg.startup.mime_types import register_media_types
        from django_cfg.startup.registry_validation import validate_registry
        from django_cfg.startup.type_stubs import install_type_stubs

        # First: django-storages reads `mimetypes` when it uploads, so the
        # table has to be complete before anything can write a file.
        for hook in (
            register_media_types,
            register_constance_admin,
            install_type_stubs,
            patch_drf_authentication,
            validate_registry,
        ):
            _run_hook(hook)
