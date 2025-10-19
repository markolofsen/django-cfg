---
title: Django Admin Quick Start
description: Get started with Django-CFG declarative admin in 5 minutes. Simple examples to configure your first Pydantic-based admin interface.
sidebar_label: Quick Start
sidebar_position: 2
keywords:
  - django admin quick start
  - pydantic admin tutorial
  - django-cfg admin setup
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Quick Start

Get your first declarative admin up and running in 5 minutes.

## Installation

Django Admin module is included with Django-CFG by default. No additional installation required.

:::tip[Already Installed]
If you have `django-cfg` installed, the admin module is ready to use!
:::

## Basic Setup

### Step 1: Import Components

```python
from django.contrib import admin
from django_cfg.modules.django_admin import AdminConfig
from django_cfg.modules.django_admin.base import PydanticAdmin
```

:::warning[Import Path]
**Always import `PydanticAdmin` from `.base`:**
```python
# ✅ Correct
from django_cfg.modules.django_admin.base import PydanticAdmin

# ❌ Wrong
from django_cfg.modules.django_admin import PydanticAdmin  # Won't work!
```
:::

### Step 2: Create Your First Admin

Let's say you have a simple `Product` model:

```python
# models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

Create a declarative admin:

```python
# admin.py
from django.contrib import admin
from django_cfg.modules.django_admin import AdminConfig
from django_cfg.modules.django_admin.base import PydanticAdmin
from .models import Product

# Define configuration
config = AdminConfig(
    model=Product,
    list_display=["name", "price", "stock", "is_active", "created_at"],
    list_filter=["is_active", "created_at"],
    search_fields=["name"],
)

# Register admin
@admin.register(Product)
class ProductAdmin(PydanticAdmin):
    config = config
```

That's it! You now have a fully functional admin interface.

## Adding Display Fields

Let's enhance the display with specialized field types:

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Product,

    list_display=["name", "price", "stock", "is_active", "created_at"],

    # Add specialized display fields
    display_fields=[
        CurrencyField(
            name="price",
            title="Price",
            currency="USD",
            precision=2,
        ),
        BooleanField(
            name="is_active",
            title="Status",
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            show_relative=True,
        ),
    ],

    list_filter=["is_active", "created_at"],
    search_fields=["name"],
)

@admin.register(Product)
class ProductAdmin(PydanticAdmin):
    config = config
```

:::info[What Changed?]
- **CurrencyField** - Formats `price` as `$1,234.56`
- **BooleanField** - Shows `is_active` with ✓/✗ icons
- **DateTimeField** - Displays `created_at` as "2 hours ago"
:::

## Adding Icons and Badges

Make your admin more visual with badges and icons:

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Product,

    list_display=["name", "price", "status", "stock_level"],

    display_fields=[
        BadgeField(
            name="status",
            title="Status",
            variant="primary",
            icon=Icons.INVENTORY,
        ),
        BadgeField(
            name="stock_level",
            title="Stock",
            label_map={
                "in_stock": "success",
                "low_stock": "warning",
                "out_of_stock": "danger",
            },
            icon=Icons.PACKAGE,
        ),
    ],
)

@admin.register(Product)
class ProductAdmin(PydanticAdmin):
    config = config
```

## Organizing with Fieldsets

Group related fields using fieldsets:

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    FieldsetConfig,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Product,

    list_display=["name", "price", "is_active"],

    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "description"],
        ),
        FieldsetConfig(
            title="Pricing & Inventory",
            fields=["price", "stock", "sku"],
        ),
        FieldsetConfig(
            title="Status",
            fields=["is_active", "created_at", "updated_at"],
            collapsed=True,  # Start collapsed
        ),
    ],

    readonly_fields=["created_at", "updated_at"],
)

@admin.register(Product)
class ProductAdmin(PydanticAdmin):
    config = config
```

## Query Optimization

Optimize database queries with built-in support:

```python
config = AdminConfig(
    model=Order,

    # Optimize queries
    select_related=["user", "product"],
    prefetch_related=["items"],

    list_display=["id", "user", "product", "total"],
)
```

:::tip[Automatic Optimization]
The admin automatically applies `select_related` and `prefetch_related` to all queries. No need to override `get_queryset()`!
:::

## Common Patterns

### User Admin

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    DateTimeField,
    Icons,
    UserField,
)

config = AdminConfig(
    model=User,

    list_display=["username", "email", "is_active", "date_joined"],

    display_fields=[
        UserField(
            name="username",
            title="User",
            header=True,  # Show with avatar
        ),
        BooleanField(name="is_active", title="Active"),
        BooleanField(name="is_staff", title="Staff"),
        DateTimeField(name="date_joined", title="Joined"),
    ],

    list_filter=["is_active", "is_staff", "date_joined"],
    search_fields=["username", "email", "first_name", "last_name"],
)
```

### E-commerce Order

```python
config = AdminConfig(
    model=Order,

    select_related=["user", "shipping_address"],
    prefetch_related=["items"],

    list_display=["order_number", "user", "total", "status", "created_at"],

    display_fields=[
        UserField(name="user", header=True),
        CurrencyField(name="total", currency="USD", precision=2),
        BadgeField(
            name="status",
            label_map={
                "pending": "warning",
                "processing": "info",
                "shipped": "primary",
                "delivered": "success",
                "cancelled": "danger",
            },
            icon=Icons.SHOPPING_CART,
        ),
        DateTimeField(name="created_at", show_relative=True),
    ],

    list_filter=["status", "created_at"],
    search_fields=["order_number", "user__email"],
)
```

### Blog Post

```python
config = AdminConfig(
    model=Post,

    select_related=["author", "category"],

    list_display=["title", "author", "category", "status", "published_at"],

    display_fields=[
        BadgeField(
            name="status",
            label_map={"draft": "secondary", "published": "success"},
            icon=Icons.ARTICLE,
        ),
        BadgeField(
            name="category",
            variant="info",
            icon=Icons.CATEGORY,
        ),
        DateTimeField(name="published_at", show_relative=True),
    ],

    fieldsets=[
        FieldsetConfig(title="Content", fields=["title", "slug", "content"]),
        FieldsetConfig(title="Meta", fields=["author", "category", "tags"]),
        FieldsetConfig(title="Publishing", fields=["status", "published_at"]),
    ],

    list_filter=["status", "category", "published_at"],
    search_fields=["title", "content"],
    prepopulated_fields={"slug": ("title",)},
)
```

## Next Steps

<div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">

### 📚 Learn More

- [Field Types Reference](./field-types.md) - All available field types
- [Configuration Guide](./configuration.md) - AdminConfig options
- [Filters Guide](./filters.md) - Simple and custom filters
- [Examples](./examples.md) - Real-world examples

### 🚀 Advanced Features

- Custom actions and bulk operations
- Import/Export integration
- [Advanced filtering](./filters.md) - Custom filters and third-party integrations
- Custom widgets and renderers

</div>

:::tip[Pro Tip]
Start simple with basic `AdminConfig`, then gradually add display fields, fieldsets, and optimizations as needed. The declarative approach makes it easy to iterate!
:::
