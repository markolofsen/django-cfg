---
title: Field Types Reference
description: Complete reference for all Django Admin field types including BadgeField, CurrencyField, DateTimeField, ShortUUIDField, UserField, and more.
sidebar_label: Field Types
sidebar_position: 3
keywords:
  - django admin field types
  - BadgeField
  - CurrencyField
  - DateTimeField
  - ImageField
  - ShortUUIDField
  - UserField
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Field Types Reference

Complete reference for all specialized field configuration types in Django Admin.

## Overview

Django Admin provides specialized field types that automatically handle formatting, display, and rendering:

| Field Type | Purpose | Common Use Cases |
|------------|---------|------------------|
| **BadgeField** | Colored badges with icons | Status, categories, tags |
| **BooleanField** | Boolean indicators | Active/inactive, published/draft |
| **CurrencyField** | Formatted currency | Prices, totals, balances |
| **DateTimeField** | Formatted dates/times | Created, updated, published |
| **ImageField** | Images with captions | QR codes, photos, avatars |
| **ShortUUIDField** | Shortened UUIDs with tooltip | Primary keys, unique identifiers |
| **TextField** | Text with truncation | Descriptions, content |
| **UserField** | User display with avatar | Authors, assignees, owners |

## BadgeField

Display values as colored badges with optional icons.

### Parameters

```python
class BadgeField(FieldConfig):
    name: str                                    # Field name
    title: str | None = None                     # Display title
    variant: Literal[                            # Badge color
        "primary", "secondary", "success",
        "danger", "warning", "info"
    ] = "primary"
    icon: str | None = None                      # Material icon name
    label_map: dict[str, str] | None = None      # Value → variant mapping
    empty_value: str = "—"                       # Value when None
    ordering: str | None = None                  # Sort field
```

### Basic Usage

```python
from django_cfg.modules.django_admin import BadgeField, Icons

# Simple badge
BadgeField(
    name="status",
    title="Status",
    variant="primary",
)

# Badge with icon
BadgeField(
    name="category",
    title="Category",
    variant="info",
    icon=Icons.CATEGORY,
)

# Badge with conditional colors
BadgeField(
    name="status",
    title="Status",
    label_map={
        "pending": "warning",
        "approved": "success",
        "rejected": "danger",
    },
    icon=Icons.CHECK_CIRCLE,
)
```

### Examples

<Tabs>
  <TabItem value="status" label="Status Badge" default>

```python
display_fields=[
    BadgeField(
        name="status",
        title="Status",
        label_map={
            "draft": "secondary",
            "pending": "warning",
            "published": "success",
            "archived": "info",
        },
        icon=Icons.ARTICLE,
    ),
]
```

  </TabItem>
  <TabItem value="priority" label="Priority Badge">

```python
display_fields=[
    BadgeField(
        name="priority",
        title="Priority",
        label_map={
            "low": "info",
            "medium": "warning",
            "high": "danger",
            "critical": "danger",
        },
        icon=Icons.PRIORITY_HIGH,
    ),
]
```

  </TabItem>
  <TabItem value="category" label="Category Badge">

```python
display_fields=[
    BadgeField(
        name="category",
        title="Category",
        variant="primary",
        icon=Icons.CATEGORY,
    ),
]
```

  </TabItem>
</Tabs>

:::tip[When to Use label_map]
Use `label_map` when you need different colors for different values. The map translates field values to badge variants.
:::

## BooleanField

Display boolean values with checkmark/cross icons.

### Parameters

```python
class BooleanField(FieldConfig):
    name: str                          # Field name
    title: str | None = None           # Display title
    empty_value: str = "—"             # Value when None
    ordering: str | None = None        # Sort field
```

### Basic Usage

```python
from django_cfg.modules.django_admin import BooleanField

# Simple boolean
BooleanField(
    name="is_active",
    title="Active",
)

# With ordering
BooleanField(
    name="is_published",
    title="Published",
    ordering="is_published",
)
```

### Examples

```python
display_fields=[
    BooleanField(name="is_active", title="Active"),
    BooleanField(name="is_verified", title="Verified"),
    BooleanField(name="email_confirmed", title="Email Confirmed"),
]
```

