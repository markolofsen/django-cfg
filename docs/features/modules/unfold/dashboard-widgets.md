---
title: Dashboard Widgets System
description: Create beautiful, type-safe dashboard widgets with automatic template variable resolution and real-time metrics.
sidebar_label: Dashboard Widgets
sidebar_position: 2
keywords:
  - dashboard widgets
  - unfold widgets
  - django-cfg dashboard
  - stats cards
  - widget system
---

# Dashboard Widgets System

Django-CFG includes a **powerful widget system** for creating beautiful, interactive dashboard widgets with automatic template variable resolution and real-time metrics.

## Overview

The Dashboard Widgets system provides:
- **Type-Safe Widgets** - Define widgets using Pydantic models
- **Template Variable Resolution** - Automatic template variable resolution for dynamic values
- **Multiple Widget Types** - Stats cards, charts, and custom widgets
- **Real-Time Metrics** - System, RPC, and custom application metrics
- **Automatic Integration** - Seamlessly integrated with Unfold dashboard
- **Tabbed Interface** - Widgets displayed in dedicated "Widgets" tab

## Quick Start

### Basic Widget Configuration

```python
# config.py
from django_cfg import DjangoConfig, UnfoldConfig
from django_cfg.modules.django_unfold.models.dashboard import StatCard, StatsCardsWidget
from django_cfg.modules.django_unfold.callbacks import UnfoldCallbacks
from django_cfg import Icons

class MyConfig(DjangoConfig):
    unfold: UnfoldConfig = UnfoldConfig(
        dashboard_callback="myapp.config.dashboard_callback"
    )

def dashboard_callback(request, context):
    """Custom dashboard with widgets."""
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta

    User = get_user_model()

    # 1. Get real data FIRST
    total_users = User.objects.count()
    week_ago = timezone.now() - timedelta(days=7)
    recent_users = User.objects.filter(date_joined__gte=week_ago).count()

    # 2. Create widgets with template variables
    custom_widgets = [
        StatsCardsWidget(
            title="User Metrics",
            cards=[
                StatCard(
                    title="Total Users",
                    value="{'{{'} total_users {'}}'}",  # Template variable
                    icon=Icons.PEOPLE,
                    change="{'{{'} recent_users_change {'}}'}",
                    change_type="positive" if recent_users > 0 else "neutral",
                    description="Registered users",
                    color="primary"
                ),
            ]
        )
    ]

    # 3. Add widgets and metrics to context BEFORE calling main callback
    context.update({
        "custom_widgets": custom_widgets,
        "total_users": total_users,  # Actual value for template resolution
        "recent_users_change": f"+{recent_users}" if recent_users > 0 else "0",
    })

    # 4. Call base callback - it picks up custom_widgets automatically
    unfold_callbacks = UnfoldCallbacks()
    context = unfold_callbacks.main_dashboard_callback(request, context)

    return context
```

## Widget Types

### StatsCardsWidget

Display grouped statistics with icons, colors, and change indicators:

```python
from django_cfg.modules.django_unfold.models.dashboard import StatCard, StatsCardsWidget
from django_cfg import Icons

# Create a widget group
stats_widget = StatsCardsWidget(
    title="Trading Metrics",
    cards=[
        StatCard(
            title="Active Bots",
            value="{'{{'} active_bots {'}}'}",
            icon=Icons.SMART_TOY,
            change="{'{{'} total_bots_change {'}}'}",
            change_type="positive",  # positive, negative, neutral
            description="Running trading bots",
            color="primary"  # primary, success, danger, warning, info
        ),
        StatCard(
            title="Open Deals",
            value="{'{{'} open_deals {'}}'}",
            icon=Icons.ATTACH_MONEY,
            change="{'{{'} total_deals_change {'}}'}",
            change_type="positive",
            description="{'{{'} closed_deals_text {'}}'}",
            color="success"
        ),
    ]
)
```

### StatCard Configuration

