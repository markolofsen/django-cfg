---
title: Real-World Examples
description: Complete working examples of Django Admin from production code - Payment, User, E-commerce, and Newsletter admins.
sidebar_label: Examples
sidebar_position: 6
keywords:
  - django admin examples
  - real-world admin
  - payment admin example
  - user admin example
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Real-World Examples

Complete working examples from production code showing best practices and common patterns.

## Payment Admin

Complete payment management with transaction details, QR codes, and status tracking.

```python
"""
Payment Admin - Complete example from production
Features: Badges, Currency, DateTime, Custom readonly fields with self.html
"""

from django.contrib import admin
from django.utils import timezone
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, CurrencyField, DateTimeField,
    FieldsetConfig, Icons, UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

# Declarative configuration
payment_config = AdminConfig(
    model=Payment,

    # Performance optimization
    select_related=["user", "currency"],

    # List display
    list_display=[
        "internal_payment_id",
        "user",
        "amount_usd",
        "currency",
        "status",
        "status_changed_at",
        "created_at"
    ],

    # Auto-generated display methods
    display_fields=[
        BadgeField(
            name="internal_payment_id",
            title="Payment ID",
            variant="info",
            icon=Icons.RECEIPT
        ),
        UserField(
            name="user",
            title="User",
            header=True  # Show with avatar
        ),
        CurrencyField(
            name="amount_usd",
            title="Amount",
            currency="USD",
            precision=2
        ),
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "confirming": "info",
                "confirmed": "primary",
                "completed": "success",
                "partially_paid": "warning",
                "failed": "danger",
                "cancelled": "secondary",
                "expired": "danger"
            }
        ),
        DateTimeField(
            name="status_changed_at",
            title="Status Changed",
            ordering="status_changed_at"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Filters
    list_filter=["status", "currency", "created_at"],
    search_fields=["internal_payment_id", "user__username", "user__email"],

    # Readonly fields (custom methods below)
    readonly_fields=["payment_details_display", "qr_code_display"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["id", "internal_payment_id", "user", "status"]
        ),
        FieldsetConfig(
            title="Payment Details",
            fields=["amount_usd", "currency", "pay_amount", "payment_details_display"]
        ),
        FieldsetConfig(
            title="QR Code",
            fields=["qr_code_display"],
            collapsed=True
        ),
    ],
)

@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """Enhanced payment admin with custom readonly fields."""
    config = payment_config

    def payment_details_display(self, obj):
        """Detailed payment information using self.html utilities."""
        if not obj.pk:
            return "Save to see details"

        details = []

        # Payment age
        age = timezone.now() - obj.created_at
        age_text = f"{age.days} days, {age.seconds // 3600} hours"

        details.append(self.html.inline([
            self.html.span("Age:", "font-semibold"),
            self.html.span(age_text, "")
        ], separator=" "))

        # Transaction hash with explorer link
        if obj.transaction_hash:
            explorer_link = obj.get_explorer_link()
            if explorer_link:
                details.append(self.html.inline([
                    self.html.span("Transaction:", "font-semibold"),
                    self.html.link(explorer_link, obj.transaction_hash[:16] + "...", target="_blank")
                ], separator=" "))

        # Confirmations badge
        if obj.confirmations_count > 0:
            details.append(self.html.badge(
                f"{obj.confirmations_count} confirmations",
                variant="info",
                icon=Icons.CHECK_CIRCLE
            ))

        # Pay address (monospace code)
        if obj.pay_address:
            details.append(self.html.inline([
                self.html.span("Pay Address:", "font-semibold"),
                self.html.span(f'<code>{obj.pay_address}</code>', "")
            ], separator=" "))

        # Expiration status
        if obj.expires_at:
            if obj.is_expired:
                details.append(self.html.badge(
                    f"Expired ({obj.expires_at})",
                    variant="danger",
                    icon=Icons.ERROR
                ))
            else:
                details.append(self.html.inline([
                    self.html.span("Expires At:", "font-semibold"),
                    self.html.span(str(obj.expires_at), "")
                ], separator=" "))

        return "<br>".join(details)

    payment_details_display.short_description = "Payment Details"

    def qr_code_display(self, obj):
        """QR code for payment address."""
        if not obj.pay_address:
            return self.html.empty("No payment address")

        qr_url = f"/api/payments/{obj.id}/qr/"
        return f'<img src="{qr_url}" alt="QR Code" width="200" height="200">'

    qr_code_display.short_description = "QR Code"
```

