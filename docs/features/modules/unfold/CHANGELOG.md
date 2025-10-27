---
title: Unfold Module Changelog
description: Latest updates and improvements to Django-CFG Unfold admin module
sidebar_label: Changelog
sidebar_position: 10
---

# Unfold Module Changelog

## Latest Updates (October 2023)

### 🎨 Dashboard Widgets System

A powerful new widget system for creating beautiful, type-safe dashboard widgets with automatic template variable resolution.

#### Features

- **Type-Safe Widgets** - Define widgets using Pydantic models (`StatsCardsWidget`, `StatCard`)
- **Template Variables** - Use `{{ variable }}` syntax for dynamic values with automatic resolution
- **Material Icons** - 2234+ icons with full IDE autocomplete (`Icons.*`)
- **Real-Time Metrics** - Built-in system, RPC, and custom application metrics
- **Tabbed Interface** - Widgets displayed in dedicated "Widgets" tab
- **Multiple Widget Groups** - Organize related metrics in widget groups

#### Migration Guide

**Before** (Old approach - still works):
```python
def dashboard_callback(request, context):
    context['total_users'] = User.objects.count()
    return context
```

**After** (New widgets approach):
```python
from django_cfg.modules.django_unfold.models.dashboard import StatCard, StatsCardsWidget
from django_cfg.modules.django_unfold.callbacks import UnfoldCallbacks
from django_cfg import Icons

def dashboard_callback(request, context):
    # 1. Get data
    total_users = User.objects.count()

    # 2. Create widgets
    custom_widgets = [
        StatsCardsWidget(
            title="User Metrics",
            cards=[
                StatCard(
                    title="Total Users",
                    value="{{ total_users }}",
                    icon=Icons.PEOPLE,
                    color="primary"
                )
            ]
        )
    ]

    # 3. Add to context BEFORE calling main callback
    context.update({
        "custom_widgets": custom_widgets,
        "total_users": total_users,
    })

    # 4. Call base callback
    unfold_callbacks = UnfoldCallbacks()
    return unfold_callbacks.main_dashboard_callback(request, context)
```

#### Breaking Changes

None - fully backward compatible.

#### Documentation

- [Dashboard Widgets Guide](./dashboard-widgets.md) - Complete guide with examples
- [Unfold Overview](./overview.md) - Updated with widget examples

---

### 🔧 Centrifugo WebSocket RPC Integration

#### New Features

- **RPC Logging** - Automatic logging of all RPC calls to database
- **RPC Dashboard Widgets** - Automatic RPC monitoring widgets when Centrifugo is enabled
- **Admin Interface** - New RPC Logs admin panel

#### Database Models

New `RPCLog` model for storing RPC call history:
- Request/Response tracking
- Duration monitoring
- Success/Error tracking
- Automatic cleanup of old logs

#### Configuration

RPC logging is automatically enabled when `centrifugo` is configured:

```python
from django_cfg import DjangoConfig, DjangoCfgCentrifugoConfig

class MyConfig(DjangoConfig):
    centrifugo: DjangoCfgCentrifugoConfig = DjangoCfgCentrifugoConfig(
        enabled=True,
        centrifugo_url="ws://localhost:8000/connection/websocket",
        log_all_calls=True,  # Enable RPC logging (default: True)
        log_level="INFO",    # Log level (default: "INFO")
    )
```

#### Automatic Widgets

When RPC is enabled, these widgets are automatically added:

- **Total Calls** - Total RPC calls in last 24h
- **Success Rate** - Percentage of successful calls
- **Avg Response Time** - Average response time in ms
- **Failed Calls** - Number of failed calls

---

### 📊 Dashboard System Improvements

#### New Components

- **WidgetsSection** - New section for rendering widgets (`modules/django_dashboard/sections/widgets.py`)
- **widgets_section.html** - Template for widgets display
- **widgets_tab.html** - Tab wrapper for widgets interface

#### Template Structure

```
templates/admin/
├── layouts/
│   └── dashboard_with_tabs.html (updated - added Widgets tab)
├── sections/
│   └── widgets_section.html (new)
└── snippets/
    └── tabs/
        └── widgets_tab.html (new)
```

#### Callback System

Enhanced `UnfoldCallbacks` to support:
- Automatic extraction of `custom_widgets` from context
- Template variable resolution for widget values
- Custom metrics merging

---

## Upgrade Path

### Step 1: Update Django-CFG

```bash
poetry update django-cfg
# or
pip install --upgrade django-cfg
```

### Step 2: Run Migrations (if using RPC)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Update dashboard_callback (Optional)

If you want to use the new widgets system, update your `dashboard_callback` following the pattern above.

**Note**: Old callbacks continue to work without changes.

---

## Related Documentation

- [Dashboard Widgets Guide](./dashboard-widgets.md) - Complete widgets documentation
- [Unfold Overview](./overview.md) - Main unfold documentation
- [Centrifugo Integration](/features/integrations/centrifugo/) - RPC system documentation

---

## Feedback

Found an issue or have a suggestion? Please [open an issue](https://github.com/your-repo/issues).
