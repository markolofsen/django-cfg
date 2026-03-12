"""
Configuration models for declarative Django Admin.
"""

from .action_config import ActionConfig
from .admin_config import AdminConfig
from .background_task_config import BackgroundTaskConfig
from .documentation_config import DocumentationConfig, DocumentationSection
from .field_config import (
    AvatarField,
    BadgeField,
    BadgeRule,
    BooleanField,
    CounterBadgeField,
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
    VideoField,
)
from .fieldset_config import DjangoFieldsets, FieldsetConfig, FieldsetOptions, FieldsetTuple
from .admin_config import FilterSpec  # re-export TypeAlias
from .filter_config import FilterConfig, FilterType
from .flash_config import FlashFieldConfig, FlashPayload, FlashStyle
from .resource_config import ResourceConfig
from .widget_config import ImagePreviewWidgetConfig, JSONWidgetConfig, TextWidgetConfig, WidgetConfig

__all__ = [
    "AdminConfig",
    "FieldConfig",
    "FieldsetConfig",
    "ActionConfig",
    "ResourceConfig",
    "BackgroundTaskConfig",
    "DocumentationConfig",
    "DocumentationSection",
    # Specialized Field Types (for display_fields)
    "AvatarField",
    "BadgeField",
    "BadgeRule",
    "BooleanField",
    "CounterBadgeField",
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
    "VideoField",
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
    # Flash types
    "FlashFieldConfig",
    "FlashPayload",
    "FlashStyle",
]
