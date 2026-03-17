"""
django_cfg.startup.type_stubs — Auto-install DRF type stubs for Pyright.

Writes typings/rest_framework/serializers.pyi and patches pyrightconfig.json
so that after is_valid(raise_exception=True) Pyright narrows validated_data
to dict[str, Any]. Only runs in development environments.
"""


def install_type_stubs() -> None:
    """Install DRF validated_data type stubs. No-op in production."""
    try:
        import os
        is_dev = os.environ.get("DJANGO_ENV", "development") not in ("production", "prod")
        if not is_dev:
            return

        from django_cfg.core.integration.setup_types import install
        install()

    except Exception:
        pass