| Field | Type | Description |
|-------|------|-------------|
| `title` | str | Card title |
| `value` | str | Main value (supports template variables) |
| `icon` | str | Material icon name (use `Icons.*`) |
| `change` | str | Change indicator (optional, supports template variables) |
| `change_type` | str | "positive", "negative", or "neutral" |
| `description` | str | Additional description (supports template variables) |
| `color` | str | Card accent color: "primary", "success", "danger", "warning", "info" |

## Template Variables

Template variables allow dynamic value resolution at render time:

### Basic Usage

```python
def dashboard_callback(request, context):
    # 1. Get data
    user_count = User.objects.count()

    # 2. Create widget with template variable
    custom_widgets = [
        StatsCardsWidget(
            title="Metrics",
            cards=[
                StatCard(
                    title="Users",
                    value="{'{{'} user_count {'}}'}",  # Will be resolved to actual value
                    icon=Icons.PEOPLE
                )
            ]
        )
    ]

    # 3. Provide actual value
    context.update({
        "custom_widgets": custom_widgets,
        "user_count": user_count,  # This resolves {'{{'} user_count {'}}'}
    })

    # 4. Call base callback
    unfold_callbacks = UnfoldCallbacks()
    return unfold_callbacks.main_dashboard_callback(request, context)
```

### Multiple Variables

```python
def dashboard_callback(request, context):
    # Calculate metrics
    total = Order.objects.count()
    pending = Order.objects.filter(status='pending').count()
    completed = Order.objects.filter(status='completed').count()

    # Create widget with multiple template variables
    custom_widgets = [
        StatsCardsWidget(
            title="Order Statistics",
            cards=[
                StatCard(
                    title="Total Orders",
                    value="{'{{'} total_orders {'}}'}",
                    change="{'{{'} completed_orders_text {'}}'}",
                    description="{'{{'} pending_orders_text {'}}'}",
                    icon=Icons.SHOPPING_CART
                )
            ]
        )
    ]

    # Provide all values
    context.update({
        "custom_widgets": custom_widgets,
        "total_orders": total,
        "completed_orders_text": f"{completed} completed",
        "pending_orders_text": f"{pending} pending",
    })

    unfold_callbacks = UnfoldCallbacks()
    return unfold_callbacks.main_dashboard_callback(request, context)
```

## Real-World Examples

### E-Commerce Dashboard

```python
def dashboard_callback(request, context):
    from apps.orders.models import Order
    from apps.products.models import Product
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta

    # Get metrics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()

    # Revenue calculation
    today = timezone.now().date()
    daily_revenue = Order.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Create widgets
    custom_widgets = [
        StatsCardsWidget(
            title="Sales Metrics",
            cards=[
                StatCard(
                    title="Total Orders",
                    value="{'{{'} total_orders {'}}'}",
                    icon=Icons.SHOPPING_CART,
                    change="{'{{'} pending_orders_text {'}}'}",
                    description="All orders",
                    color="primary"
                ),
                StatCard(
                    title="Daily Revenue",
                    value="{'{{'} daily_revenue {'}}'}",
                    icon=Icons.ATTACH_MONEY,
                    description="Today's revenue",
                    color="success"
                ),
                StatCard(
                    title="Products",
                    value="{'{{'} total_products {'}}'}",
                    icon=Icons.INVENTORY,
                    description="Total products",
                    color="info"
                ),
            ]
        ),
    ]

    # Add to context
    context.update({
        "custom_widgets": custom_widgets,
        "total_orders": total_orders,
        "pending_orders_text": f"{pending_orders} pending",
        "daily_revenue": f"${daily_revenue:,.2f}",
        "total_products": total_products,
    })

    unfold_callbacks = UnfoldCallbacks()
    return unfold_callbacks.main_dashboard_callback(request, context)
```

### Trading Platform Dashboard