## User Admin

User management with computed fields, status badges, and related counts.

```python
"""
User Admin - Complete example with computed fields
Features: @computed_field decorator, Status badges, Annotations
"""

from django.contrib import admin
from django.db.models import Count
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, DateTimeField, Icons,
    UserField, computed_field, annotated_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

# Configuration with annotations
customuser_config = AdminConfig(
    model=CustomUser,

    # Performance
    prefetch_related=["groups", "user_permissions"],

    # Annotations for counts
    annotations={
        'activity_count': Count('activities'),
        'email_count': Count('email_logs'),
        'ticket_count': Count('support_tickets'),
    },

    # List display
    list_display=[
        "avatar",
        "email",
        "full_name",
        "status",
        "activity_count_display",
        "last_login",
        "date_joined"
    ],

    # Auto-generated fields
    display_fields=[
        UserField(name="avatar", title="Avatar", header=True),
        BadgeField(name="email", title="Email", variant="info", icon=Icons.EMAIL),
        DateTimeField(name="last_login", title="Last Login", ordering="last_login"),
        DateTimeField(name="date_joined", title="Joined", ordering="date_joined"),
    ],

    # Filters
    list_filter=["is_staff", "is_active", "date_joined"],
    search_fields=["email", "first_name", "last_name"],
)

@admin.register(CustomUser)
class UserAdmin(PydanticAdmin):
    """Enhanced user admin with computed fields."""
    config = customuser_config

    @computed_field("Full Name", ordering="last_name")
    def full_name(self, obj):
        """Display full name with badge."""
        name = obj.get_full_name()
        if not name:
            return self.html.badge("No name", variant="secondary", icon=Icons.PERSON)
        return self.html.badge(name, variant="primary", icon=Icons.PERSON)

    @computed_field("Status", ordering="is_active")
    def status(self, obj):
        """Enhanced status display with conditional icons and colors."""
        if obj.is_superuser:
            return self.html.badge(
                "Superuser",
                variant="danger",
                icon=Icons.ADMIN_PANEL_SETTINGS
            )
        elif obj.is_staff:
            return self.html.badge(
                "Staff",
                variant="warning",
                icon=Icons.SETTINGS
            )
        elif obj.is_active:
            return self.html.badge(
                "Active",
                variant="success",
                icon=Icons.CHECK_CIRCLE
            )
        else:
            return self.html.badge(
                "Inactive",
                variant="secondary",
                icon=Icons.CANCEL
            )

    @annotated_field("Activities", annotation_name="activity_count")
    def activity_count_display(self, obj):
        """Display activity count from annotation."""
        count = getattr(obj, 'activity_count', 0)
        if count == 0:
            return self.html.empty()
        return self.html.badge(
            f"{count} activit{'ies' if count != 1 else 'y'}",
            variant="info",
            icon=Icons.HISTORY
        )
```

## E-commerce Order Admin

Order management with multiple related fields and aggregations.

