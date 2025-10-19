"""
Django Admin - Declarative Configuration with Pydantic 2.x

Type-safe, reusable admin configurations using Pydantic models.

Example:
    ```python
    from django_cfg.modules.django_admin import (
        PydanticAdmin, AdminConfig, FieldConfig, FieldsetConfig
    )

    user_balance_config = AdminConfig(
        model=UserBalance,
        list_display=["user", "balance_usd", "status"],
        display_fields=[
            FieldConfig(
                name="user",
                title="User",
                ui_widget="user_avatar",
                header=True
            ),
            FieldConfig(
                name="balance_usd",
                title="Balance (USD)",
                ui_widget="currency",
                currency="USD",
                precision=2
            ),
        ],
        fieldsets=[
            FieldsetConfig(
                title="Balance Details",
                fields=["balance_usd", "total_deposited"]
            ),
        ],
        select_related=["user"],
    )

    @admin.register(UserBalance)
    class UserBalanceAdmin(PydanticAdmin):
        config = user_balance_config
    ```
"""

# Core config models
from .config import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    FieldConfig,
    FieldsetConfig,
    ImageField,
    TextField,
    UserField,
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
    # Specialized Field Types
    "BadgeField",
    "BooleanField",
    "CurrencyField",
    "DateTimeField",
    "ImageField",
    "TextField",
    "UserField",
    # Advanced
    "WidgetRegistry",
    # Icons
    "Icons",
    "IconCategories",
    # Display utilities (for custom widgets)
    "UserDisplay",
    "MoneyDisplay",
    "DateTimeDisplay",
    "StatusBadge",
    "ProgressBadge",
    "CounterBadge",
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
