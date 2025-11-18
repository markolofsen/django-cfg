---
title: Configuration Guide
description: Complete configuration reference for Django Admin - AdminConfig, decorators, HTML utilities, and display helpers.
sidebar_label: Configuration
sidebar_position: 4
keywords:
  - AdminConfig
  - computed_field
  - HTML builder
  - django admin utilities
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Configuration Guide

Complete reference for configuring Django Admin with AdminConfig, decorators, and utilities.

## AdminConfig Reference

`AdminConfig` is a Pydantic model that defines the complete admin configuration.

### Basic Options

```python
from django_cfg.modules.django_admin import AdminConfig

config = AdminConfig(
    model=MyModel,  # Required: Django model class

    # List display
    list_display=["field1", "field2"],  # Field names
    list_display_links=["field1"],      # Clickable fields (optional)
    list_per_page=50,                   # Pagination
    list_max_show_all=200,              # "Show all" limit

    # Filters and search
    list_filter=["status", "created_at"],
    search_fields=["name", "email"],
    date_hierarchy="created_at",

    # Ordering
    ordering=["-created_at"],

    # Readonly
    readonly_fields=["id", "created_at", "updated_at"],

    # Form options
    autocomplete_fields=["user"],
    raw_id_fields=["foreign_key_field"],
    prepopulated_fields={"slug": ("name",)},

    # Other
    save_on_top=False,
    save_as=False,
    preserve_filters=True,
)
```

### Performance Optimization

```python
config = AdminConfig(
    model=Order,

    # Auto-applied to all queries
    select_related=["user", "product", "shipping_address"],
    prefetch_related=["items", "items__options"],

    # Database aggregations
    annotations={
        'total_items': Count('items'),
        'total_amount': Sum('items__price'),
        'avg_price': Avg('items__price'),
    },
)
```

:::tip[Automatic Optimization]
`select_related` and `prefetch_related` are automatically applied to all queries in the admin. No need to override `get_queryset()`!
:::

### Display Fields

Define specialized field configurations that auto-generate display methods:

```python
from django_cfg.modules.django_admin import (
    BadgeField, BooleanField, CurrencyField,
    DateTimeField, TextField, UserField, Icons,
)

config = AdminConfig(
    model=Payment,

    list_display=["id", "user", "amount", "status", "created_at"],

    display_fields=[
        UserField(name="user", header=True, ordering="user__username"),
        CurrencyField(name="amount", currency="USD", precision=2, ordering="amount"),
        BadgeField(
            name="status",
            label_map={
                "pending": "warning",
                "completed": "success",
                "failed": "danger",
            }
        ),
        DateTimeField(name="created_at", ordering="created_at"),
    ],
)
```

**Each field type automatically generates a `{field_name}_display()` method.**

See [Field Types](./field-types.md) for complete reference.

### Fieldsets

Organize form fields into sections:

```python
from django_cfg.modules.django_admin import FieldsetConfig

config = AdminConfig(
    model=Payment,

    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["id", "internal_payment_id", "user", "status"]
        ),
        FieldsetConfig(
            title="Payment Details",
            fields=["amount_usd", "currency", "pay_amount"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True  # Start collapsed
        ),
    ],
)
```

### Widgets

Configure custom widgets for specific fields using `WidgetConfig` classes. This is especially useful for JSON fields, text fields, and other complex inputs.

#### JSON Widget Configuration

```python
from django_cfg.modules.django_admin import AdminConfig, JSONWidgetConfig

config = AdminConfig(
    model=BotConfig,

    # Centralized widget configuration
    widgets=[
        # Editable JSON field
        JSONWidgetConfig(
            field="settings",
            mode="tree",  # Interactive tree editor
            height="400px",
            show_copy_button=True,
        ),
        # Read-only JSON field
        JSONWidgetConfig(
            field="schema",
            mode="view",  # Read-only display
            height="500px",
            show_copy_button=True,
        ),
    ],

    fieldsets=[
        FieldsetConfig(
            title="Configuration",
            fields=["settings", "schema"],  # Widget config applied automatically
        ),
    ],
)
```

#### JSON Widget Modes