:::info[Automatic Rendering]
BooleanField automatically renders as:
- ✅ Green checkmark for `True`
- ❌ Red cross for `False`
- "—" for `None`
:::

## CurrencyField

Format numbers as currency with symbols and precision.

### Parameters

```python
class CurrencyField(FieldConfig):
    name: str                          # Field name
    title: str | None = None           # Display title
    currency: str = "USD"              # Currency code (USD, EUR, etc.)
    precision: int = 2                 # Decimal places
    empty_value: str = "—"             # Value when None
    ordering: str | None = None        # Sort field
```

### Basic Usage

```python
from django_cfg.modules.django_admin import CurrencyField

# USD with 2 decimals
CurrencyField(
    name="price",
    title="Price",
    currency="USD",
    precision=2,
)

# EUR with 2 decimals
CurrencyField(
    name="total",
    title="Total",
    currency="EUR",
    precision=2,
)

# No decimals for large amounts
CurrencyField(
    name="market_cap",
    title="Market Cap",
    currency="USD",
    precision=0,
)
```

### Examples

<Tabs>
  <TabItem value="basic" label="Basic Prices" default>

```python
display_fields=[
    CurrencyField(
        name="price",
        title="Price",
        currency="USD",
        precision=2,
    ),
    CurrencyField(
        name="discount",
        title="Discount",
        currency="USD",
        precision=2,
    ),
    CurrencyField(
        name="total",
        title="Total",
        currency="USD",
        precision=2,
        ordering="total",
    ),
]
```

**Renders as:** `$1,234.56`

  </TabItem>
  <TabItem value="multi-currency" label="Multi-Currency">

```python
display_fields=[
    CurrencyField(name="price_usd", title="USD", currency="USD", precision=2),
    CurrencyField(name="price_eur", title="EUR", currency="EUR", precision=2),
    CurrencyField(name="price_gbp", title="GBP", currency="GBP", precision=2),
]
```

  </TabItem>
  <TabItem value="crypto" label="Crypto Prices">

```python
display_fields=[
    CurrencyField(
        name="current_price_usd",
        title="Price",
        currency="USD",
        precision=2,
    ),
    CurrencyField(
        name="market_cap_usd",
        title="Market Cap",
        currency="USD",
        precision=0,  # No decimals for large numbers
    ),
]
```

**Renders as:** `$1,234` (no decimals)

  </TabItem>
</Tabs>

## DateTimeField

Format datetime values with optional relative time display.

### Parameters

```python
class DateTimeField(FieldConfig):
    name: str                          # Field name
    title: str | None = None           # Display title
    format: str = "%Y-%m-%d %H:%M"     # DateTime format string
    show_relative: bool = False        # Show "2 hours ago"
    empty_value: str = "—"             # Value when None
    ordering: str | None = None        # Sort field
```

### Basic Usage

```python
from django_cfg.modules.django_admin import DateTimeField

# Standard format
DateTimeField(
    name="created_at",
    title="Created",
)

# Relative time
DateTimeField(
    name="last_login",
    title="Last Login",
    show_relative=True,
)

# Custom format
DateTimeField(
    name="published_at",
    title="Published",
    format="%B %d, %Y",  # "January 15, 2024"
)
```

### Examples

<Tabs>
  <TabItem value="standard" label="Standard Format" default>

```python
display_fields=[
    DateTimeField(
        name="created_at",
        title="Created",
        ordering="created_at",
    ),
    DateTimeField(
        name="updated_at",
        title="Updated",
        ordering="updated_at",
    ),
]
```

**Renders as:** `2024-01-15 14:30`

  </TabItem>
  <TabItem value="relative" label="Relative Time">

```python
display_fields=[
    DateTimeField(
        name="last_login",
        title="Last Login",
        show_relative=True,
    ),
    DateTimeField(
        name="created_at",
        title="Created",
        show_relative=True,
    ),
]
```

**Renders as:** `2 hours ago`, `3 days ago`

  </TabItem>
  <TabItem value="custom" label="Custom Format">

```python
display_fields=[
    DateTimeField(
        name="published_at",
        title="Published",
        format="%B %d, %Y at %I:%M %p",
    ),
]
```

