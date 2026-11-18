"""
Configuration models for declarative Django Admin.
"""

from .action_config import ActionConfig
from .admin_config import (
    AdminConfig,
    FilterSpec,  # re-export TypeAlias
)
from .documentation import DocumentationConfig, DocumentationSection
from .field_config import (
    BadgeField,
    BadgeRule,
    BooleanField,
    CurrencyField,
    DateTimeField,
    DecimalField,
    FieldConfig,
    FieldConfigType,
    ForeignKeyField,
    ImageField,
    ImagePreviewField,
    LinkField,
    MarkdownField,
    MoneyFieldDisplay,
    RowItem,
    ShortUUIDField,
    StackedField,
    StatusBadgesField,
    TextField,
    UserField,
)
from .fieldset_config import DjangoFieldsets, FieldsetConfig, FieldsetOptions, FieldsetTuple
from .filter_config import FilterConfig, FilterType
from .widget_config import (
    ImagePreviewWidgetConfig,
    JSONWidgetConfig,
    TextWidgetConfig,
    WidgetConfig,
)

__all__ = [
    "AdminConfig",
    "FieldConfig",
    "FieldsetConfig",
    "ActionConfig",
    "DocumentationConfig",
    "DocumentationSection",
    # Specialized Field Types (for display_fields)
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
]
