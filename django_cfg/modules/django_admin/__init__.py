"""
Django Admin: declarative configuration with Pydantic.

Type-safe, reusable admin configurations built on django-unfold. Describe a
model admin with an AdminConfig (list columns, display fields, filters,
fieldsets, actions, widgets) and let PydanticAdmin generate the ModelAdmin
attributes and display methods.

Documentation:
    - README.md (this directory): usage guide and field reference
    - @docs/ (this directory): configuration, API reference, architecture, examples
    - Icons: ``from django_cfg import Icons`` (constants live in django_cfg/icons/constants.py)

Quick example:
    ```python
    from django.contrib import admin
    from django_cfg import Icons
    from django_cfg.modules.django_admin import ActionConfig, AdminConfig, BadgeField
    from django_cfg.modules.django_admin.base import PydanticAdmin

    config = AdminConfig(
        model=Payment,
        list_display=["id", "status", "amount"],
        display_fields=[
            BadgeField(name="status", label_map={"pending": "warning", "paid": "success"}),
        ],
        actions=[
            ActionConfig(
                name="approve",
                description="Approve payments",
                action_type="bulk",  # or "changelist"
                icon=Icons.CHECK_CIRCLE,
                handler="apps.payments.admin.actions.approve_payments",
            ),
        ],
    )

    @admin.register(Payment)
    class PaymentAdmin(PydanticAdmin):
        config = config
    ```

PydanticAdmin is not exported here (importing it needs the app registry);
import it from ``django_cfg.modules.django_admin.base``.
"""

# Core config models
from .config import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    BadgeRule,
    BooleanField,
    CurrencyField,
    DateTimeField,
    DecimalField,
    DjangoFieldsets,
    DocumentationConfig,
    FieldConfig,
    FieldConfigType,
    FieldsetConfig,
    FieldsetOptions,
    FieldsetTuple,
    FilterConfig,
    FilterSpec,
    FilterType,
    ForeignKeyField,
    ImageField,
    ImagePreviewField,
    ImagePreviewWidgetConfig,
    JSONWidgetConfig,
    LinkField,
    MarkdownField,
    MoneyFieldDisplay,
    RowItem,
    ShortUUIDField,
    StackedField,
    StatusBadgesField,
    TextField,
    TextWidgetConfig,
    UserField,
    WidgetConfig,
)

# Pydantic models (for advanced usage)
from .models import (
    BadgeConfig,
    BadgeVariant,
    DateTimeDisplayConfig,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    UserDisplayConfig,
)

# Base admin class - NOT imported here to avoid AppRegistryNotReady
# Import PydanticAdmin directly in your admin.py files:
# from django_cfg.modules.django_admin.base import PydanticAdmin
# Display utilities (for custom widgets)
from .utils import (
    CounterBadge,
    DateTimeDisplay,
    ImagePreviewDisplay,
    MarkdownRenderer,
    MoneyDisplay,
    ProgressBadge,
    StatusBadge,
    UserDisplay,
    # Decorators
    annotated_field,
    badge_field,
    computed_field,
    currency_field,
)

# Widget registry
from .widgets import WidgetRegistry

__version__ = "2.0.0"

__all__ = [
    # Core - Primary API
    # "PydanticAdmin",  # Import directly from .base to avoid AppRegistryNotReady
    "AdminConfig",
    "FieldConfig",
    "FieldsetConfig",
    "ActionConfig",
    "DocumentationConfig",
    # Specialized Field Types (for display_fields in list_display)
    "BadgeField",
    "BadgeRule",
    "BooleanField",
    "CurrencyField",
    "DateTimeField",
    "DecimalField",
    "ForeignKeyField",
    "ImageField",
    "ImagePreviewField",
    "LinkField",
    "MarkdownField",
    "MoneyFieldDisplay",
    "RowItem",
    "ShortUUIDField",
    "StackedField",
    "StatusBadgesField",
    "TextField",
    "UserField",
    # Widget Configs (for AdminConfig.widgets - form fields)
    "WidgetConfig",
    "JSONWidgetConfig",
    "TextWidgetConfig",
    "ImagePreviewWidgetConfig",
    # Type aliases and discriminated unions
    "FieldConfigType",
    "FilterSpec",
    "FilterConfig",
    "FilterType",
    "DjangoFieldsets",
    "FieldsetOptions",
    "FieldsetTuple",
    # Advanced
    "WidgetRegistry",
    # Display utilities (for custom widgets)
    "UserDisplay",
    "MoneyDisplay",
    "DateTimeDisplay",
    "ImagePreviewDisplay",
    "StatusBadge",
    "ProgressBadge",
    "CounterBadge",
    "MarkdownRenderer",
    # Decorators
    "computed_field",
    "badge_field",
    "currency_field",
    "annotated_field",
    # Pydantic models (for advanced widget config)
    "UserDisplayConfig",
    "MoneyDisplayConfig",
    "DateTimeDisplayConfig",
    "BadgeConfig",
    "StatusBadgeConfig",
    "BadgeVariant",
]
