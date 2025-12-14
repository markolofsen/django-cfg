"""
Django Admin - Declarative Configuration with Pydantic 2.x

Type-safe, reusable admin configurations using Pydantic models.
Provides 60-80% code reduction compared to traditional Django admin.

📚 Full Documentation:
    - README.md (this directory) - Complete examples and usage guide
    - ../../../docs_public/django_admin/ - Detailed documentation
    - icons/constants.py - All 2234 available Material Design Icons

🎨 Available Icons (2234 total):
    Icons.DASHBOARD, Icons.SETTINGS, Icons.PEOPLE, Icons.SYNC, Icons.CHECK_CIRCLE,
    Icons.ERROR, Icons.WARNING, Icons.INFO, Icons.DELETE, Icons.EDIT, Icons.ADD,
    Icons.SEARCH, Icons.FILTER, Icons.DOWNLOAD, Icons.UPLOAD, Icons.REFRESH, Icons.CLOSE,
    Icons.MENU, Icons.NOTIFICATION, Icons.EMAIL, Icons.PHONE, Icons.MESSAGE, Icons.CALENDAR,
    Icons.CLOCK, Icons.LOCATION, Icons.STAR, Icons.FAVORITE, Icons.SHARE, Icons.VISIBILITY,
    Icons.LOCK, Icons.ACCOUNT_CIRCLE, Icons.PAYMENT, Icons.SHOPPING_CART, Icons.CREDIT_CARD,
    Icons.RECEIPT, Icons.BUSINESS, Icons.WORK, Icons.HOME, Icons.SCHOOL, Icons.ATTACH_FILE,
    Icons.FOLDER, Icons.CLOUD, Icons.STORAGE, Icons.SECURITY, Icons.PLAY_ARROW, Icons.PAUSE,
    Icons.STOP, Icons.VOLUME_UP, Icons.WIFI, Icons.BLUETOOTH, Icons.BATTERY_FULL, and 2180+ more.
    See icons/constants.py for the complete list.

Quick Example:
    ```python
    from django.contrib import admin
    from django_cfg.modules.django_admin import AdminConfig, ActionConfig, BadgeField, Icons
    from django_cfg.modules.django_admin.base import PydanticAdmin

    config = AdminConfig(
        model=Payment,
        list_display=["id", "status", "amount"],
        display_fields=[
            BadgeField(name="status", label_map={"pending": "warning"}),
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

For complete examples and documentation, see README.md in this directory.
"""

# Core config models
from .config import (
    ActionConfig,
    AdminConfig,
    AvatarField,
    BackgroundTaskConfig,
    BadgeField,
    BadgeRule,
    BooleanField,
    CounterBadgeField,
    CurrencyField,
    DateTimeField,
    DecimalField,
    DocumentationConfig,
    FieldConfig,
    FieldsetConfig,
    ForeignKeyField,
    ImageField,
    ImagePreviewField,
    ImagePreviewWidgetConfig,
    JSONWidgetConfig,
    LinkField,
    MarkdownField,
    ResourceConfig,
    ShortUUIDField,
    StatusBadgesField,
    TextField,
    TextWidgetConfig,
    UserField,
    VideoField,
    WidgetConfig,
)

# Widget registry
from .widgets import WidgetRegistry

# Base admin class - NOT imported here to avoid AppRegistryNotReady
# Import PydanticAdmin directly in your admin.py files:
# from django_cfg.modules.django_admin.base import PydanticAdmin

# Icons (optional)
from .icons import IconCategories, Icons

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
    VideoDisplay,
    # Decorators
    annotated_field,
    badge_field,
    computed_field,
    currency_field,
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

__version__ = "2.0.0"

__all__ = [
    # Core - Primary API
    # "PydanticAdmin",  # Import directly from .base to avoid AppRegistryNotReady
    "AdminConfig",
    "FieldConfig",
    "FieldsetConfig",
    "ActionConfig",
    "ResourceConfig",
    "BackgroundTaskConfig",
    "DocumentationConfig",
    # Specialized Field Types (for display_fields in list_display)
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
    "ShortUUIDField",
    "StatusBadgesField",
    "TextField",
    "UserField",
    "VideoField",
    # Widget Configs (for AdminConfig.widgets - form fields)
    "WidgetConfig",
    "JSONWidgetConfig",
    "TextWidgetConfig",
    "ImagePreviewWidgetConfig",
    # Advanced
    "WidgetRegistry",
    # Icons
    "Icons",
    "IconCategories",
    # Display utilities (for custom widgets)
    "UserDisplay",
    "MoneyDisplay",
    "DateTimeDisplay",
    "ImagePreviewDisplay",
    "VideoDisplay",
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