**Renders as:** `January 15, 2024 at 02:30 PM`

  </TabItem>
</Tabs>

## TextField

Display text with optional truncation and tooltips.

### Parameters

```python
class TextField(FieldConfig):
    name: str                          # Field name
    title: str | None = None           # Display title
    max_length: int | None = None      # Truncate after N chars
    show_tooltip: bool = False         # Show full text on hover
    empty_value: str = "—"             # Value when None
    ordering: str | None = None        # Sort field
```

### Basic Usage

```python
from django_cfg.modules.django_admin import TextField

# Simple text
TextField(
    name="description",
    title="Description",
)

# Truncated with tooltip
TextField(
    name="content",
    title="Content",
    max_length=100,
    show_tooltip=True,
)
```

### Examples

```python
display_fields=[
    TextField(
        name="description",
        title="Description",
        max_length=50,
        show_tooltip=True,
    ),
    TextField(
        name="notes",
        title="Notes",
        max_length=100,
    ),
]
```

:::tip[When to Truncate]
Use `max_length` for long text fields to keep list views clean. Enable `show_tooltip` to let users see the full text on hover.
:::

## UserField

Display user information with avatar and optional header styling.

### Parameters

```python
class UserField(FieldConfig):
    name: str                          # Field name (must be ForeignKey to User)
    title: str | None = None           # Display title
    header: bool = False               # Show with avatar
    empty_value: str = "—"             # Value when None
    ordering: str | None = None        # Sort field (e.g., "user__username")
```

### Basic Usage

```python
from django_cfg.modules.django_admin import UserField

# Simple user display
UserField(
    name="author",
    title="Author",
    ordering="author__username",
)

# User with avatar header
UserField(
    name="owner",
    title="Owner",
    header=True,
    ordering="owner__username",
)
```

### Examples

<Tabs>
  <TabItem value="basic" label="Basic User" default>

```python
display_fields=[
    UserField(
        name="author",
        title="Author",
        ordering="author__username",
    ),
]
```

**Renders as:** Username only

  </TabItem>
  <TabItem value="header" label="User with Avatar">

```python
display_fields=[
    UserField(
        name="owner",
        title="Owner",
        header=True,
        ordering="owner__username",
    ),
]
```

**Renders as:** Avatar + Username in header style

  </TabItem>
  <TabItem value="multiple" label="Multiple Users">

```python
display_fields=[
    UserField(name="created_by", title="Created By", header=True),
    UserField(name="assigned_to", title="Assigned To"),
    UserField(name="approved_by", title="Approved By"),
]
```

  </TabItem>
</Tabs>

:::warning[Requires User Relation]
UserField only works with ForeignKey fields pointing to the User model. Ensure `select_related` includes the user field for optimal performance.
:::

## Combining Field Types

Mix different field types for rich admin displays:

```python
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    Icons,
    ShortUUIDField,
    UserField,
)

config = AdminConfig(
    model=Order,
    select_related=["user", "product"],

    list_display=["order_number", "user", "product", "total", "status", "is_paid", "created_at"],

    display_fields=[
        UserField(
            name="user",
            title="Customer",
            header=True,
            ordering="user__username",
        ),
        CurrencyField(
            name="total",
            title="Total",
            currency="USD",
            precision=2,
            ordering="total",
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "processing": "info",
                "shipped": "primary",
                "delivered": "success",
                "cancelled": "danger",
            },
            icon=Icons.SHOPPING_CART,
        ),
        BooleanField(
            name="is_paid",
            title="Paid",
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            show_relative=True,
            ordering="created_at",
        ),
    ],
)
```

## Material Icons Reference

All field types support Material Design icons via the `Icons` class:

```python
from django_cfg.modules.django_admin import Icons

# Common icons
Icons.CHECK_CIRCLE      # ✓
Icons.CANCEL            # ✗
Icons.ARTICLE           # 📄
Icons.CATEGORY          # 🏷️
Icons.SHOPPING_CART     # 🛒
Icons.CURRENCY_BITCOIN  # ₿
Icons.ACCOUNT_CIRCLE    # 👤
Icons.BUSINESS          # 🏢
Icons.PRIORITY_HIGH     # ⚠️
Icons.PACKAGE           # 📦
```