| Mode | Use Case | Features |
|------|----------|----------|
| `tree` | Complex nested JSON | Interactive tree, expand/collapse, inline editing |
| `code` | Raw JSON editing | Text editor with syntax highlighting |
| `view` | Display only | Read-only, formatted display, no editing |

#### JSON Widget Parameters

```python
JSONWidgetConfig(
    field="config_schema",       # Required: field name
    mode="tree",                 # "tree", "code", or "view"
    height="400px",              # Editor height
    width=None,                  # Editor width (default: 100%)
    show_copy_button=True,       # Show copy button (default: True)
)
```

#### Automatic JSON Widget

JSONWidget is **automatically applied** to all Django JSONField models:

```python
from django.db import models

class Bot(models.Model):
    settings = models.JSONField(default=dict)  # Auto-gets JSON editor!

# No widget configuration needed unless you want to customize
```

:::tip[When to Configure]
Only add `JSONWidgetConfig` when you need to:
- Change the editor mode (tree/code/view)
- Adjust height for large JSON
- Disable copy button
- Set specific width
:::

#### Multiple Widget Types

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    JSONWidgetConfig,
    TextWidgetConfig,
)

config = AdminConfig(
    model=Article,

    widgets=[
        # JSON widget for metadata
        JSONWidgetConfig(
            field="metadata",
            mode="tree",
            height="300px",
        ),
        # Text widget for description
        TextWidgetConfig(
            field="description",
            placeholder="Enter article description",
            rows=5,
        ),
    ],
)
```

:::warning[Widget Config Location]
Always define widgets in `AdminConfig.widgets`, not in `FieldsetConfig`. Fieldsets only define field structure.
:::

### Actions

Define admin actions declaratively using `ActionConfig`. This provides a clean, type-safe way to define actions with enhanced UI features.

#### Basic Action Example

```python
from django_cfg.modules.django_admin import ActionConfig
from django.contrib import messages

def mark_as_completed(modeladmin, request, queryset):
    """Mark items as completed."""
    count = queryset.update(status='completed')
    messages.success(request, f"Marked {count} items as completed")

config = AdminConfig(
    model=Payment,

    actions=[
        ActionConfig(
            name="mark_as_completed",
            description="Mark as completed",
            variant="success",
            handler=mark_as_completed
        ),
    ],
)
```

#### ActionConfig Parameters

- **name** (str, required): Action function name - must match the handler function name
- **description** (str, required): Display text shown in the admin actions dropdown
- **action_type** (str, optional): Type of action. Options:
  - `"bulk"` - Traditional bulk action (requires selecting items) - **default**
  - `"changelist"` - Button above the listing (no selection required)
- **variant** (str, optional): Button color variant. Options:
  - `"default"` - Gray button (default)
  - `"success"` - Green button for positive actions
  - `"warning"` - Orange button for cautionary actions
  - `"danger"` - Red button for destructive actions
  - `"primary"` - Blue button for primary actions
  - `"info"` - Light blue button for informational actions
- **icon** (str, optional): Material Icon name (e.g., `"check_circle"`, `"warning"`, `"delete"`)
- **url_path** (str, optional): Custom URL path for changelist actions (auto-generated if not provided)
- **confirmation** (bool, optional): If `True`, shows confirmation dialog before executing (default: `False`)
- **handler** (callable or str, required): Action handler function or import path to handler
- **permissions** (list[str], optional): Required permissions to show this action

:::info Action Handler Signatures
- **Bulk actions**: `handler(modeladmin, request, queryset)` - receives selected items
- **Changelist actions**: `handler(modeladmin, request)` - no queryset, must return HttpResponse
:::

#### Multiple Actions with Different Variants

```python
from django_cfg.modules.django_admin import ActionConfig

