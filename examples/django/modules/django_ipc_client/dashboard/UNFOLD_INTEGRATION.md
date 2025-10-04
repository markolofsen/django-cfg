# Unfold Admin Integration 🎨

Complete guide for integrating RPC Dashboard with django-unfold admin interface.

---

## ✨ Automatic Integration (New in v2.0)

**Zero configuration required!** When you enable RPC, django-cfg automatically adds "Operations" section to Unfold navigation:

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.modules.django_cfg_rpc_client.config import DjangoCfgRPCConfig

class MyConfig(DjangoConfig):
    # Enable RPC module
    django_cfg_rpc = DjangoCfgRPCConfig(
        enabled=True,
        redis_url="redis://localhost:6379/2",
    )
```

**That's it!** Django-cfg automatically creates "Operations" section with:
- ✅ RPC Dashboard (if RPC enabled)
- ✅ Background Tasks (if tasks enabled)
- ✅ Configuration (Constance)
- ✅ Maintenance (if enabled)
- ✅ Health Check

**No URL configuration needed** - URLs are auto-registered via `get_django_cfg_urlpatterns()`

---

## 🎨 Custom Navigation (Advanced)

If you want to customize the navigation, override `unfold` config:

### Option 1: Custom Section Name

```python
from django_cfg import UnfoldConfig, NavigationSection, NavigationItem, Icons

class MyConfig(DjangoConfig):
    django_cfg_rpc = DjangoCfgRPCConfig(enabled=True, redis_url="redis://localhost:6379/2")

    # Override navigation
    unfold = UnfoldConfig(
        site_title="My Admin",
        navigation=[
            NavigationSection(
                title="Monitoring",  # Custom name
                items=[
                    NavigationItem(
                        title="RPC Dashboard",
                        icon=Icons.MONITOR_HEART,
                        link="/admin/rpc/"
                    ),
                ],
            ),
        ],
    )
```

### Option 2: Manual URL Registration (Not Recommended)

If not using django-cfg's automatic URL generation:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/rpc/', include('django_cfg.modules.django_cfg_rpc_client.dashboard.urls')),
]
```

---

## 📍 Navigation Placement

### Option 1: Operations Section (Recommended)

Combine RPC Dashboard with all operational tools for logical grouping:

```python
NavigationSection(
    title="Operations",
    items=[
        NavigationItem(
            title="RPC Dashboard",
            icon=Icons.MONITOR_HEART,
            link="/admin/rpc/"
        ),
        NavigationItem(
            title="Background Tasks",
            icon=Icons.TASK,
            link="admin:django_dramatiq_task_changelist"
        ),
        NavigationItem(
            title="Configuration",
            icon=Icons.SETTINGS,
            link="admin:constance_config_changelist"
        ),
        NavigationItem(
            title="Maintenance",
            icon=Icons.BUILD,
            link="admin:maintenance_cloudflaresite_changelist"
        ),
    ],
)
```

### Option 2: System/Admin Section

```python
NavigationSection(
    title="System",
    items=[
        NavigationItem(title="Configuration", icon=Icons.SETTINGS, link="/admin/constance/config/"),
        NavigationItem(title="RPC Dashboard", icon=Icons.MONITOR_HEART, link="/admin/rpc/"),
        NavigationItem(title="Logs", icon=Icons.DESCRIPTION, link="/admin/logs/"),
    ],
)
```

### Option 3: Integrated with Content

```python
navigation=[
    NavigationSection(
        title="Content",
        items=[
            NavigationItem(title="Posts", icon=Icons.ARTICLE, link="admin:blog_post_changelist"),
        ],
    ),
    NavigationSection(
        title="Tools",
        items=[
            NavigationItem(title="RPC Dashboard", icon=Icons.INSIGHTS, link="/admin/rpc/"),
            NavigationItem(title="Analytics", icon=Icons.ANALYTICS, link="/admin/analytics/"),
        ],
    ),
]
```

---

## 🎨 Icon Options

Material Design icons for RPC Dashboard:

```python
# Health & Monitoring (Recommended)
icon=Icons.MONITOR_HEART      # ❤️ Heart monitor - best for health monitoring
icon=Icons.HEALTH_AND_SAFETY  # 🏥 Health and safety
icon=Icons.MEDICAL_SERVICES   # 🩺 Medical services

# Analytics & Insights
icon=Icons.INSIGHTS           # 💡 Insights - good for analytics
icon=Icons.ANALYTICS          # 📊 Analytics charts
icon=Icons.BAR_CHART          # 📊 Bar chart
icon=Icons.DASHBOARD          # 📋 Dashboard

# Activity & Timeline
icon=Icons.TIMELINE           # 📈 Timeline activity
icon=Icons.HISTORY            # 🕐 History/activity
icon=Icons.UPDATE             # 🔄 Updates

# Communication
icon=Icons.WEBHOOK            # 🔗 Webhooks
icon=Icons.API                # 🔌 API
icon=Icons.CLOUD_SYNC         # ☁️ Cloud sync
```

### Icon Preview

```python
# Health monitoring focus
NavigationItem(title="RPC Monitor", icon=Icons.MONITOR_HEART, link="/admin/rpc/")
# → Best for: Health checks, system monitoring

# Analytics focus
NavigationItem(title="RPC Analytics", icon=Icons.INSIGHTS, link="/admin/rpc/")
# → Best for: Statistics, performance metrics

# Activity focus
NavigationItem(title="RPC Activity", icon=Icons.TIMELINE, link="/admin/rpc/")
# → Best for: Request logs, recent activity

# Technical focus
NavigationItem(title="RPC Dashboard", icon=Icons.API, link="/admin/rpc/")
# → Best for: Developer tools, API monitoring
```

---