:::tip[IDE Autocomplete]
The `Icons` class provides autocomplete for 2234+ Material icons. Just type `Icons.` and let your IDE suggest available icons!
:::

## ImageField

Display images from URLs with optional captions and styling.

### Parameters

```python
class ImageField(FieldConfig):
    name: str                              # Field name (or method name)
    title: str | None = None               # Display title
    width: str | None = None               # Image width (e.g., "200px")
    height: str | None = None              # Image height (e.g., "200px")
    max_width: str = "200px"               # Maximum width
    max_height: str | None = None          # Maximum height
    border_radius: str | None = None       # Border radius (e.g., "50%", "8px")
    caption: str | None = None             # Static caption text
    caption_field: str | None = None       # Model field to use as caption
    caption_template: str | None = None    # Template with {field_name} placeholders
    alt_text: str = "Image"                # Alt text for image
    empty_value: str = "—"                 # Value when None
```

### Basic Usage

```python
from django_cfg.modules.django_admin import ImageField

# Simple image
ImageField(
    name="photo_url",
    title="Photo",
    max_width="200px",
)

# Image with static caption
ImageField(
    name="thumbnail",
    title="Thumbnail",
    max_width="100px",
    caption="Product Image",
)

# Image with caption from field
ImageField(
    name="avatar_url",
    title="Avatar",
    width="50px",
    height="50px",
    border_radius="50%",
    caption_field="username",
)
```

### Examples

<Tabs>
  <TabItem value="qr" label="QR Code" default>

```python
# QR code with template caption
display_fields=[
    ImageField(
        name="get_qr_code_url",  # Can be a method
        title="QR Code",
        max_width="200px",
        caption_template="Scan to pay: <code>{pay_address}</code>",
    ),
]
```

**Result:**
```html
<img src="https://api.qrserver.com/..." alt="Image" style="max-width: 200px;">
<br><small>Scan to pay: <code>0x1234...5678</code></small>
```

  </TabItem>
  <TabItem value="avatar" label="Circular Avatar">

```python
# Circular avatar with username
display_fields=[
    ImageField(
        name="profile_picture",
        title="Avatar",
        width="50px",
        height="50px",
        border_radius="50%",
        caption_field="full_name",
    ),
]
```

**Result:**
```html
<img src="/media/avatars/john.jpg" alt="Image"
     style="width: 50px; height: 50px; border-radius: 50%;">
<br><small>John Doe</small>
```

  </TabItem>
  <TabItem value="product" label="Product Photo">

```python
# Product photo with multiple fields in caption
display_fields=[
    ImageField(
        name="image_url",
        title="Product",
        max_width="150px",
        max_height="150px",
        caption_template="{name} - ${price}",
    ),
]
```

**Result:**
```html
<img src="/media/products/laptop.jpg" alt="Image"
     style="max-width: 150px; max-height: 150px;">
<br><small>Laptop Pro - $1299</small>
```

  </TabItem>
</Tabs>

### Method Support

ImageField supports both model fields and methods:

```python
class Payment(models.Model):
    pay_address = models.CharField(max_length=100)

    def get_qr_code_url(self, size=200):
        """Generate QR code URL dynamically."""
        from urllib.parse import quote
        data = quote(self.pay_address)
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={data}"

# Use method in ImageField
ImageField(
    name="get_qr_code_url",  # Method will be called automatically
    title="Payment QR",
    max_width="200px",
    caption_template="Address: <code>{pay_address}</code>",
)
```

### Caption Templates

Use `{field_name}` placeholders in `caption_template`:

```python
# Single field
caption_template="Scan: {address}"

# Multiple fields
caption_template="User: {username} | ID: {user_id}"

# With HTML
caption_template="Pay to: <code>{wallet_address}</code>"
```

### Styling

Control image appearance with CSS properties:

```python
# Fixed size
ImageField(width="100px", height="100px")

# Maximum constraints
ImageField(max_width="300px", max_height="200px")

# Circular/rounded
ImageField(border_radius="50%")    # Circle
ImageField(border_radius="8px")    # Rounded corners

# Combined
ImageField(
    width="80px",
    height="80px",
    border_radius="50%",
    max_width="100px",
)
```

