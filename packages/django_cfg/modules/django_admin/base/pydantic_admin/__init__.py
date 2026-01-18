"""
PydanticAdmin - Declarative admin base class.

Provides Pydantic-driven configuration for Django ModelAdmin.

Usage:
    from django_cfg.modules.django_admin import AdminConfig
    from django_cfg.modules.django_admin.base import PydanticAdmin

    config = AdminConfig(
        model=MyModel,
        list_display=["name", "status"],
        ...
    )

    @admin.register(MyModel)
    class MyModelAdmin(PydanticAdmin):
        config = config
"""

from .base_class import get_base_admin_class
from .mixin import PydanticAdminMixin

# For backward compatibility, also export the underscore-prefixed version
_get_base_admin_class = get_base_admin_class


def _get_money_field_mixin():
    """Lazy load MoneyFieldAdminMixin to avoid circular imports."""
    try:
        from django_cfg.modules.django_currency.admin import MoneyFieldAdminMixin
        return MoneyFieldAdminMixin
    except ImportError:
        # django_currency not available, return empty mixin
        class EmptyMixin:
            pass
        return EmptyMixin


class PydanticAdmin(PydanticAdminMixin, _get_money_field_mixin(), get_base_admin_class()):
    """
    Pydantic-driven admin base class with Unfold UI and Import/Export support.

    Inherits from UnfoldImportExportModelAdmin which combines:
    - ImportExportModelAdmin: Import/Export functionality
    - UnfoldModelAdmin: Modern Unfold UI
    - Django ModelAdmin: Base Django admin

    Both Unfold UI and Import/Export are always available.
    Enable import/export functionality via config:
        import_export_enabled=True
        resource_class=YourResourceClass

    Usage:
        from django_cfg.modules.django_admin import AdminConfig
        from django_cfg.modules.django_admin.base import PydanticAdmin

        # Simple admin (Unfold UI enabled by default)
        config = AdminConfig(
            model=MyModel,
            list_display=["name", "status"],
            ...
        )

        @admin.register(MyModel)
        class MyModelAdmin(PydanticAdmin):
            config = config

        # With Import/Export
        config = AdminConfig(
            model=MyModel,
            import_export_enabled=True,
            resource_class=MyModelResource,
            list_display=["name", "status"],
            ...
        )

        @admin.register(MyModel)
        class MyModelAdmin(PydanticAdmin):
            config = config
    """
    pass


__all__ = [
    'PydanticAdmin',
    'PydanticAdminMixin',
    'get_base_admin_class',
    '_get_base_admin_class',  # backward compatibility
]