```python
"""
Order Admin - E-commerce example
Features: Multi-field display, Aggregations, Related data
"""

from django.contrib import admin
from django.db.models import Count, Sum
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, CurrencyField, DateTimeField,
    FieldsetConfig, Icons, UserField, annotated_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

order_config = AdminConfig(
    model=Order,

    # Performance
    select_related=["user", "shipping_address"],
    prefetch_related=["items"],

    # Annotations
    annotations={
        'items_count': Count('items'),
        'total_amount': Sum('items__price'),
    },

    # List display
    list_display=[
        "order_number",
        "user",
        "items_count_display",
        "total_amount_display",
        "status",
        "created_at"
    ],

    # Display fields
    display_fields=[
        UserField(name="user", header=True, ordering="user__username"),
        BadgeField(
            name="status",
            label_map={
                "pending": "warning",
                "processing": "info",
                "shipped": "primary",
                "delivered": "success",
                "cancelled": "danger",
            },
            icon=Icons.SHOPPING_CART
        ),
        DateTimeField(name="created_at", ordering="created_at"),
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Order Information",
            fields=["order_number", "user", "status"]
        ),
        FieldsetConfig(
            title="Shipping",
            fields=["shipping_address", "shipping_method", "tracking_number"]
        ),
        FieldsetConfig(
            title="Items",
            fields=["order_items_display"],
            collapsed=True
        ),
    ],

    readonly_fields=["order_items_display"],
    list_filter=["status", "created_at"],
    search_fields=["order_number", "user__email"],
)

@admin.register(Order)
class OrderAdmin(PydanticAdmin):
    """E-commerce order admin."""
    config = order_config

    @annotated_field("Items", annotation_name="items_count")
    def items_count_display(self, obj):
        """Display item count from annotation."""
        count = getattr(obj, 'items_count', 0)
        return self.html.badge(
            f"{count} item{'s' if count != 1 else ''}",
            variant="info",
            icon=Icons.SHOPPING_BAG
        )

    @annotated_field("Total", annotation_name="total_amount", ordering="total_amount")
    def total_amount_display(self, obj):
        """Display total from annotation."""
        from django_cfg.modules.django_admin.utils.displays import MoneyDisplay
        from django_cfg.modules.django_admin.models.display_models import MoneyDisplayConfig

        total = getattr(obj, 'total_amount', 0) or 0
        config = MoneyDisplayConfig(currency="USD", precision=2)
        return MoneyDisplay.amount(total, config)

    def order_items_display(self, obj):
        """Display order items with self.html."""
        if not obj.pk:
            return "Save to see items"

        items = obj.items.all()
        if not items:
            return self.html.empty("No items")

        item_lines = []
        for item in items:
            item_lines.append(self.html.inline([
                self.html.badge(item.product.name, variant="primary"),
                self.html.span(f"×{item.quantity}", ""),
                self.html.span(f"${item.price:.2f}", "font-mono"),
            ], separator=" "))

        return "<br>".join(item_lines)

    order_items_display.short_description = "Order Items"
```

## Newsletter Admin

Newsletter management with email tracking and status indicators.

```python
"""
Newsletter Admin - Email campaign example
Features: Email tracking, Custom filters, Multiple computed fields
"""

from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, DateTimeField, Icons,
    UserField, computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

emaillog_config = AdminConfig(
    model=EmailLog,

    # Performance
    select_related=['user', 'newsletter'],

    # List display
    list_display=[
        "user_display",
        "recipient_display",
        "subject_display",
        "status_display",
        "tracking_display",
        "created_at"
    ],

    # Display fields
    display_fields=[
        UserField(name="user", title="User"),
        BadgeField(name="recipient", title="Recipient", variant="info", icon=Icons.EMAIL),
        BadgeField(name="subject", title="Subject", variant="primary"),
        DateTimeField(name="created_at", title="Created", ordering="created_at"),
    ],

    # Filters
    list_filter=["status", "created_at", "newsletter"],
    search_fields=["recipient", "subject", "user__username"],
)

@admin.register(EmailLog)
class EmailLogAdmin(PydanticAdmin):
    """Newsletter email tracking admin."""
    config = emaillog_config

    @computed_field("Status", ordering="status")
    def status_display(self, obj):
        """Status with icons."""
        icon_map = {
            'pending': Icons.SCHEDULE,
            'sent': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
        }
        variant_map = {
            'pending': 'warning',
            'sent': 'success',
            'failed': 'danger',
        }

        return self.html.badge(
            obj.get_status_display(),
            variant=variant_map.get(obj.status, 'secondary'),
            icon=icon_map.get(obj.status)
        )

    @computed_field("Tracking")
    def tracking_display(self, obj):
        """Email tracking indicators."""
        badges = []

        if obj.is_opened:
            badges.append(self.html.badge(
                "Opened",
                variant="success",
                icon=Icons.VISIBILITY
            ))

        if obj.is_clicked:
            badges.append(self.html.badge(
                "Clicked",
                variant="info",
                icon=Icons.MOUSE
            ))

        if not badges:
            return self.html.empty("No activity")

        return self.html.inline(badges, separator=" ")
```

