---
title: Django Unfold Overview
description: Django-CFG overview feature guide. Production-ready django unfold overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview & Philosophy
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# Unfold Admin Module

Django-CFG includes a **comprehensive Unfold admin interface integration** that provides beautiful, modern admin dashboards with advanced theming, navigation, and monitoring capabilities.

## Overview

The Django Unfold module provides:
- **Modern Admin Interface** - Beautiful, responsive admin design
- **Advanced Dashboard** - Customizable dashboard with widgets and statistics
- **Theme System** - Complete theming with colors, fonts, and layouts
- **Navigation Management** - Dynamic sidebar and navigation configuration
- **System Monitoring** - Real-time system health and performance metrics
- **Callback System** - Extensible callback system for custom functionality

## Quick Start

### Automatic Integration

```python
# config.py
from django_cfg import DjangoConfig, UnfoldConfig

class MyConfig(DjangoConfig):
    # Enable Unfold admin interface
    unfold: UnfoldConfig | None = UnfoldConfig(
        site_title="My Admin",
        site_header="My Project Administration",
    )
```

### Manual Configuration

```python
# settings.py
INSTALLED_APPS = [
    "unfold",  # Must be before django.contrib.admin
    "django.contrib.admin",
    # ... other apps
    "django_cfg",
]

# Unfold settings
UNFOLD = {
    "SITE_TITLE": "Django CFG Admin",
    "SITE_HEADER": "Django CFG Administration",
    "SITE_URL": "/",
    "SITE_ICON": "speed",
    "SITE_LOGO": {
        "light": "/static/logo-light.svg",
        "dark": "/static/logo-dark.svg",
    },
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "django_cfg.core.environment.get_environment_name",
    "DASHBOARD_CALLBACK": "django_cfg.modules.django_unfold.callbacks.dashboard_callback",
    "LOGIN": {
        "image": "/static/admin-login.jpg",
        "redirect_after": "/admin/",
    },
    "STYLES": [
        lambda request: "/static/css/custom-admin.css",
    ],
    "SCRIPTS": [
        lambda request: "/static/js/custom-admin.js",
    ],
}
```

## Theme System

### Built-in Themes

```python
from django_cfg.modules.django_unfold import UnfoldTheme, get_unfold_colors

# Available themes
class MyConfig(DjangoConfig):
    unfold_theme: str = "blue"     # blue, green, purple, red, orange, yellow
    unfold_mode: str = "auto"      # light, dark, auto
    
    # Custom colors
    unfold_primary_color: str = "#3b82f6"
    unfold_secondary_color: str = "#64748b"
    unfold_success_color: str = "#10b981"
    unfold_warning_color: str = "#f59e0b"
    unfold_error_color: str = "#ef4444"

# Get theme colors programmatically
colors = get_unfold_colors("blue")
print(colors.primary)  # #3b82f6
print(colors.secondary)  # #64748b
```

### Custom Theme Configuration

```python
from django_cfg.modules.django_unfold.models import UnfoldThemeConfig

class CustomThemeConfig(UnfoldThemeConfig):
    """Custom theme configuration"""
    
    primary_color: str = "#6366f1"
    secondary_color: str = "#8b5cf6"
    accent_color: str = "#06b6d4"
    
    # Typography
    font_family: str = "Inter, system-ui, sans-serif"
    font_size_base: str = "14px"
    
    # Layout
    sidebar_width: str = "280px"
    header_height: str = "64px"
    
    # Animations
    transition_duration: str = "200ms"
    border_radius: str = "8px"

# Apply custom theme
class MyConfig(DjangoConfig):
    unfold_theme_config: CustomThemeConfig = CustomThemeConfig()
```

## Dashboard System

### Dashboard Manager

```python
from django_cfg.modules.django_unfold import DashboardManager, get_dashboard_manager

# Get dashboard manager
dashboard = get_dashboard_manager()

# Add custom dashboard widgets
dashboard.add_stat_card(
    title="Total Users",
    value=lambda: User.objects.count(),
    icon="people",
    color="blue"
)

dashboard.add_stat_card(
    title="Active Sessions",
    value=lambda: Session.objects.filter(expire_date__gt=timezone.now()).count(),
    icon="timeline",
    color="green"
)

dashboard.add_chart_widget(
    title="User Registration Trend",
    chart_type="line",
    data_callback="myapp.callbacks.get_registration_data"
)
```

### Custom Dashboard Callbacks

