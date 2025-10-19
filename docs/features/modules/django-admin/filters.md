---
title: Filters Guide
description: Complete guide to using filters in Django Admin module - simple filters, custom filters, and third-party integrations.
sidebar_label: Filters
sidebar_position: 5
keywords:
  - django admin filters
  - list_filter
  - custom filters
  - range filters
  - unfold filters
---

# Filters Guide

Complete guide to configuring and using filters in Django Admin v2.0.

## Overview

Django Admin uses the `list_filter` field in `AdminConfig` to define filters for the changelist view. Due to Pydantic's type validation, there are specific requirements for filter configuration.

## Type Definition

```python
class AdminConfig(BaseModel):
    list_filter: List[Union[str, Type, Tuple[str, Type]]] = []
```

**Accepted values:**
- ✅ `str` - Field name for simple filters
- ✅ `Type` - Custom filter class
- ✅ `Tuple[str, Type]` - Field name + filter class (for third-party filters like RangeFilter)

## Simple Filters

Use field names as strings for basic filtering:

```python
from django_cfg.modules.django_admin import AdminConfig

config = AdminConfig(
    model=Payment,

    # Simple field filters
    list_filter=["status", "created_at", "is_active"],

    # Foreign key filters (shows related objects)
    list_filter=["user", "currency", "created_at"],

    # Choice field filters (shows available choices)
    list_filter=["status", "payment_method"],
)
```

### Auto-detected Filter Types

Django automatically selects the appropriate filter type based on the field:

| Field Type | Filter Type | Example |
|------------|-------------|---------|
| `BooleanField` | Boolean filter (Yes/No/All) | `is_active` |
| `CharField` with choices | Choice filter | `status` |
| `ForeignKey` | Related object filter | `user` |
| `DateField`/`DateTimeField` | Date hierarchy filter | `created_at` |
| `IntegerField` | Exact match | `amount` |

## Custom Filter Classes

Define custom filter classes for advanced filtering logic:

### Basic Custom Filter

```python
from django.contrib import admin
from django_cfg.modules.django_admin import AdminConfig

class StatusFilter(admin.SimpleListFilter):
    title = 'payment status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(status='pending')
        elif self.value() == 'completed':
            return queryset.filter(status='completed')
        elif self.value() == 'failed':
            return queryset.filter(status='failed')
        return queryset

config = AdminConfig(
    model=Payment,
    list_filter=[StatusFilter, "created_at"],  # ✅ Class, then string
)
```

### Filter with Dynamic Choices

```python
class UserWorkspaceFilter(admin.SimpleListFilter):
    title = 'workspace'
    parameter_name = 'workspace'

    def lookups(self, request, model_admin):
        # Get unique workspaces from database
        workspaces = Workspace.objects.filter(
            owner=request.user
        ).values_list('id', 'name')
        return workspaces

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(workspace_id=self.value())
        return queryset

config = AdminConfig(
    model=Session,
    list_filter=[UserWorkspaceFilter, "status", "created_at"],
)
```

## Date Hierarchy

For date-based filtering with drill-down navigation:

```python
config = AdminConfig(
    model=Payment,

    # Adds year/month/day drill-down navigation at the top
    date_hierarchy="created_at",

    # Can still include in list_filter for sidebar
    list_filter=["status", "created_at"],
)
```

## Third-Party Filter Libraries

### django-admin-rangefilter

**✅ Tuple syntax is now fully supported!**

```python
from rangefilter.filters import DateRangeFilter, NumericRangeFilter

config = AdminConfig(
    model=Payment,
    list_filter=[
        ("created_at", DateRangeFilter),  # ✅ Works!
        ("amount", NumericRangeFilter),   # ✅ Works!
        "status",
    ]
)
```

### Unfold Admin Filters (Recommended)

Unfold provides modern range filters with better UX. **Use tuples to specify the field:**

```python
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeDateTimeFilter,
    SingleNumericFilter,
    RangeNumericFilter,
)

config = AdminConfig(
    model=Payment,
    list_filter=[
        ("created_at", RangeDateFilter),      # ✅ Date range with calendar
        ("amount", RangeNumericFilter),       # ✅ Numeric range with inputs
        "status",
    ]
)
```

## Multiple Related Object Filters

For filtering by multiple related objects:

```python
class HasRelatedFilter(admin.SimpleListFilter):
    title = 'has transactions'
    parameter_name = 'has_transactions'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Has transactions'),
            ('no', 'No transactions'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(transactions__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(transactions__isnull=True)
        return queryset

config = AdminConfig(
    model=Payment,
    list_filter=[HasRelatedFilter, "status", "created_at"],
)
```

## Complete Example

