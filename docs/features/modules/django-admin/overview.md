---
title: Django Admin Module Overview
description: Declarative Pydantic-based Django admin configuration with type-safe field definitions, automatic display methods, and modern UI components.
sidebar_label: Overview & Philosophy
sidebar_position: 1
keywords:
  - django admin
  - pydantic admin
  - django-cfg admin
  - declarative admin
  - type-safe admin
---

# Django Admin Module

Django-CFG includes a **revolutionary Pydantic-based admin system** that transforms how you build Django admin interfaces. Say goodbye to verbose admin classes and hello to clean, declarative, type-safe configurations.

## Overview

The Django Admin module provides:
- **Declarative Configuration** - Define admin interfaces using Pydantic models
- **Type Safety** - Full Pydantic 2.x validation and IDE autocomplete
- **Specialized Field Types** - Pre-built field configs for common patterns (badges, currency, dates, users)
- **Automatic Display Methods** - Auto-generated display methods with widgets
- **HTML Builder Utilities** - `self.html` methods for custom displays
- **Computed Field Decorators** - `@computed_field` for type-safe custom logic
- **Modern UI** - Seamless Unfold integration with Material Design icons
- **Query Optimization** - Built-in select_related/prefetch_related support
- **Zero Boilerplate** - Minimal code, maximum functionality

## Philosophy

### Before: Traditional Django Admin

```python
from django.contrib import admin

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']

    # Lots of manual configuration...
```

### After: Django-CFG Declarative Admin

```python
from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, CurrencyField, DateTimeField, UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

# ✅ Clean, declarative configuration
payment_config = AdminConfig(
    model=Payment,
    select_related=["user"],  # Auto-applied to all queries

    list_display=["internal_payment_id", "user", "amount_usd", "status", "created_at"],

    # Auto-generates display methods with widgets
    display_fields=[
        BadgeField(
            name="internal_payment_id",
            variant="info",
            icon=Icons.RECEIPT
        ),
        UserField(name="user", header=True),  # User with avatar
        CurrencyField(name="amount_usd", currency="USD", precision=2),
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

    list_filter=["status", "created_at"],
    search_fields=["internal_payment_id", "user__username"],
)

@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """Type-safe, auto-configured admin with zero boilerplate."""
    config = payment_config
```

## Key Features

### 1. Type-Safe Configuration

All configuration is validated at runtime using Pydantic 2.x:

```python
config = AdminConfig(
    model=MyModel,
    list_display=["name", "status"],
    display_fields=[
        BadgeField(
            name="status",
            variant="primary",  # ✅ IDE autocomplete + validation
            icon=Icons.CHECK_CIRCLE  # ✅ 2234+ icons with autocomplete
        )
    ]
)
```

### 2. Specialized Field Types

Pre-built field configurations for common patterns - these **automatically generate display methods**:

```python
display_fields=[
    # User with avatar
    UserField(name="user", header=True),

    # Formatted currency
    CurrencyField(name="price", currency="USD", precision=2),

    # Status badge with conditional colors
    BadgeField(
        name="status",
        label_map={"active": "success", "inactive": "secondary"}
    ),

    # Datetime with relative time
    DateTimeField(name="created_at", ordering="created_at"),
]
```

### 3. HTML Builder Utilities

For custom display methods, use `self.html` utilities:

```python
@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    config = payment_config

    def payment_details_display(self, obj):
        """Custom readonly field using self.html."""
        details = []

        # Badge with icon
        details.append(self.html.badge(
            f"Confirmations: {obj.confirmations_count}",
            variant="info",
            icon=Icons.CHECK_CIRCLE
        ))

        # Inline items with separator
        details.append(self.html.inline([
            self.html.span("Amount:", "font-semibold"),
            self.html.span(f"${obj.amount:.2f}", "")
        ], separator=" "))

        # Icon with text
        details.append(self.html.icon_text(Icons.RECEIPT, obj.internal_payment_id))

        return "<br>".join(details)

    payment_details_display.short_description = "Payment Details"
```

