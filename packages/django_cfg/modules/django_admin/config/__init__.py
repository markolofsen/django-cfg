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
    FieldConfig,
    ImageField,
    LinkField,
    MarkdownField,
    ShortUUIDField,
    StatusBadgesField,
    TextField,
    UserField,
)
from .fieldset_config import FieldsetConfig
from .resource_config import ResourceConfig
from .widget_config import JSONWidgetConfig, TextWidgetConfig, WidgetConfig

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
    "ImageField",
    "LinkField",
    "MarkdownField",
    "ShortUUIDField",
    "StatusBadgesField",
    "TextField",
    "UserField",
    # Widget Configs (for AdminConfig.widgets - form fields)
    "WidgetConfig",
    "JSONWidgetConfig",
    "TextWidgetConfig",
]