config = AdminConfig(
    model=Lead,

    actions=[
        ActionConfig(
            name="mark_as_contacted",
            description="Mark as contacted",
            variant="warning",
            handler=mark_as_contacted
        ),
        ActionConfig(
            name="mark_as_qualified",
            description="Mark as qualified",
            variant="primary",
            handler=mark_as_qualified
        ),
        ActionConfig(
            name="mark_as_converted",
            description="Mark as converted",
            variant="success",
            handler=mark_as_converted
        ),
        ActionConfig(
            name="mark_as_rejected",
            description="Mark as rejected",
            variant="danger",
            handler=mark_as_rejected
        ),
    ],
)
```

#### Actions with Icons and Confirmation

```python
config = AdminConfig(
    model=Document,

    actions=[
        ActionConfig(
            name="publish_documents",
            description="Publish selected documents",
            variant="success",
            icon="publish",
            confirmation=True,  # Shows confirmation dialog
            handler=publish_documents
        ),
        ActionConfig(
            name="archive_documents",
            description="Archive selected documents",
            variant="warning",
            icon="archive",
            confirmation=True,
            handler=archive_documents
        ),
        ActionConfig(
            name="delete_permanently",
            description="Delete permanently",
            variant="danger",
            icon="delete_forever",
            confirmation=True,  # Important for destructive actions!
            handler=delete_permanently
        ),
    ],
)
```

#### Organizing Actions in Separate Files

For cleaner code organization, define action handlers in a separate `actions.py` file:

```python
# leads/admin/actions.py
from django.contrib import messages

def mark_as_contacted(modeladmin, request, queryset):
    """Mark selected leads as contacted."""
    updated = queryset.update(status='contacted')
    messages.success(request, f"Marked {updated} leads as contacted.")

def mark_as_qualified(modeladmin, request, queryset):
    """Mark selected leads as qualified."""
    updated = queryset.update(status='qualified')
    messages.success(request, f"Marked {updated} leads as qualified.")

def mark_as_converted(modeladmin, request, queryset):
    """Mark selected leads as converted."""
    updated = queryset.update(status='converted')
    messages.success(request, f"Marked {updated} leads as converted.")

def mark_as_rejected(modeladmin, request, queryset):
    """Mark selected leads as rejected."""
    updated = queryset.update(status='rejected')
    messages.warning(request, f"Marked {updated} leads as rejected.")
```

```python
# leads/admin/leads_admin.py
from django_cfg.modules.django_admin import AdminConfig, ActionConfig
from .actions import mark_as_contacted, mark_as_qualified, mark_as_converted, mark_as_rejected

config = AdminConfig(
    model=Lead,

    actions=[
        ActionConfig(
            name="mark_as_contacted",
            description="Mark as contacted",
            variant="warning",
            handler=mark_as_contacted
        ),
        ActionConfig(
            name="mark_as_qualified",
            description="Mark as qualified",
            variant="primary",
            handler=mark_as_qualified
        ),
        ActionConfig(
            name="mark_as_converted",
            description="Mark as converted",
            variant="success",
            handler=mark_as_converted
        ),
        ActionConfig(
            name="mark_as_rejected",
            description="Mark as rejected",
            variant="danger",
            handler=mark_as_rejected
        ),
    ],
)
```

#### Actions with Permissions

Restrict actions to users with specific permissions:

```python
config = AdminConfig(
    model=Payment,

    actions=[
        ActionConfig(
            name="approve_payment",
            description="Approve payment",
            variant="success",
            icon="check_circle",
            permissions=["payments.approve_payment"],  # Custom permission
            handler=approve_payment
        ),
        ActionConfig(
            name="reject_payment",
            description="Reject payment",
            variant="danger",
            icon="cancel",
            permissions=["payments.reject_payment"],
            confirmation=True,
            handler=reject_payment
        ),
    ],
)
```

#### Best Practices

1. **Use appropriate variants**: Match button colors to action semantics
   - Green (`success`) for positive actions (approve, complete, publish)
   - Red (`danger`) for destructive actions (delete, reject, cancel)
   - Orange (`warning`) for cautionary actions (archive, suspend)
   - Blue (`primary`) for primary workflow actions

2. **Always use confirmation for destructive actions**: Set `confirmation=True` for actions that delete or permanently modify data

3. **Organize actions in separate files**: Keep action handlers in `actions.py` for better code organization

4. **Use meaningful icons**: Choose icons that clearly represent the action

5. **Add proper permissions**: Restrict sensitive actions using the `permissions` parameter

6. **Provide user feedback**: Always use Django messages to inform users about action results:
   ```python
   from django.contrib import messages

   def my_action(modeladmin, request, queryset):
       count = queryset.update(...)
       messages.success(request, f"Updated {count} items")
   ```

#### Changelist Actions (Buttons Above Listing)

Changelist actions are buttons that appear **above the listing** and don't require selecting items. They're perfect for global operations like imports, exports, synchronizations, or bulk operations.

**Key Differences from Bulk Actions:**

| Feature | Bulk Actions | Changelist Actions |
|---------|-------------|-------------------|
| Location | Dropdown menu | Buttons above listing |
| Selection Required | ✅ Yes | ❌ No |
| Handler Signature | `(modeladmin, request, queryset)` | `(modeladmin, request)` |
| Return Value | None | HttpResponse (redirect) |
| `action_type` | `"bulk"` (default) | `"changelist"` |

**Example: Sync Buttons for External API**

```python
# proxies/admin/actions.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from io import StringIO