```python
# callbacks.py
from django_cfg.modules.django_unfold.callbacks import UnfoldCallbacks
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def dashboard_callback(request, context):
    """Custom dashboard callback"""
    
    # Add custom statistics
    context.update({
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count(),
        'new_users_today': User.objects.filter(
            date_joined__gte=timezone.now().date()
        ).count(),
    })
    
    # Add custom widgets
    context['custom_widgets'] = [
        {
            'title': 'System Health',
            'template': 'admin/widgets/system_health.html',
            'data': get_system_health_data()
        },
        {
            'title': 'Recent Activity',
            'template': 'admin/widgets/recent_activity.html',
            'data': get_recent_activity_data()
        }
    ]
    
    return context

def get_system_health_data():
    """Get system health metrics"""
    import psutil
    
    return {
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
    }

def get_recent_activity_data():
    """Get recent user activity"""
    return User.objects.filter(
        last_login__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-last_login')[:10]
```

## 🧭 Navigation System

### Dynamic Navigation

```python
from django_cfg.modules.django_unfold.models import NavigationItem, NavigationSection

class MyConfig(DjangoConfig):
    unfold_navigation: list = [
        NavigationSection(
            title="Content Management",
            items=[
                NavigationItem(
                    title="Posts",
                    icon="article",
                    link="/admin/blog/post/",
                    badge="new"
                ),
                NavigationItem(
                    title="Categories",
                    icon="category",
                    link="/admin/blog/category/"
                ),
            ]
        ),
        NavigationSection(
            title="User Management",
            items=[
                NavigationItem(
                    title="Users",
                    icon="people",
                    link="/admin/auth/user/",
                    permission="auth.view_user"
                ),
                NavigationItem(
                    title="Groups",
                    icon="group",
                    link="/admin/auth/group/",
                    permission="auth.view_group"
                ),
            ]
        ),
        NavigationSection(
            title="Django CFG",
            items=[
                NavigationItem(
                    title="System Monitor",
                    icon="monitor_heart",
                    link="/admin/django_cfg/system/",
                    permission="is_staff"
                ),
                NavigationItem(
                    title="Configuration",
                    icon="settings",
                    link="/admin/constance/config/",
                    permission="is_superuser"
                ),
            ]
        )
    ]
```

### Conditional Navigation

```python
def get_navigation_items(request):
    """Dynamic navigation based on user permissions"""
    items = []
    
    # Always visible items
    items.append(NavigationItem(
        title="Dashboard",
        icon="dashboard",
        link="/admin/"
    ))
    
    # User management (staff only)
    if request.user.is_staff:
        items.append(NavigationSection(
            title="User Management",
            items=[
                NavigationItem(
                    title="Users",
                    icon="people",
                    link="/admin/auth/user/"
                ),
                NavigationItem(
                    title="Activity Log",
                    icon="history",
                    link="/admin/accounts/activity/"
                ),
            ]
        ))
    
    # System administration (superuser only)
    if request.user.is_superuser:
        items.append(NavigationSection(
            title="System",
            items=[
                NavigationItem(
                    title="Configuration",
                    icon="settings",
                    link="/admin/constance/config/"
                ),
                NavigationItem(
                    title="System Monitor",
                    icon="monitor_heart",
                    link="/admin/system/monitor/"
                ),
            ]
        ))
    
    return items

# Use in settings
UNFOLD = {
    "SIDEBAR": {
        "navigation": "myapp.navigation.get_navigation_items",
    }
}
```

## System Monitoring

### System Monitor

```python
from django_cfg.modules.django_unfold import SystemMonitor, get_system_monitor

# Get system monitor
monitor = get_system_monitor()

# Get system metrics
metrics = monitor.get_system_metrics()
print(metrics)
# {
#     'cpu_usage': 45.2,
#     'memory_usage': 62.8,
#     'disk_usage': 78.1,
#     'load_average': 1.23,
#     'uptime': '2 days, 14:32:15',
#     'processes': 156
# }

# Get Django metrics
django_metrics = monitor.get_django_metrics()
print(django_metrics)
# {
#     'active_sessions': 23,
#     'total_users': 1247,
#     'database_connections': 8,
#     'cache_hit_rate': 94.2,
#     'response_time_avg': 120.5
# }
```

### Custom Monitoring Widgets

```python
# admin.py
from django.contrib import admin
from django_cfg.modules.django_unfold import get_system_monitor

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        """Add system monitoring to changelist"""
        extra_context = extra_context or {}
        
        monitor = get_system_monitor()
        extra_context.update({
            'system_metrics': monitor.get_system_metrics(),
            'django_metrics': monitor.get_django_metrics(),
            'custom_metrics': self.get_custom_metrics()
        })
        
        return super().changelist_view(request, extra_context)
    
    def get_custom_metrics(self):
        """Get model-specific metrics"""
        return {
            'total_records': MyModel.objects.count(),
            'active_records': MyModel.objects.filter(is_active=True).count(),
            'recent_records': MyModel.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
```