## ShortUUIDField

Display shortened UUIDs with hover tooltip showing full value.

### Parameters

```python
class ShortUUIDField(FieldConfig):
    name: str                          # Field name
    title: str | None = None           # Display title
    length: int = 8                    # Number of characters to display
    copy_on_click: bool = True         # Enable click-to-copy
    show_full_on_hover: bool = True    # Show full UUID in tooltip
    empty_value: str = "—"             # Value when None
    ordering: str | None = None        # Sort field
```

### Basic Usage

```python
from django_cfg.modules.django_admin import ShortUUIDField

# Simple shortened UUID
ShortUUIDField(
    name="id",
    title="ID",
    length=8,
)

# Longer display
ShortUUIDField(
    name="uuid",
    title="UUID",
    length=12,
)

# With ordering
ShortUUIDField(
    name="id",
    title="ID",
    length=8,
    ordering="id",
)
```

### Examples

<Tabs>
  <TabItem value="basic" label="Basic UUID" default>

```python
display_fields=[
    ShortUUIDField(
        name="id",
        title="ID",
        length=8,
    ),
]
```

**Renders as:** `a1b2c3d4` (with full UUID on hover)

  </TabItem>
  <TabItem value="custom-length" label="Custom Length">

```python
display_fields=[
    ShortUUIDField(
        name="transaction_id",
        title="Transaction",
        length=12,
        ordering="transaction_id",
    ),
]
```

**Renders as:** `a1b2c3d4e5f6`

  </TabItem>
  <TabItem value="multiple" label="Multiple IDs">

```python
display_fields=[
    ShortUUIDField(name="id", title="ID", length=8),
    ShortUUIDField(name="parent_id", title="Parent", length=8),
    ShortUUIDField(name="reference_id", title="Reference", length=10),
]
```

  </TabItem>
</Tabs>

:::tip[Perfect for List Views]
ShortUUIDField is ideal for admin list views where you need to display UUIDs without taking up too much space. Users can hover to see the full UUID or click to copy it.
:::

:::info[Automatic Formatting]
ShortUUIDField automatically:
- Removes dashes for cleaner display
- Shows tooltip with full UUID on hover
- Enables click-to-copy functionality
- Styles as inline code block
:::

## Best Practices

### 1. Choose the Right Field Type

| Data Type | Recommended Field |
|-----------|------------------|
| Status/Category | BadgeField |
| Boolean | BooleanField |
| Money/Prices | CurrencyField |
| Dates/Times | DateTimeField |
| Images/Photos/QR | ImageField |
| UUIDs/IDs | ShortUUIDField |
| Long Text | TextField |
| User Relations | UserField |

### 2. Always Set Titles

```python
# ✅ Good - Clear titles
BadgeField(name="order_status", title="Status")
CurrencyField(name="total_amount", title="Total")

# ❌ Bad - Missing titles (falls back to field name)
BadgeField(name="order_status")
```

### 3. Use Ordering for Sortable Fields

```python
# ✅ Good - Sortable
CurrencyField(name="price", title="Price", ordering="price")
UserField(name="author", title="Author", ordering="author__username")

# ⚠️ OK - Not sortable
BadgeField(name="status", title="Status")  # Badges often don't need sorting
```

### 4. Optimize User Fields

```python
# ✅ Good - select_related for performance
config = AdminConfig(
    model=Order,
    select_related=["user"],  # Important!
    display_fields=[
        UserField(name="user", header=True),
    ],
)
```

### 5. Use label_map for Dynamic Badge Colors

```python
# ✅ Good - Different colors for different states
BadgeField(
    name="status",
    label_map={"active": "success", "inactive": "secondary", "error": "danger"}
)

# ⚠️ OK - Single color for all values
BadgeField(name="status", variant="primary")
```

## Next Steps

- **[Configuration Guide](./configuration.md)** - AdminConfig options
- **[Filters](./filters.md)** - Complete guide to filters
- **[Examples](./examples.md)** - Real-world examples
- **[Overview](./overview.md)** - Learn the philosophy