## Cryptocurrency Exchange Admin

Crypto exchange with smart decimal formatting and market data.

```python
"""
Exchange Admin - Cryptocurrency example
Features: Smart decimal places, Large numbers, External links
"""

from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, BooleanField, CurrencyField,
    FieldsetConfig, Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

exchange_config = AdminConfig(
    model=Exchange,

    # List display
    list_display=[
        "name",
        "code",
        "volume_24h_usd",
        "rank",
        "is_active",
        "is_verified"
    ],

    # Display fields
    display_fields=[
        BadgeField(name="name", title="Exchange", variant="primary", icon=Icons.BUSINESS),
        BadgeField(name="code", title="Code", variant="info"),
        CurrencyField(
            name="volume_24h_usd",
            title="24h Volume",
            currency="USD",
            precision=0  # No decimals for large numbers
        ),
        BooleanField(name="is_active", title="Active"),
        BooleanField(name="is_verified", title="Verified"),
    ],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["name", "code", "description"]
        ),
        FieldsetConfig(
            title="Trading Data",
            fields=["volume_24h_usd", "rank", "trading_pairs_count"]
        ),
        FieldsetConfig(
            title="Links",
            fields=["website_link_display", "api_link_display"],
            collapsed=True
        ),
    ],

    readonly_fields=["website_link_display", "api_link_display"],
    list_filter=["is_active", "is_verified"],
    search_fields=["name", "code"],
    prepopulated_fields={'slug': ('name',)},
)

@admin.register(Exchange)
class ExchangeAdmin(PydanticAdmin):
    """Cryptocurrency exchange admin."""
    config = exchange_config

    def website_link_display(self, obj):
        """External website link."""
        if not obj.website_url:
            return self.html.empty()

        return self.html.link(
            obj.website_url,
            "Visit Website",
            css_class="text-blue-600",
            target="_blank"
        )

    website_link_display.short_description = "Website"

    def api_link_display(self, obj):
        """API documentation link."""
        if not obj.api_url:
            return self.html.empty()

        return self.html.inline([
            self.html.icon(Icons.API, size="sm"),
            self.html.link(obj.api_url, "API Docs", target="_blank")
        ])

    api_link_display.short_description = "API"
```

## Wallet Balance Admin

Exchange wallet balances with UUID shortening and custom avatar displays.