def sync_proxy6(modeladmin, request):
    """Synchronize proxies from Proxy6 provider."""
    try:
        messages.info(request, "🔄 Syncing proxies from Proxy6...")

        # Call management command
        out = StringIO()
        call_command('sync_proxy_providers', provider='proxy6', stdout=out)

        # Show command output
        output = out.getvalue()
        if output:
            messages.success(request, output)

    except Exception as e:
        messages.error(request, f"❌ Failed to sync Proxy6: {str(e)}")

    # IMPORTANT: Must return redirect for changelist actions
    return redirect(reverse('admin:proxies_proxy_changelist'))


def sync_all_providers(modeladmin, request):
    """Synchronize proxies from all providers."""
    try:
        messages.info(request, "🔄 Syncing all providers...")

        out = StringIO()
        call_command('sync_proxy_providers', provider='all', stdout=out)

        output = out.getvalue()
        if output:
            messages.success(request, output)

    except Exception as e:
        messages.error(request, f"❌ Failed to sync: {str(e)}")

    return redirect(reverse('admin:proxies_proxy_changelist'))
```

```python
# proxies/admin/proxy_admin.py
from django_cfg.modules.django_admin import AdminConfig, ActionConfig

config = AdminConfig(
    model=Proxy,

    actions=[
        # Bulk actions (require selection)
        ActionConfig(
            name='test_selected_proxies',
            action_type='bulk',  # Default
            description='Test selected proxies',
            variant='warning',
            icon='speed',
            confirmation=True,
            handler='apps.proxies.admin.actions.test_selected_proxies',
        ),

        # Changelist actions (buttons above listing, no selection needed)
        ActionConfig(
            name='sync_all_providers',
            action_type='changelist',  # 🎯 Button above listing!
            description='🔄 Sync All Providers',
            variant='primary',
            icon='sync',
            confirmation=True,
            handler='apps.proxies.admin.actions.sync_all_providers',
        ),
        ActionConfig(
            name='sync_proxy6',
            action_type='changelist',  # 🎯 Button above listing!
            description='Sync Proxy6',
            variant='info',
            icon='cloud_sync',
            handler='apps.proxies.admin.actions.sync_proxy6',
        ),
    ],
)
```

**Result in Admin:**

```
┌────────────────────────────────────────────────────┐
│  [🔄 Sync All Providers]  [Sync Proxy6]            │  ← Changelist actions
├────────────────────────────────────────────────────┤
│  Actions: [▼ Test selected proxies]                │  ← Bulk actions dropdown
│                                                     │
│  ☐  ID    Host      Provider   Status              │
│  ☐  abc   1.2.3.4   proxy6     Active              │
└────────────────────────────────────────────────────┘
```

**Common Use Cases for Changelist Actions:**

- **Data Synchronization**: Sync with external APIs, refresh data
- **Bulk Imports**: Import data from files without selecting items
- **Reports**: Generate reports for all items
- **Cache Operations**: Clear caches, rebuild indexes
- **Maintenance**: Run cleanup tasks, optimize database

:::warning Important for Changelist Actions
1. **Must return HttpResponse**: Always return `redirect()` or other HttpResponse
2. **No queryset parameter**: Handler receives only `(modeladmin, request)`
3. **Use for model-level operations**: Not for selected items
4. **Always provide user feedback**: Use Django messages framework
:::

#### Old-Style Actions (Not Recommended)

**Do NOT use old-style actions with `.short_description` attributes:**

```python
# ❌ BAD - Old-style action
def my_action(self, request, queryset):
    # do stuff
    pass
my_action.short_description = "My Action"

