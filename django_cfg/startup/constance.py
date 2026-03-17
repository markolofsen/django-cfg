"""
django_cfg.startup.constance — Register Constance admin with Unfold integration.
"""


def register_constance_admin() -> None:
    """Register Constance admin using Unfold ModelAdmin if both are installed."""
    try:
        from django.conf import settings
        from django.contrib import admin

        if not (hasattr(settings, "CONSTANCE_CONFIG") and settings.CONSTANCE_CONFIG):
            return

        from constance.admin import Config, ConstanceAdmin
        from unfold.admin import ModelAdmin

        class ConstanceConfigAdmin(ConstanceAdmin, ModelAdmin):
            """Constance admin with Unfold integration."""
            pass

        admin.site._registry[Config] = ConstanceConfigAdmin(Config, admin.site)

    except ImportError:
        pass
    except Exception:
        pass