```python
from django.contrib import admin
from django.db.models import Q
from rangefilter.filters import DateRangeFilter

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

# Custom status filter with counts
class PaymentStatusFilter(admin.SimpleListFilter):
    title = 'payment status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

# Amount range filter
class AmountRangeFilter(admin.SimpleListFilter):
    title = 'amount range'
    parameter_name = 'amount_range'

    def lookups(self, request, model_admin):
        return [
            ('0-100', '$0 - $100'),
            ('100-500', '$100 - $500'),
            ('500-1000', '$500 - $1000'),
            ('1000+', '$1000+'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-100':
            return queryset.filter(amount_usd__gte=0, amount_usd__lt=100)
        elif self.value() == '100-500':
            return queryset.filter(amount_usd__gte=100, amount_usd__lt=500)
        elif self.value() == '500-1000':
            return queryset.filter(amount_usd__gte=500, amount_usd__lt=1000)
        elif self.value() == '1000+':
            return queryset.filter(amount_usd__gte=1000)
        return queryset

# Configuration
payment_config = AdminConfig(
    model=Payment,

    # List display
    list_display=[
        'internal_payment_id',
        'user',
        'amount_usd',
        'status',
        'created_at'
    ],

    # Display fields
    display_fields=[
        BadgeField(name='internal_payment_id', variant='info', icon=Icons.RECEIPT),
        UserField(name='user', header=True),
        CurrencyField(name='amount_usd', currency='USD', precision=2),
        BadgeField(
            name='status',
            label_map={
                'pending': 'warning',
                'processing': 'info',
                'completed': 'success',
                'failed': 'danger',
            }
        ),
        DateTimeField(name='created_at', ordering='created_at'),
    ],

    # Filters - mix of custom classes, tuples, and simple strings
    list_filter=[
        PaymentStatusFilter,                # Custom filter with choices
        AmountRangeFilter,                   # Custom range filter
        ("created_at", DateRangeFilter),    # ✅ Date range filter (tuple)
        "currency",                          # Simple foreign key filter
        "is_test",                           # Simple boolean filter
    ],

    # Date hierarchy for top navigation
    date_hierarchy="created_at",

    # Search
    search_fields=['internal_payment_id', 'user__email', 'user__username'],

    # Other options
    ordering=['-created_at'],
    list_per_page=50,
)

@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """Payment admin with advanced filtering."""
    config = payment_config

    # Autocomplete
    autocomplete_fields = ['user', 'currency']
```

## Best Practices

### 1. **Order Filters by Importance**

```python
# ✅ Good - most used filters first
list_filter=[
    "status",           # Most common filter
    "created_at",       # Date filter
    "is_active",        # Boolean filter
    "user",             # Less common
]

# ❌ Avoid - random order
list_filter=["user", "is_active", "status", "created_at"]
```

### 2. **Use Custom Filters for Complex Logic**

```python
# ✅ Good - custom filter for complex queries
class RecentPaymentsFilter(admin.SimpleListFilter):
    title = 'recent payments'
    parameter_name = 'recent'

    def lookups(self, request, model_admin):
        return [
            ('24h', 'Last 24 hours'),
            ('7d', 'Last 7 days'),
            ('30d', 'Last 30 days'),
        ]

    def queryset(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        if self.value() == '24h':
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif self.value() == '7d':
            return queryset.filter(created_at__gte=now - timedelta(days=7))
        elif self.value() == '30d':
            return queryset.filter(created_at__gte=now - timedelta(days=30))
        return queryset
```

### 3. **Limit Filters for Large Datasets**

```python
# ❌ Avoid - too many foreign key filters on large datasets
list_filter=["user", "workspace", "project", "task", "category"]

# ✅ Good - use autocomplete or search instead
list_filter=["status", "created_at"]
search_fields=["user__email", "workspace__name"]
```

### 4. **Use Date Hierarchy for Time-based Data**

```python
# ✅ Good - date hierarchy for drill-down
config = AdminConfig(
    model=Payment,
    date_hierarchy="created_at",
    list_filter=["status", "currency"],
)
```

### 5. **Combine with Search**

```python
# ✅ Good - filters for categories, search for specific items
config = AdminConfig(
    model=Payment,
    list_filter=["status", "currency", "created_at"],
    search_fields=["internal_payment_id", "user__email", "transaction_hash"],
)
```

## Troubleshooting

### Filter Not Appearing

**Problem:** Filter specified but not showing in admin

**Solutions:**
1. Check field exists in model
2. Verify field is not in `exclude` list
3. For custom filters, check `lookups()` returns values
4. Check user has permission to see filtered data

### Performance Issues

**Problem:** Filters slow on large datasets

**Solutions:**
1. Add database indexes on filtered fields
2. Use `select_related` for foreign key filters
3. Consider custom filter with optimized queryset
4. Use autocomplete instead of showing all options

```python
# ✅ Optimized configuration
config = AdminConfig(
    model=Payment,

    # Add select_related for foreign key filters
    select_related=["user", "currency"],

    # Use indexed fields for filters
    list_filter=["status", "created_at"],  # Both indexed
)
```

## Next Steps

- **[Configuration](./configuration.md)** - Complete AdminConfig reference
- **[Examples](./examples.md)** - Real-world admin examples
- **[API Reference](./api-reference.md)** - Full API documentation