# ✅ GOOD - Use ActionConfig instead
ActionConfig(
    name="my_action",
    description="My Action",
    variant="primary",
    handler=my_action
)
```

Old-style actions lack support for variants, icons, confirmation, and permissions. Always use `ActionConfig` for declarative, feature-rich actions.

### Import/Export

Enable import/export functionality:

```python
from import_export import resources

class PaymentResource(resources.ModelResource):
    class Meta:
        model = Payment
        fields = ('id', 'internal_payment_id', 'amount_usd', 'status')

config = AdminConfig(
    model=Payment,
    import_export_enabled=True,
    resource_class=PaymentResource,
)
```

## Decorators

Django Admin provides decorators for custom display methods.

### @computed_field

For custom display logic in list views:

```python
from django_cfg.modules.django_admin import computed_field, Icons

@admin.register(User)
class UserAdmin(PydanticAdmin):
    config = user_config

    @computed_field("Full Name", ordering="last_name")
    def full_name(self, obj):
        """Display full name with badge."""
        name = obj.get_full_name()
        if not name:
            return self.html.badge("No name", variant="secondary", icon=Icons.PERSON)
        return self.html.badge(name, variant="primary", icon=Icons.PERSON)

    @computed_field("Status", boolean=False)
    def status_display(self, obj):
        """Status with conditional colors."""
        if obj.is_superuser:
            return self.html.badge("Superuser", variant="danger", icon=Icons.ADMIN_PANEL_SETTINGS)
        elif obj.is_staff:
            return self.html.badge("Staff", variant="warning", icon=Icons.SETTINGS)
        elif obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.CANCEL)
```

**Parameters:**
- `short_description` (str): Column header text
- `ordering` (str, optional): Field name for sorting
- `boolean` (bool): Display as boolean icon
- `empty_value` (str): Value when None/empty (default: "—")

### @annotated_field

For values computed from queryset annotations:

```python
from django.db.models import Count
from django_cfg.modules.django_admin import annotated_field

config = AdminConfig(
    model=User,
    annotations={
        'transaction_count': Count('transactions'),
    },
)

@admin.register(User)
class UserAdmin(PydanticAdmin):
    config = config

    @annotated_field("Transactions", annotation_name="transaction_count")
    def transaction_display(self, obj):
        """Display transaction count from annotation."""
        count = getattr(obj, 'transaction_count', 0)
        if count == 0:
            return self.html.empty()
        return self.html.badge(f"{count} transactions", variant="info", icon=Icons.RECEIPT)
```

**Parameters:**
- `short_description` (str): Column header text
- `annotation_name` (str): Name of the annotation in queryset
- `ordering` (str, optional): Field name for sorting (defaults to annotation_name)
- `empty_value` (str): Value when None/empty

## HTML Builder Utilities

Access via `self.html` in any admin method for building rich HTML displays.

### badge()

Colored badge with optional icon:

```python
def status_display(self, obj):
    return self.html.badge(
        "Active",
        variant="success",    # primary, success, warning, danger, info, secondary
        icon=Icons.CHECK_CIRCLE
    )
```

**Variants:**
- `primary` - Blue (default)
- `success` - Green
- `warning` - Yellow/Orange
- `danger` - Red
- `info` - Light blue
- `secondary` - Gray

### span()

Wrapped text with CSS classes:

```python
def custom_display(self, obj):
    return self.html.span("Important", "font-semibold text-red-600")
```

### inline()

Join multiple items horizontally:

```python
def details_display(self, obj):
    return self.html.inline([
        self.html.span("ID:", "font-semibold"),
        self.html.span(obj.id, ""),
        self.html.badge(obj.status, variant="info"),
    ], separator=" | ")
```

**Parameters:**
- `items` (list): List of HTML elements
- `separator` (str): Separator between items (default: " | ")

### icon()

Material icon only:

```python
def has_email_icon(self, obj):
    if obj.email:
        return self.html.icon(Icons.CHECK_CIRCLE, size="sm")
    return self.html.icon(Icons.CANCEL, size="sm")
```

**Sizes:** `xs`, `sm`, `base`, `lg`, `xl`

### icon_text()

Icon + text combination:

```python
def stats_display(self, obj):
    return self.html.inline([
        self.html.icon_text(Icons.EDIT, obj.posts_count),
        self.html.icon_text(Icons.CHAT, obj.comments_count),
    ])