**Available `self.html` Methods:**

```python
self.html.badge(text, variant="primary", icon=None)
    # Colored badge with optional Material icon

self.html.span(text, css_class="")
    # Wrapped text with CSS classes

self.html.inline(items, separator=" | ")
    # Join items horizontally

self.html.icon(icon_name, size="xs")
    # Material icon only

self.html.icon_text(icon_or_text, text, icon_size="xs", color=None)
    # Icon + text combination with optional color

self.html.colored_text(text, color=None)
    # Colored text without icon

self.html.link(url, text, css_class="", target="")
    # Clickable link

self.html.empty(text="—")
    # Empty placeholder
```

### 4. Computed Field Decorator

For custom display logic in list views, use `@computed_field`:

```python
from django_cfg.modules.django_admin import computed_field, Icons

@admin.register(User)
class UserAdmin(PydanticAdmin):
    config = user_config

    @computed_field("Status", ordering="is_active")
    def status_display(self, obj):
        """Enhanced status with icons."""
        if obj.is_superuser:
            return self.html.badge("Superuser", variant="danger", icon=Icons.ADMIN_PANEL_SETTINGS)
        elif obj.is_staff:
            return self.html.badge("Staff", variant="warning", icon=Icons.SETTINGS)
        elif obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.CANCEL)

    @computed_field("Full Name")
    def full_name(self, obj):
        """Full name with badge."""
        name = obj.get_full_name()
        if not name:
            return self.html.badge("No name", variant="secondary", icon=Icons.PERSON)
        return self.html.badge(name, variant="primary", icon=Icons.PERSON)
```

### 5. Annotated Fields

For computed values from database aggregations:

```python
from django.db.models import Count

config = AdminConfig(
    model=User,
    # Define annotations
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

### 6. Material Design Icons

2234+ Material icons with full IDE autocomplete:

```python
from django_cfg.modules.django_admin import Icons

Icons.CHECK_CIRCLE       # ✓
Icons.CANCEL             # ✗
Icons.RECEIPT            # Receipt
Icons.EMAIL              # Email
Icons.PERSON             # Person
Icons.ADMIN_PANEL_SETTINGS  # Admin
Icons.SHOPPING_CART      # Cart
Icons.CURRENCY_BITCOIN   # Bitcoin
Icons.BUSINESS           # Business
# ... 2234+ more icons
```

### 7. Query Optimization

Built-in database optimization - applied automatically:

```python
config = AdminConfig(
    model=Order,

    # Auto-applied to all queries
    select_related=["user", "product"],
    prefetch_related=["items"],

    # Aggregate annotations
    annotations={
        'total_items': Count('items'),
        'total_amount': Sum('items__price'),
    },
)
```

## Architecture

```
┌─────────────────────────────────────────┐
│         PydanticAdmin                    │
│  (Base class with config processing)    │
└────────────────┬────────────────────────┘
                 │
                 ├──> AdminConfig (Pydantic model)
                 │    ├── list_display
                 │    ├── display_fields []
                 │    ├── fieldsets []
                 │    ├── actions []
                 │    └── optimizations
                 │
                 ├──> Field Configs
                 │    ├── BadgeField → auto-generates display method
                 │    ├── CurrencyField → auto-generates display method
                 │    ├── DateTimeField → auto-generates display method
                 │    └── UserField → auto-generates display method
                 │
                 ├──> Custom Display Methods
                 │    ├── @computed_field → for list display
                 │    ├── @annotated_field → for aggregations
                 │    └── self.html → for readonly fields
                 │
                 └──> Widget Registry
                      ├── badge → render_badge()
                      ├── currency → render_currency()
                      └── datetime → render_datetime()
```

## Integration with Unfold

The admin module is designed to work seamlessly with Django Unfold:

```python
from django_cfg.modules.django_admin.base import PydanticAdmin

