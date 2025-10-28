---
title: Unfold Module Updates
description: Latest features and improvements to Django-CFG Unfold admin module
sidebar_label: What's New
sidebar_position: 10
---

# What's New in Unfold Module

## 🎨 Next.js Dashboard Integration

Modern React-based admin dashboard with real-time capabilities and type-safe API.

### Features

- **Next.js Dashboard** - Modern React-based admin dashboard served via iframe
- **REST API Backend** - Complete API at `/cfg/dashboard/api/` for all dashboard data
- **Service Layer** - Clean service classes for statistics, health, charts, and commands
- **Type-Safe** - Full TypeScript + Pydantic type safety
- **Real-Time** - WebSocket support via Centrifugo integration

### API Endpoints

Access dashboard data via REST API:

- `/cfg/dashboard/api/statistics/` - User and app statistics
- `/cfg/dashboard/api/health/` - System health checks
- `/cfg/dashboard/api/charts/` - Chart data
- `/cfg/dashboard/api/commands/` - Django management commands

### Configuration

The dashboard is automatically configured and served at `/admin/`. No additional setup required.

```python
from django_cfg import DjangoConfig, UnfoldConfig

class MyConfig(DjangoConfig):
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="My Admin",
        site_header="Admin Panel",
        theme='dark',
    )
```

---

## 🔧 Centrifugo WebSocket Integration

Real-time communication via WebSocket with automatic RPC logging.

### Features

- **RPC Logging** - Automatic logging of all RPC calls to database
- **Admin Interface** - RPC Logs admin panel with filtering
- **Real-Time Metrics** - WebSocket connection monitoring
- **Type-Safe** - Full Pydantic validation for all messages

### Configuration

```python
from django_cfg import DjangoConfig, DjangoCfgCentrifugoConfig

class MyConfig(DjangoConfig):
    centrifugo: DjangoCfgCentrifugoConfig = DjangoCfgCentrifugoConfig(
        enabled=True,
        centrifugo_url="ws://localhost:8000/connection/websocket",
        log_all_calls=True,
        log_level="INFO",
    )
```

### Usage

Access Centrifugo dashboard at `/cfg/centrifugo/admin/` to view:
- Real-time connection status
- RPC call logs
- Channel statistics
- Error tracking

---

## 🎯 Navigation Manager

Automatic navigation generation based on enabled Django-CFG modules.

### Auto-Generated Sections

The NavigationManager automatically creates sidebar sections for:

- **Dashboard** - Overview, Frontend Admin, Settings, Health Check
- **Centrifugo** (if enabled) - Dashboard, Logs
- **Operations** (if enabled) - Background Tasks, Maintenance
- **Users & Access** (if accounts enabled) - Users, Groups, OTP Secrets
- **Support** (if enabled) - Tickets, Messages
- **Newsletter** (if enabled) - Newsletters, Subscriptions, Campaigns
- **Leads** (if enabled) - Lead management
- **AI Agents** (if enabled) - Agent Definitions, Executions, Templates
- **Knowledge Base** (if enabled) - Documents, Chunks, Chat Sessions
- **Payments** (if enabled) - Payments, Currencies, Balances

### Custom Navigation

Add your own navigation sections:

```python
from django_cfg.modules.django_unfold import UnfoldConfig, NavigationSection, NavigationItem
from django_cfg.modules.django_admin.icons import Icons

unfold: UnfoldConfig = UnfoldConfig(
    navigation=[
        NavigationSection(
            title="My App",
            separator=True,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Products",
                    icon=Icons.SHOPPING_CART,
                    link="admin:myapp_product_changelist"
                ),
            ]
        ),
    ],
)
```

---

## 🎨 Theme Customization

OKLCH color format for modern, perceptually uniform theming.

### Features

- **OKLCH Colors** - Perceptually uniform color space
- **Dark/Light Modes** - Automatic theme switching
- **Custom Colors** - Full color customization
- **Tailwind Integration** - Seamless Tailwind CSS integration

### Configuration

```python
from django_cfg.modules.django_unfold import UnfoldConfig, UnfoldColors

unfold: UnfoldConfig = UnfoldConfig(
    theme='dark',  # 'dark', 'light', or None for auto
    colors=UnfoldColors(
        primary="#3b82f6",  # Brand color
    ),
)
```

---

## 📚 Related Documentation

- [Unfold Overview](./overview.md) - Complete module documentation
- [Centrifugo Integration](/features/integrations/centrifugo/) - Real-time WebSocket setup
- [Configuration Guide](/fundamentals/configuration) - Unfold configuration

---

## 🚀 Quick Start

```python
from django_cfg import DjangoConfig, UnfoldConfig, DjangoCfgCentrifugoConfig

class MyConfig(DjangoConfig):
    # Unfold admin interface
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="My Admin",
        theme='dark',
    )

    # Optional: Centrifugo WebSocket
    centrifugo: DjangoCfgCentrifugoConfig = DjangoCfgCentrifugoConfig(
        enabled=True,
        centrifugo_url="ws://localhost:8000/connection/websocket",
    )
```

Access admin at: `http://localhost:8000/admin/`

---

## 💡 Tips

- Dashboard automatically adapts to enabled Django-CFG modules
- Use `NavigationManager` for consistent sidebar across projects
- OKLCH colors provide better color interpolation than RGB
- Centrifugo logging helps debug real-time issues
- All APIs are documented via OpenAPI/Swagger at `/api/schema/swagger/`