## Advanced Configuration

### Complete Unfold Configuration

```python
# settings.py
UNFOLD = {
    # Site configuration
    "SITE_TITLE": "Django CFG Admin",
    "SITE_HEADER": "Django CFG Administration",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": "/static/icon-light.svg",
        "dark": "/static/icon-dark.svg",
    },
    "SITE_LOGO": {
        "light": "/static/logo-light.svg",
        "dark": "/static/logo-dark.svg",
    },
    "SITE_SYMBOL": "speed",
    
    # Environment
    "ENVIRONMENT": "django_cfg.core.environment.get_environment_name",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    
    # Theme
    "THEME": "auto",  # light, dark, auto
    "COLORS": {
        "primary": {
            "50": "#eff6ff",
            "100": "#dbeafe", 
            "200": "#bfdbfe",
            "300": "#93c5fd",
            "400": "#60a5fa",
            "500": "#3b82f6",
            "600": "#2563eb",
            "700": "#1d4ed8",
            "800": "#1e40af",
            "900": "#1e3a8a",
        }
    },
    
    # Dashboard
    "DASHBOARD_CALLBACK": "django_cfg.modules.django_unfold.callbacks.dashboard_callback",
    
    # Sidebar
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/auth/user/",
                        "permission": lambda request: request.user.is_staff,
                    },
                ]
            }
        ]
    },
    
    # Tabs
    "TABS": [
        {
            "models": ["auth.user"],
            "items": [
                {
                    "title": "Profile",
                    "link": "/admin/auth/user/{}/change/",
                },
                {
                    "title": "Activity",
                    "link": "/admin/accounts/activity/?user__id__exact={}",
                },
            ]
        }
    ],
    
    # Login page
    "LOGIN": {
        "image": "/static/admin-login.jpg",
        "redirect_after": "/admin/",
    },
    
    # Custom CSS/JS
    "STYLES": [
        lambda request: "/static/css/custom-admin.css",
    ],
    "SCRIPTS": [
        lambda request: "/static/js/custom-admin.js",
    ],
}
```

### Integration with Django-CFG Apps

```python
# Automatic integration with Django-CFG apps
from django_cfg import DjangoConfig, UnfoldConfig

class MyConfig(DjangoConfig):
    unfold: UnfoldConfig | None = UnfoldConfig()
    enable_accounts: bool = True
    enable_support: bool = True
    enable_newsletter: bool = True

    # Unfold will automatically configure navigation for enabled apps
    unfold_auto_navigation: bool = True

    # Custom dashboard widgets for each app
    unfold_dashboard_widgets: dict = {
        'accounts': ['user_stats', 'activity_chart'],
        'support': ['ticket_stats', 'response_time'],
        'newsletter': ['subscriber_stats', 'campaign_performance']
    }
```

## 🧪 Testing Unfold Integration

### Unit Tests

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django_cfg.modules.django_unfold import get_dashboard_manager, get_system_monitor

User = get_user_model()

class UnfoldIntegrationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
    
    def test_dashboard_manager(self):
        """Test dashboard manager functionality"""
        dashboard = get_dashboard_manager()
        
        # Test stat card addition
        dashboard.add_stat_card(
            title="Test Metric",
            value=lambda: 42,
            icon="test",
            color="blue"
        )
        
        stats = dashboard.get_stat_cards()
        self.assertIn("Test Metric", [card['title'] for card in stats])
    
    def test_system_monitor(self):
        """Test system monitoring"""
        monitor = get_system_monitor()
        
        # Test system metrics
        metrics = monitor.get_system_metrics()
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        
        # Test Django metrics
        django_metrics = monitor.get_django_metrics()
        self.assertIn('total_users', django_metrics)
    
    def test_navigation_generation(self):
        """Test navigation generation"""
        request = self.factory.get('/admin/')
        request.user = self.user
        
        from django_cfg.modules.django_unfold.callbacks import get_navigation_items
        navigation = get_navigation_items(request)
        
        self.assertIsInstance(navigation, list)
        self.assertTrue(len(navigation) > 0)
```

## Related Documentation

- [**Configuration Guide**](/fundamentals/configuration) - Unfold configuration
- [**Admin Interface**](/fundamentals/system/utilities) - Admin customization
- [**Theme System**](/fundamentals/system/utilities) - Theming and styling
- [**Dashboard Callbacks**](/fundamentals/system/utilities) - Custom dashboard widgets

The Unfold Admin module provides a beautiful, modern admin interface for your Django applications! 🎨

TAGS: unfold, admin-interface, dashboard, theming, navigation, monitoring
DEPENDS_ON: [configuration, admin, theming]
USED_BY: [all-apps, administration, monitoring]