# PydanticAdmin inherits from:
# UnfoldImportExportModelAdmin
#   └─ ImportExportModelAdmin  # Import/Export functionality
#   └─ UnfoldModelAdmin        # Modern Unfold UI
#        └─ Django ModelAdmin
```

:::tip[Always Unfold-Ready]
Every admin class using `PydanticAdmin` automatically gets:
- ✅ Modern Unfold UI
- ✅ Material Design icons
- ✅ Import/Export support (optional)
- ✅ Responsive layout
:::

## Benefits

### For Developers

1. **Less Code** - 60-80% reduction in admin boilerplate
2. **Type Safety** - Catch errors at configuration time, not runtime
3. **Consistency** - Standardized patterns across all admins
4. **Maintainability** - Declarative configs are easier to read and modify
5. **IDE Support** - Full autocomplete for all config options
6. **Rich Utilities** - `self.html` builder and Display utilities for complex formatting

### For Teams

1. **Faster Onboarding** - New developers understand declarative configs faster
2. **Code Reviews** - Less code to review, more focus on logic
3. **Standards** - Built-in best practices and patterns
4. **Documentation** - Self-documenting configuration

### For Projects

1. **Performance** - Built-in query optimization
2. **UI/UX** - Consistent, modern interface
3. **Extensibility** - Easy to add custom fields and actions
4. **Future-Proof** - Type-safe configurations evolve with your schema

## Complete Example

```python
from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, CurrencyField, DateTimeField,
    FieldsetConfig, Icons, UserField, computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

# Declarative config
payment_config = AdminConfig(
    model=Payment,

    # Performance
    select_related=["user", "currency"],

    # List display
    list_display=["internal_payment_id", "user", "amount_usd", "status", "created_at"],

    # Auto-generated display methods
    display_fields=[
        BadgeField(name="internal_payment_id", variant="info", icon=Icons.RECEIPT),
        UserField(name="user", header=True),
        CurrencyField(name="amount_usd", currency="USD", precision=2),
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
        FieldsetConfig(title="Basic", fields=["id", "internal_payment_id", "user"]),
        FieldsetConfig(title="Payment", fields=["amount_usd", "currency", "status"]),
        FieldsetConfig(title="Details", fields=["payment_details_display"], collapsed=True),
    ],

    readonly_fields=["payment_details_display"],
    list_filter=["status", "created_at"],
    search_fields=["internal_payment_id", "user__username"],
)

@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    config = payment_config

    # Custom readonly field using self.html
    def payment_details_display(self, obj):
        """Detailed payment info using self.html utilities."""
        details = []

        details.append(self.html.inline([
            self.html.span("Internal ID:", "font-semibold"),
            self.html.span(obj.internal_payment_id, "")
        ], separator=" "))

        if obj.transaction_hash:
            details.append(self.html.inline([
                self.html.span("Transaction:", "font-semibold"),
                self.html.link(obj.get_explorer_link(), obj.transaction_hash[:16] + "...", target="_blank")
            ], separator=" "))

        if obj.confirmations_count > 0:
            details.append(self.html.badge(
                f"{obj.confirmations_count} confirmations",
                variant="info",
                icon=Icons.CHECK_CIRCLE
            ))

        return "<br>".join(details)

    payment_details_display.short_description = "Payment Details"
```

## Next Steps

- **[Quick Start](./quick-start.md)** - Get started in 5 minutes
- **[Field Types](./field-types.md)** - Complete field reference
- **[Configuration](./configuration.md)** - AdminConfig options, decorators, utilities
- **[Filters](./filters.md)** - Complete guide to filters and third-party integrations
- **[Examples](./examples.md)** - Real-world examples

:::info[Key Concepts]
- **Declarative fields** (BadgeField, CurrencyField, etc.) auto-generate display methods
- **@computed_field** decorator for custom list display logic
- **self.html** utilities for custom readonly fields
- **Display utilities** (UserDisplay, MoneyDisplay, DateTimeDisplay) for advanced formatting
:::
