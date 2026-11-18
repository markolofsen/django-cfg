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

from ...actions import action
from .base_class import get_base_admin_class
from .hooks import DROPPED_UNFOLD_ATTRIBUTES, CfgActionsMixin, DroppedUnfoldAttributeWarning
from .mixin import PydanticAdminMixin


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


class PydanticAdmin(PydanticAdminMixin, _get_money_field_mixin(), CfgActionsMixin, get_base_admin_class()):
    """
    Pydantic-driven admin base class on the stock Django admin with Import/Export.

    MRO: PydanticAdminMixin (config) -> MoneyFieldAdminMixin -> CfgActionsMixin
    (``actions_list``/``actions_detail`` buttons, ``list_before_template`` and the
    ``change_form_*`` template hooks) -> ``import_export.admin.ImportExportModelAdmin``
    -> ``django.contrib.admin.ModelAdmin``.

    Import/Export is always available.
    Enable import/export functionality via config:
        import_export_enabled=True
        resource_class=YourResourceClass

    Usage:
        from django_cfg.modules.django_admin import AdminConfig
        from django_cfg.modules.django_admin.base import PydanticAdmin

        # Simple admin
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
    'CfgActionsMixin',
    'DroppedUnfoldAttributeWarning',
    'DROPPED_UNFOLD_ATTRIBUTES',
    'action',
    'get_base_admin_class',
]
