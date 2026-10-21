"""
django_cfg.startup.type_stubs — Auto-install DRF type stubs for Pyright.

Writes typings/rest_framework/serializers.pyi and patches pyrightconfig.json
so that after is_valid(raise_exception=True) Pyright narrows validated_data
to dict[str, Any]. Only runs in a development context, and only writes inside
a project root (a directory with manage.py or pyrightconfig.json), never into
site-packages or the environment.
"""

import logging
import os

logger = logging.getLogger("django_cfg.startup")

_NON_DEV_ENVS = ("production", "prod", "staging", "stage", "test", "testing", "ci")


def _is_dev_context() -> bool:
    """True only for DEBUG=True outside production-like envs and containers."""
    from django.conf import settings

    if not getattr(settings, "DEBUG", False):
        return False
    if os.environ.get("DJANGO_ENV", "development").strip().lower() in _NON_DEV_ENVS:
        return False
    # Containers (Docker/Kubernetes) are never a place to write project files.
    if os.path.exists("/.dockerenv") or os.environ.get("KUBERNETES_SERVICE_HOST"):
        return False
    return True


def install_type_stubs() -> None:
    """Install DRF validated_data type stubs. No-op unless in a DEBUG dev context."""
    try:
        if not _is_dev_context():
            return

        from django_cfg.core.integration.setup_types import install
        install()

    except Exception as exc:
        logger.debug("django-cfg: type stubs skipped: %s", exc)