## 🔐 Access Control

### Staff-Only Access (Default)

```python
NavigationItem(
    title="RPC Dashboard",
    icon=Icons.MONITOR_HEART,
    link="/admin/rpc/",
    # No permission = staff users only (is_staff=True)
)
```

### Superuser-Only Access

```python
NavigationItem(
    title="RPC Dashboard",
    icon=Icons.MONITOR_HEART,
    link="/admin/rpc/",
    permission=lambda request: request.user.is_superuser
)
```

### Custom Permission Check

```python
NavigationItem(
    title="RPC Dashboard",
    icon=Icons.MONITOR_HEART,
    link="/admin/rpc/",
    permission=lambda request: (
        request.user.is_staff and
        request.user.has_perm('monitoring.view_rpc')
    )
)
```

---

## 🏷️ Badge Support

### Add "New" Badge

```python
NavigationItem(
    title="RPC Dashboard",
    icon=Icons.MONITOR_HEART,
    link="/admin/rpc/",
    badge="new"
)
```

### Dynamic Badge (Alert Count)

```python
def get_rpc_navigation(request):
    from django_cfg.modules.django_cfg_rpc_client.dashboard.monitor import RPCMonitor

    monitor = RPCMonitor()
    health = monitor.health_check()

    # Show badge if Redis is down
    badge = "!" if not health['redis_connected'] else None

    return NavigationItem(
        title="RPC Dashboard",
        icon=Icons.MONITOR_HEART,
        link="/admin/rpc/",
        badge=badge
    )

# Use in navigation
unfold: UnfoldConfig = UnfoldConfig(
    sidebar={
        "navigation": "myapp.navigation.get_rpc_navigation",
    }
)
```

---

## 🎯 Full Example

Complete configuration with all django-cfg features:

```python
# config.py
from django_cfg import (
    DjangoConfig,
    UnfoldConfig,
    NavigationSection,
    NavigationItem,
    Icons,
    DjangoCfgRPCConfig,
    TaskConfig,
    PaymentsConfig,
)

class ProductionConfig(DjangoConfig):
    """Production configuration with monitoring."""

    # === RPC Configuration ===
    django_cfg_rpc: DjangoCfgRPCConfig = DjangoCfgRPCConfig(
        enabled=True,
        redis_url="redis://localhost:6379/2",
        rpc_timeout=30,
    )

    # === Background Tasks ===
    enable_tasks: bool = True

    # === Payments ===
    payments: PaymentsConfig = PaymentsConfig(enabled=True)

    # === Unfold Admin ===
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="Production Admin",
        site_header="Production Dashboard",
        theme='dark',

        navigation=[
            # Dashboard
            NavigationSection(
                title="Dashboard",
                items=[
                    NavigationItem(
                        title="Overview",
                        icon=Icons.DASHBOARD,
                        link="/admin/"
                    ),
                ],
            ),

            # Content Management
            NavigationSection(
                title="Content",
                items=[
                    NavigationItem(title="Posts", icon=Icons.ARTICLE, link="admin:blog_post_changelist"),
                    NavigationItem(title="Pages", icon=Icons.DESCRIPTION, link="admin:pages_page_changelist"),
                ],
            ),

            # E-commerce
            NavigationSection(
                title="E-commerce",
                items=[
                    NavigationItem(title="Products", icon=Icons.INVENTORY, link="admin:shop_product_changelist"),
                    NavigationItem(title="Orders", icon=Icons.SHOPPING_CART, link="admin:shop_order_changelist"),
                    NavigationItem(title="Payments", icon=Icons.PAYMENT, link="admin:payments_payment_changelist"),
                ],
            ),

            # Operations (RPC Dashboard + System Tools)
            NavigationSection(
                title="Operations",
                items=[
                    NavigationItem(
                        title="RPC Dashboard",
                        icon=Icons.MONITOR_HEART,
                        link="/admin/rpc/",
                        permission=lambda request: request.user.is_staff
                    ),
                    NavigationItem(
                        title="Background Tasks",
                        icon=Icons.TASK,
                        link="admin:django_dramatiq_task_changelist",
                        permission=lambda request: request.user.is_staff
                    ),
                    NavigationItem(
                        title="Configuration",
                        icon=Icons.SETTINGS,
                        link="admin:constance_config_changelist",
                        permission=lambda request: request.user.is_staff
                    ),
                    NavigationItem(
                        title="Maintenance",
                        icon=Icons.BUILD,
                        link="admin:maintenance_cloudflaresite_changelist",
                        permission=lambda request: request.user.is_superuser
                    ),
                ],
            ),
        ],
    )
```

---

## 🧪 Testing Integration

### Test Navigation Display

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

class UnfoldNavigationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_user = User.objects.create_user(
            username='staff',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user',
            is_staff=False
        )

    def test_rpc_dashboard_visible_to_staff(self):
        """Test RPC Dashboard appears in navigation for staff users."""
        request = self.factory.get('/admin/')
        request.user = self.staff_user

        # Navigation rendering logic
        # Verify RPC Dashboard link is present

    def test_rpc_dashboard_hidden_from_regular_users(self):
        """Test RPC Dashboard hidden from non-staff users."""
        request = self.factory.get('/admin/')
        request.user = self.regular_user

        # Verify RPC Dashboard link is NOT present
```

---

## 📚 Related Documentation

- [Unfold Admin Guide](/docs/features/modules/unfold/overview.md)
- [RPC Dashboard README](./README.md)
- [Icons Reference](/docs/fundamentals/icons.md)
- [Navigation Configuration](/docs/guides/admin-interface.md)

---

**Last Updated**: 2025-10-03
**Version**: 2.0
**Compatible with**: django-unfold 0.x, django-cfg 2.x