```

### link()

Clickable link:

```python
def external_link(self, obj):
    return self.html.link(
        obj.website_url,
        "Visit Website",
        css_class="text-blue-600",
        target="_blank"
    )
```

### empty()

Empty placeholder:

```python
def optional_field(self, obj):
    if not obj.description:
        return self.html.empty()  # Shows "—"
    return obj.description
```

## Display Utilities

Advanced display utilities for specialized formatting.

### UserDisplay

Utility for user display with avatar support:

```python
from django_cfg.modules.django_admin.utils.displays import UserDisplay
from django_cfg.modules.django_admin.models.display_models import UserDisplayConfig

def user_display(self, obj):
    """User with avatar."""
    config = UserDisplayConfig(
        show_avatar=True,
        show_email=True,
        avatar_size="md"
    )
    return UserDisplay.with_avatar(obj.user, config)

def simple_user(self, obj):
    """Simple user display without avatar."""
    return UserDisplay.simple(obj.user)
```

**UserDisplayConfig Parameters:**
- `show_avatar` (bool): Show avatar image
- `show_email` (bool): Show email below name
- `avatar_size` (str): Avatar size - sm, md, lg

### MoneyDisplay

Utility for currency formatting:

```python
from django_cfg.modules.django_admin.utils.displays import MoneyDisplay
from django_cfg.modules.django_admin.models.display_models import MoneyDisplayConfig

def amount_display(self, obj):
    """Smart currency formatting."""
    config = MoneyDisplayConfig(
        currency="USD",
        decimal_places=2,
        thousand_separator=True,
        show_currency_symbol=True,
        show_sign=False,
        smart_decimal_places=False
    )
    return MoneyDisplay.amount(obj.amount, config)

def rate_display(self, obj):
    """Exchange rate display."""
    config = MoneyDisplayConfig(
        currency="USD",
        rate_mode=True,  # Special formatting for rates
        smart_decimal_places=True  # Auto-adjust decimals
    )
    return MoneyDisplay.amount(obj.exchange_rate, config)
```

**MoneyDisplayConfig Parameters:**
- `currency` (str): Currency code (USD, EUR, BTC, etc.)
- `decimal_places` (int): Number of decimal places (default: 2)
- `thousand_separator` (bool): Add thousand separators
- `show_currency_symbol` (bool): Show currency symbol
- `show_sign` (bool): Show + for positive amounts
- `smart_decimal_places` (bool): Auto-adjust decimals based on amount
- `rate_mode` (bool): Special formatting for exchange rates

### DateTimeDisplay

Utility for datetime formatting:

```python
from django_cfg.modules.django_admin.utils.displays import DateTimeDisplay
from django_cfg.modules.django_admin.models.display_models import DateTimeDisplayConfig

def created_display(self, obj):
    """Datetime with relative time."""
    config = DateTimeDisplayConfig(
        datetime_format="%Y-%m-%d %H:%M",
        show_relative=True
    )
    return DateTimeDisplay.relative(obj.created_at, config)

def compact_time(self, obj):
    """Compact datetime display."""
    return DateTimeDisplay.compact(obj.updated_at)
```

**DateTimeDisplayConfig Parameters:**
- `datetime_format` (str): strftime format string
- `show_relative` (bool): Show "2 hours ago" below absolute time

## Complete Example

Putting it all together:

```python
from django.contrib import admin
from django.db.models import Count
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, CurrencyField, DateTimeField,
    FieldsetConfig, Icons, UserField, computed_field, annotated_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.utils.displays import MoneyDisplay