```python
"""
Wallet Balance Admin - Cryptocurrency exchange example
Features: UUID shortening, custom avatars, balance displays, SafeString HTML
"""

from decimal import Decimal
from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, DateTimeField, FieldsetConfig, Icons, computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

wallet_config = AdminConfig(
    model=MarketAccountWallet,

    # Performance optimization
    select_related=[
        'account', 'account__account', 'account__account__exchange',
        'account__account__user', 'coin'
    ],

    # List display with custom fields
    list_display=[
        'id_display',           # Shortened UUID
        'wallet_display',       # Custom avatar + text
        'coin_display',         # Badge
        'balance_total_display',
        'balance_available_display',
        'balance_locked_display',
        'value_usd_display',
        'last_sync_display',
    ],

    # Filters
    list_filter=[
        'account__market_type',
        'account__account__exchange',
        'coin__is_stable',
        'account__is_active',
    ],

    # Search
    search_fields=[
        'id', 'coin__symbol', 'coin__label',
        'account__account__name', 'account__account__user__email',
    ],

    # Ordering by balance
    ordering=['-balance_total', 'coin__symbol'],
    list_per_page=50,

    readonly_fields=['id', 'created_at', 'updated_at', 'last_sync_at'],
)


@admin.register(MarketAccountWallet)
class MarketAccountWalletAdmin(PydanticAdmin):
    config = wallet_config

    @computed_field("ID")
    def id_display(self, obj):
        """Short UUID with tooltip."""
        return self.html.uuid_short(obj.id, length=6)

    @computed_field("Wallet")
    def wallet_display(self, obj):
        """Custom avatar with account info."""
        if not obj.account or not obj.account.account:
            return self.html.empty("Unknown")

        account = obj.account.account
        market_type = obj.account.market_type
        header_text = f"{account.name} ({market_type})"
        subtitle_text = f"{account.exchange.name} - {account.user.email}"
        initials = account.name[:2].upper()

        # Use inline styles for perfect circular avatar
        from django.utils.safestring import mark_safe
        return mark_safe(
            f'<div class="flex items-center gap-3">'
            f'<div class="flex items-center justify-center rounded-full '
            f'bg-primary-100 text-primary-600 font-semibold flex-shrink-0" '
            f'style="width: 40px; height: 40px; min-width: 40px; min-height: 40px;">'
            f'{initials}'
            f'</div>'
            f'<div class="flex-1 min-w-0">'
            f'<div class="font-medium truncate">{header_text}</div>'
            f'<div class="text-sm text-gray-500 truncate">{subtitle_text}</div>'
            f'</div>'
            f'</div>'
        )

    @computed_field("Coin")
    def coin_display(self, obj):
        """Coin badge."""
        if not obj.coin:
            return self.html.empty("Unknown")
        return self.html.badge(obj.coin.symbol, variant="info", icon=Icons.CURRENCY_BITCOIN)

    @computed_field("Total")
    def balance_total_display(self, obj):
        """Total balance with currency."""
        if obj.balance_total <= 0:
            return self.html.span("0.00", "text-gray-500")

        precision = obj.coin.precision_display if obj.coin else 8
        formatted = f"{obj.balance_total:.{precision}f}".rstrip('0').rstrip('.')
        symbol = obj.coin.symbol if obj.coin else ''

        # Use inline with empty separator for adjacent HTML
        return self.html.inline([
            f'<strong>{formatted}</strong>',
            f'<span class="text-gray-500 ml-1">{symbol}</span>',
        ], separator="")

    @computed_field("Available")
    def balance_available_display(self, obj):
        """Available balance."""
        if obj.balance_available <= 0:
            return self.html.span("0.00", "text-gray-500")

        precision = obj.coin.precision_display if obj.coin else 8
        formatted = f"{obj.balance_available:.{precision}f}".rstrip('0').rstrip('.')
        symbol = obj.coin.symbol if obj.coin else ''

        return self.html.inline([
            self.html.span(formatted, "text-green-600 font-semibold"),
            f'<span class="text-gray-500 ml-1">{symbol}</span>',
        ], separator="")

    @computed_field("Value USD")
    def value_usd_display(self, obj):
        """USD value badge."""
        if not obj.coin or not obj.coin.price_usd:
            return self.html.span("—", "text-gray-500")

        value_usd = obj.balance_total * obj.coin.price_usd
        if value_usd < Decimal('0.01'):
            return self.html.span("< $0.01", "text-gray-500")

        return self.html.badge(
            f"${value_usd:,.2f}",
            variant="success",
            icon=Icons.ATTACH_MONEY,
        )
```

**Key Features:**
- `uuid_short()` for clean ID display with tooltip
- Custom circular avatar with fixed proportions
- `inline()` with `separator=""` for adjacent HTML elements
- Tailwind CSS classes for styling
- `mark_safe()` for complex HTML structures
- Perfect for financial/crypto applications

## Common Patterns

### Pattern 1: Conditional Badges