```python
def dashboard_callback(request, context):
    from apps.trading_bots.models import TradingBot
    from apps.stock_deals.models import StockDeal
    from decimal import Decimal

    # Get trading metrics
    active_bots = TradingBot.objects.filter(
        is_active=True,
        status='running'
    ).count()
    total_bots = TradingBot.objects.count()
    open_deals = StockDeal.objects.filter(status='open').count()

    # P&L calculation
    day_ago = timezone.now() - timedelta(days=1)
    daily_profit = StockDeal.objects.filter(
        status='close',
        closed_at__gte=day_ago,
        profit_loss__gt=0
    ).aggregate(total=Sum('profit_loss'))['total'] or Decimal('0')

    # Create widgets
    custom_widgets = [
        StatsCardsWidget(
            title="Trading Metrics",
            cards=[
                StatCard(
                    title="Active Bots",
                    value="{'{{'} active_bots {'}}'}",
                    icon=Icons.SMART_TOY,
                    change="{'{{'} total_bots_text {'}}'}",
                    change_type="positive",
                    description="Running trading bots",
                    color="primary"
                ),
                StatCard(
                    title="Open Deals",
                    value="{'{{'} open_deals {'}}'}",
                    icon=Icons.ATTACH_MONEY,
                    description="Active positions",
                    color="success"
                ),
                StatCard(
                    title="Daily P&L",
                    value="{'{{'} daily_pnl {'}}'}",
                    icon=Icons.ANALYTICS,
                    description="24h profit/loss",
                    color="success" if daily_profit > 0 else "danger"
                ),
            ]
        ),
    ]

    # Add to context
    context.update({
        "custom_widgets": custom_widgets,
        "active_bots": active_bots,
        "total_bots_text": f"{total_bots} total",
        "open_deals": open_deals,
        "daily_pnl": f"${daily_profit:,.2f}",
    })

    unfold_callbacks = UnfoldCallbacks()
    return unfold_callbacks.main_dashboard_callback(request, context)
```

### Multi-Workspace IDE Dashboard

```python
def dashboard_callback(request, context):
    from apps.workspaces.models import Workspace, Session
    from apps.ai_agents.models import AIAgent, AITask

    # Get workspace metrics
    total_workspaces = Workspace.objects.count()
    active_workspaces = Workspace.objects.filter(is_active=True).count()
    active_sessions = Session.objects.filter(status='running').count()

    # AI metrics
    total_ai_agents = AIAgent.objects.filter(is_active=True).count()
    running_tasks = AITask.objects.filter(status='running').count()

    # Recent activity
    week_ago = timezone.now() - timedelta(days=7)
    recent_workspaces = Workspace.objects.filter(
        created_at__gte=week_ago
    ).count()

    # Create widgets
    custom_widgets = [
        StatsCardsWidget(
            title="Workspace Metrics",
            cards=[
                StatCard(
                    title="Total Workspaces",
                    value="{'{{'} total_workspaces {'}}'}",
                    icon=Icons.FOLDER,
                    change="{'{{'} recent_workspaces_text {'}}'}",
                    change_type="positive",
                    description="{'{{'} active_workspaces_text {'}}'}",
                    color="primary"
                ),
                StatCard(
                    title="Active Sessions",
                    value="{'{{'} active_sessions {'}}'}",
                    icon=Icons.TERMINAL,
                    description="Running sessions",
                    color="success"
                ),
            ]
        ),
        StatsCardsWidget(
            title="AI Metrics",
            cards=[
                StatCard(
                    title="AI Agents",
                    value="{'{{'} total_ai_agents {'}}'}",
                    icon=Icons.SMART_TOY,
                    change="{'{{'} running_tasks_text {'}}'}",
                    change_type="positive",
                    description="Active agents",
                    color="warning"
                ),
            ]
        ),
    ]

    # Add to context
    context.update({
        "custom_widgets": custom_widgets,
        "total_workspaces": total_workspaces,
        "active_workspaces_text": f"{active_workspaces} active",
        "recent_workspaces_text": f"+{recent_workspaces} this week",
        "active_sessions": active_sessions,
        "total_ai_agents": total_ai_agents,
        "running_tasks_text": f"{running_tasks} running",
    })

    unfold_callbacks = UnfoldCallbacks()
    return unfold_callbacks.main_dashboard_callback(request, context)
```