# Configuration
payment_config = AdminConfig(
    model=Payment,

    # Performance
    select_related=["user", "currency"],
    prefetch_related=["transactions"],
    annotations={
        'transaction_count': Count('transactions'),
    },

    # Display
    list_display=["internal_payment_id", "user", "amount_usd", "status", "transaction_count_display", "created_at"],

    display_fields=[
        BadgeField(name="internal_payment_id", variant="info", icon=Icons.RECEIPT),
        UserField(name="user", header=True, ordering="user__username"),
        CurrencyField(name="amount_usd", currency="USD", precision=2, ordering="amount_usd"),
        BadgeField(
            name="status",
            label_map={
                "pending": "warning",
                "completed": "success",
                "failed": "danger",
            }
        ),
        DateTimeField(name="created_at", ordering="created_at"),
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(title="Basic", fields=["id", "internal_payment_id", "user", "status"]),
        FieldsetConfig(title="Payment", fields=["amount_usd", "currency", "pay_amount"]),
        FieldsetConfig(title="Details", fields=["payment_details_display"], collapsed=True),
    ],

    readonly_fields=["payment_details_display"],
    list_filter=["status", "created_at"],
    search_fields=["internal_payment_id", "user__username"],
)

@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    config = payment_config

    # Computed field with decorator
    @annotated_field("Transactions", annotation_name="transaction_count")
    def transaction_count_display(self, obj):
        """Display transaction count from annotation."""
        count = getattr(obj, 'transaction_count', 0)
        if count == 0:
            return self.html.empty()
        return self.html.badge(f"{count} txns", variant="info", icon=Icons.RECEIPT)

    # Custom readonly field using self.html
    def payment_details_display(self, obj):
        """Detailed payment information."""
        details = []

        # Basic info
        details.append(self.html.inline([
            self.html.span("Internal ID:", "font-semibold"),
            self.html.span(obj.internal_payment_id, "")
        ], separator=" "))

        # Transaction link
        if obj.transaction_hash:
            details.append(self.html.inline([
                self.html.span("Transaction:", "font-semibold"),
                self.html.link(
                    obj.get_explorer_link(),
                    obj.transaction_hash[:16] + "...",
                    target="_blank"
                )
            ], separator=" "))

        # Confirmations badge
        if obj.confirmations_count > 0:
            details.append(self.html.badge(
                f"{obj.confirmations_count} confirmations",
                variant="info",
                icon=Icons.CHECK_CIRCLE
            ))

        # Pay amount with MoneyDisplay utility
        if obj.pay_amount:
            from django_cfg.modules.django_admin.utils.displays import MoneyDisplay
            from django_cfg.modules.django_admin.models.display_models import MoneyDisplayConfig

            config = MoneyDisplayConfig(currency=obj.currency.token, smart_decimal_places=True)
            amount_html = MoneyDisplay.amount(obj.pay_amount, config)
            details.append(self.html.inline([
                self.html.span("Pay Amount:", "font-semibold"),
                amount_html
            ], separator=" "))

        return "<br>".join(details)

    payment_details_display.short_description = "Payment Details"
```

## Best Practices

### 1. Use Declarative Fields When Possible

```python
# ✅ Good - Auto-generated display method
display_fields=[
    CurrencyField(name="amount", currency="USD", precision=2)
]

# ⚠️ Only when needed - Manual method
@computed_field("Amount")
def amount_display(self, obj):
    return f"${obj.amount:.2f}"
```

### 2. Use self.html Builder

```python
# ✅ Good - Rich HTML builder
def status(self, obj):
    return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)

def details(self, obj):
    return self.html.inline([
        self.html.span("ID:", "font-semibold"),
        self.html.badge(obj.id, variant="info"),
    ], separator=" ")
```

### 3. Apply Query Optimizations in Config

```python
# ✅ Good - Automatic optimization
config = AdminConfig(
    model=Order,
    select_related=["user", "product"],
    prefetch_related=["items"],
)

# These optimizations are auto-applied to all queries
```

### 4. Use Annotations for Database Aggregations

```python
# ✅ Database-level computation (efficient)
config = AdminConfig(
    model=User,
    annotations={'order_count': Count('orders')},
)

@annotated_field("Orders", annotation_name="order_count")
def order_count_display(self, obj):
    return self.html.badge(f"{obj.order_count} orders", variant="info")

# ⚠️ Python-level computation (creates N+1 queries)
@computed_field("Orders")
def order_count_display(self, obj):
    count = obj.orders.count()  # Extra query per row
    return f"{count} orders"
```

## Next Steps

- **[Examples](./examples.md)** - Real-world working examples
- **[Field Types](./field-types.md)** - Complete field reference
- **[Filters](./filters.md)** - Complete guide to filters
- **[Quick Start](./quick-start.md)** - Get started guide