```python
@computed_field("Priority")
def priority_display(self, obj):
    """Priority with colors based on value."""
    priority_map = {
        'low': ('info', Icons.ARROW_DOWNWARD),
        'medium': ('warning', Icons.REMOVE),
        'high': ('danger', Icons.ARROW_UPWARD),
        'critical': ('danger', Icons.PRIORITY_HIGH),
    }

    variant, icon = priority_map.get(obj.priority, ('secondary', None))
    return self.html.badge(obj.get_priority_display(), variant=variant, icon=icon)
```

### Pattern 2: Multiple Inline Badges

```python
@computed_field("Features")
def features_display(self, obj):
    """Show multiple feature badges."""
    badges = []

    if obj.is_featured:
        badges.append(self.html.badge("Featured", variant="success", icon=Icons.STAR))

    if obj.is_new:
        badges.append(self.html.badge("New", variant="info", icon=Icons.NEW_RELEASES))

    if obj.on_sale:
        badges.append(self.html.badge("Sale", variant="danger", icon=Icons.LOCAL_OFFER))

    return self.html.inline(badges, separator=" ") if badges else self.html.empty()
```

### Pattern 3: Complex Readonly Field

```python
def detailed_info_display(self, obj):
    """Complex info using multiple self.html methods."""
    sections = []

    # Header
    sections.append(self.html.span("Details", "text-lg font-bold"))

    # Key-value pairs
    info_items = [
        ("ID", obj.id),
        ("Created", obj.created_at.strftime("%Y-%m-%d")),
        ("Updated", obj.updated_at.strftime("%Y-%m-%d")),
    ]

    for label, value in info_items:
        sections.append(self.html.inline([
            self.html.span(f"{label}:", "font-semibold"),
            self.html.span(str(value), "")
        ], separator=" "))

    # Status badge
    sections.append(self.html.badge(
        obj.get_status_display(),
        variant="success" if obj.is_active else "secondary"
    ))

    return "<br>".join(sections)
```

### Time-Based Colored Text

```python
@computed_field("Last Activity")
def last_activity_display(self, obj):
    """Show time ago with color based on freshness."""
    if not obj.last_activity_at:
        return self.html.empty("Never")
    
    from django.utils import timezone
    from django.utils.timesince import timesince
    
    age_seconds = (timezone.now() - obj.last_activity_at).total_seconds()
    time_ago = timesince(obj.last_activity_at, timezone.now())
    
    # Color based on freshness
    if age_seconds < 120:  # < 2 minutes
        color = "success"
    elif age_seconds < 300:  # < 5 minutes
        color = "warning"
    else:  # > 5 minutes
        color = "danger"
    
    return self.html.colored_text(f"{time_ago} ago", color)
```

### Status with Icon and Color

```python
@computed_field("Connection Status")
def connection_status_display(self, obj):
    """Show connection status with icon and color."""
    if obj.is_connected:
        return self.html.icon_text(
            Icons.CHECK_CIRCLE, 
            "Connected", 
            color="success"
        )
    
    # Show disconnection time with color
    if obj.last_seen_at:
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        age_seconds = (timezone.now() - obj.last_seen_at).total_seconds()
        time_ago = timesince(obj.last_seen_at, timezone.now())
        
        # Gradually change color as time passes
        if age_seconds < 60:  # < 1 minute
            color = "warning"
            icon = Icons.SCHEDULE
        elif age_seconds < 300:  # < 5 minutes
            color = "warning"
            icon = Icons.CANCEL
        else:  # > 5 minutes
            color = "danger"
            icon = Icons.ERROR
        
        return self.html.icon_text(icon, f"Offline {time_ago}", color=color)
    
    return self.html.icon_text(Icons.CANCEL, "Never connected", color="secondary")
```

## Next Steps

- **[Overview](./overview.md)** - Learn the philosophy
- **[Quick Start](./quick-start.md)** - Get started in 5 minutes
- **[Configuration](./configuration.md)** - Complete configuration reference
- **[Field Types](./field-types.md)** - All field types
- **[Filters](./filters.md)** - Complete guide to filters

:::tip[Pro Tip]
All examples above are from real production code. Copy-paste and adapt them to your needs!
:::