## Built-in System Widgets

Django-CFG automatically provides system monitoring widgets:

### System Overview

Automatically included - shows CPU, Memory, and Disk usage:

```python
# Provided automatically by DashboardManager.get_widgets_config()
StatsCardsWidget(
    title="System Overview",
    cards=[
        StatCard(
            title="CPU Usage",
            value="{'{{'} cpu_percent {'}}'}%",
            icon=Icons.MEMORY,
            color="blue"
        ),
        StatCard(
            title="Memory",
            value="{'{{'} memory_percent {'}}'}%",
            icon=Icons.STORAGE,
            color="purple"
        ),
        StatCard(
            title="Disk",
            value="{'{{'} disk_percent {'}}'}%",
            icon=Icons.SAVE,
            color="orange"
        ),
    ]
)
```

### RPC Monitoring (if Centrifugo enabled)

Automatically included when `centrifugo` is configured:

```python
# Provided automatically when centrifugo.enabled = True
StatsCardsWidget(
    title="Centrifugo RPC Monitoring",
    cards=[
        StatCard(
            title="Total Calls",
            value="{'{{'} rpc_total_calls {'}}'}",
            icon=Icons.API,
            color="blue"
        ),
        StatCard(
            title="Success Rate",
            value="{'{{'} rpc_success_rate {'}}'}%",
            icon=Icons.CHECK_CIRCLE,
            color="green"
        ),
        StatCard(
            title="Avg Response Time",
            value="{'{{'} rpc_avg_duration {'}}'}ms",
            icon=Icons.SPEED,
            color="purple"
        ),
        StatCard(
            title="Failed Calls",
            value="{'{{'} rpc_failed_calls {'}}'}",
            icon=Icons.ERROR,
            color="red"
        ),
    ]
)
```

## Best Practices

### 1. Execution Order

**CRITICAL**: Always add widgets to context BEFORE calling `main_dashboard_callback()`:

```python
def dashboard_callback(request, context):
    # ✅ CORRECT: Add widgets FIRST
    context.update({
        "custom_widgets": custom_widgets,
        "metric_value": 123,
    })

    # Then call base callback
    unfold_callbacks = UnfoldCallbacks()
    context = unfold_callbacks.main_dashboard_callback(request, context)

    return context

def dashboard_callback_wrong(request, context):
    # ❌ WRONG: Calling base callback FIRST
    unfold_callbacks = UnfoldCallbacks()
    context = unfold_callbacks.main_dashboard_callback(request, context)

    # Widgets added too late - won't be processed!
    context.update({
        "custom_widgets": custom_widgets,
    })

    return context
```

### 2. Template Variable Naming

Use clear, descriptive variable names:

```python
# ✅ GOOD: Clear, descriptive names
context.update({
    "total_users": user_count,
    "recent_users_change": f"+{recent_users}",
    "active_sessions_text": f"{active_sessions} active",
})

# ❌ BAD: Unclear names
context.update({
    "val1": user_count,
    "txt": f"+{recent_users}",
    "x": f"{active_sessions} active",
})
```

### 3. Data Fetching Performance

Optimize database queries:

```python
def dashboard_callback(request, context):
    from django.db.models import Count, Sum

    # ✅ GOOD: Single query with aggregation
    stats = Order.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        revenue=Sum('total_amount')
    )

    # ❌ BAD: Multiple queries
    total = Order.objects.count()
    pending = Order.objects.filter(status='pending').count()
    revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum']
```

### 4. Widget Organization

Group related metrics together:

```python
custom_widgets = [
    # Group 1: User metrics
    StatsCardsWidget(
        title="User Metrics",
        cards=[
            StatCard(title="Total Users", ...),
            StatCard(title="Active Users", ...),
        ]
    ),

    # Group 2: Business metrics
    StatsCardsWidget(
        title="Business Metrics",
        cards=[
            StatCard(title="Revenue", ...),
            StatCard(title="Orders", ...),
        ]
    ),
]
```

### 5. Error Handling

Always handle potential errors:

```python
def dashboard_callback(request, context):
    try:
        # Get metrics
        total_users = User.objects.count()

        # Create widgets
        custom_widgets = [...]

        context.update({
            "custom_widgets": custom_widgets,
            "total_users": total_users,
        })

        unfold_callbacks = UnfoldCallbacks()
        return unfold_callbacks.main_dashboard_callback(request, context)

    except Exception as e:
        # Fallback
        context.update({
            "dashboard_title": "Dashboard",
            "error": f"Error: {str(e)}",
        })
        return context
```

## Icon Reference

Common Material icons for widgets:

```python
from django_cfg import Icons

# User & People
Icons.PEOPLE              # Group of people
Icons.PERSON              # Single person
Icons.ADMIN_PANEL_SETTINGS  # Admin

# Business & Money
Icons.ATTACH_MONEY        # Dollar sign
Icons.RECEIPT             # Receipt
Icons.SHOPPING_CART       # Cart
Icons.BUSINESS            # Business building
Icons.PAYMENTS            # Payments

# Status & Indicators
Icons.CHECK_CIRCLE        # Success/Complete
Icons.CANCEL              # Failed/Cancelled
Icons.ERROR               # Error
Icons.WARNING             # Warning
Icons.INFO                # Information

# Technology & System
Icons.SMART_TOY           # Bot/AI
Icons.TERMINAL            # Terminal/Console
Icons.API                 # API
Icons.SPEED               # Performance
Icons.MEMORY              # CPU/Memory
Icons.STORAGE             # Disk/Storage

# Analytics
Icons.ANALYTICS           # Charts/Analytics
Icons.TRENDING_UP         # Trending up
Icons.TRENDING_DOWN       # Trending down
Icons.TIMELINE            # Timeline

# Development
Icons.CODE                # Code
Icons.FOLDER              # Folder/Workspace
Icons.SOURCE              # Source code
Icons.DEVELOPER_BOARD     # Development
```

## Troubleshooting

### Widgets Not Appearing

**Problem**: Widgets don't show up in dashboard.

**Solution**: Check execution order:
```python
# Make sure widgets are added BEFORE main_dashboard_callback
context.update({"custom_widgets": custom_widgets})
context = unfold_callbacks.main_dashboard_callback(request, context)
```

### Template Variables Not Resolving

**Problem**: Seeing `{'{{'} variable {'}}'}` instead of actual value.

**Solution**: Ensure you provide the actual value in context:
```python
# Widget definition
StatCard(value="{'{{'} total_users {'}}'}", ...)

# Must provide in context
context.update({"total_users": 123})  # Not just the widget!
```

### Performance Issues

**Problem**: Dashboard loading slowly.

**Solution**: Optimize queries:
```python
# Use aggregation instead of multiple queries
stats = Model.objects.aggregate(
    count=Count('id'),
    sum=Sum('amount')
)
```

## Related Documentation

- [**Unfold Overview**](./overview.md) - Unfold admin configuration
- [**Dashboard Callbacks**](./overview.md#custom-dashboard-callbacks) - Callback system
- [**Centrifugo Integration**](/features/integrations/centrifugo/) - RPC monitoring widgets

:::tip[Key Takeaways]
- Always add `custom_widgets` to context **BEFORE** calling `main_dashboard_callback()`
- Use template variables ({'{{'} variable {'}}'}) for dynamic values
- Provide actual values in context for template resolution
- Group related metrics in StatsCardsWidget
- Use Material icons from `Icons` enum for consistency
:::

The Dashboard Widgets system makes it easy to create beautiful, real-time dashboards! 📊
