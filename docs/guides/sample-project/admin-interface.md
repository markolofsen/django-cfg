---
title: Admin Interface
description: Modern admin interface with Unfold theme and custom dashboards in Django-CFG
sidebar_label: Admin Interface
sidebar_position: 5
---

# Admin Interface

The Django-CFG sample project showcases a modern, customizable admin interface built on the Unfold theme. This guide covers admin customization, dashboard widgets, and navigation configuration.

## Unfold Theme Integration

The sample project uses the Unfold theme for a modern, Material Design-inspired admin interface.

### Theme Configuration

Configure the theme in `api/config.py`:

```python
from django_cfg import UnfoldConfig

unfold: UnfoldConfig = UnfoldConfig(
    site_title="Django-CFG Sample Admin",
    site_header="Django-CFG Sample",
    site_url="/",
    site_icon={
        "light": "/static/icon-light.svg",
        "dark": "/static/icon-dark.svg",
    },
    dashboard_callback="api.config.dashboard_callback",
    navigation=[...],  # Navigation structure
    colors={
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "196 181 253",
            "400": "147 51 234",
            "500": "124 58 237",
            "600": "109 40 217",
        }
    }
)
```

### Theme Options

#### Basic Settings

```python
UnfoldConfig(
    site_title="My Admin",           # Browser tab title
    site_header="My Site Admin",     # Admin header text
    site_url="/",                     # Logo link URL
    index_title="Dashboard",          # Index page title
)
```

#### Branding

```python
UnfoldConfig(
    site_icon={
        "light": "/static/icon-light.svg",  # Light mode icon
        "dark": "/static/icon-dark.svg",     # Dark mode icon
    },
    site_logo={
        "light": "/static/logo-light.svg",   # Light mode logo
        "dark": "/static/logo-dark.svg",     # Dark mode logo
    },
)
```

#### Colors

Customize the color scheme:

```python
UnfoldConfig(
    colors={
        "primary": {
            "50": "250 245 255",   # Lightest
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "196 181 253",
            "400": "147 51 234",
            "500": "124 58 237",   # Base color
            "600": "109 40 217",   # Darkest
        }
    }
)
```

## Navigation Structure

### Custom Navigation

Define a custom navigation menu:

```python
unfold: UnfoldConfig = UnfoldConfig(
    navigation=[
        {
            "title": "Dashboard",
            "separator": True,
            "items": [
                {
                    "title": "Overview",
                    "icon": "dashboard",
                    "link": "/admin/",
                },
            ]
        },
        {
            "title": "Content Management",
            "separator": True,
            "items": [
                {
                    "title": "Blog Posts",
                    "icon": "article",
                    "link": "/admin/blog/post/",
                },
                {
                    "title": "Comments",
                    "icon": "comment",
                    "link": "/admin/blog/comment/",
                },
            ]
        },
        {
            "title": "E-Commerce",
            "separator": True,
            "items": [
                {
                    "title": "Products",
                    "icon": "inventory",
                    "link": "/admin/shop/product/",
                },
                {
                    "title": "Orders",
                    "icon": "shopping_cart",
                    "link": "/admin/shop/order/",
                },
            ]
        },
        {
            "title": "User Management",
            "separator": True,
            "items": [
                {
                    "title": "Users",
                    "icon": "people",
                    "link": "/admin/auth/user/",
                },
                {
                    "title": "Profiles",
                    "icon": "account_circle",
                    "link": "/admin/profiles/profile/",
                },
            ]
        }
    ]
)
```

### Navigation Options

#### Separators

Add visual separators between sections:

```python
{
    "title": "Section Name",
    "separator": True,  # Adds separator above section
    "items": [...]
}
```

#### Icons

Use Material Design icons:

```python
{
    "title": "Dashboard",
    "icon": "dashboard",  # Material icon name
    "link": "/admin/",
}
```

Common icons:
- `dashboard` - Dashboard/overview
- `article` - Blog posts/content
- `inventory` - Products/items
- `shopping_cart` - Orders/cart
- `people` - Users
- `settings` - Settings
- `analytics` - Analytics/reports

#### Collapsible Sections

Create expandable sections:

```python
{
    "title": "Reports",
    "collapsible": True,
    "items": [
        {"title": "Sales Report", "link": "/admin/reports/sales/"},
        {"title": "User Report", "link": "/admin/reports/users/"},
    ]
}
```

## Custom Dashboard

### Dashboard Callback

Create dynamic dashboard widgets:

```python
# api/config.py

def dashboard_callback(request, context):
    """Custom dashboard with real-time metrics."""
    from apps.blog.models import Post
    from apps.shop.models import Product, Order
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta

    User = get_user_model()

    # Calculate metrics
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_products = Product.objects.count()
    recent_orders = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # Add custom cards to dashboard
    custom_cards = [
        {
            "title": "Total Users",
            "value": str(total_users),
            "description": "Registered users",
            "icon": "people"
        },
        {
            "title": "Blog Posts",
            "value": str(total_posts),
            "description": "Published articles",
            "icon": "article"
        },
        {
            "title": "Products",
            "value": str(total_products),
            "description": "Available products",
            "icon": "inventory"
        },
        {
            "title": "Orders (7d)",
            "value": str(recent_orders),
            "description": "Recent orders",
            "icon": "shopping_cart"
        }
    ]

    context["cards"].extend(custom_cards)
    return context
```

### Enhanced Dashboard with Charts

Add more sophisticated metrics:

```python
def dashboard_callback(request, context):
    """Enhanced dashboard with charts and metrics."""
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta, date

    # Time periods
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # User metrics
    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()

    # Content metrics
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()

    # E-commerce metrics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    revenue_month = Order.objects.filter(
        created_at__gte=month_ago
    ).aggregate(Sum('total'))['total__sum'] or 0

    # Add metrics cards
    context["cards"].extend([
        {
            "title": "Total Users",
            "value": f"{total_users:,}",
            "description": f"+{new_users_week} this week",
            "icon": "people",
            "color": "primary"
        },
        {
            "title": "Blog Posts",
            "value": f"{published_posts}/{total_posts}",
            "description": "Published/Total",
            "icon": "article",
            "color": "success"
        },
        {
            "title": "Products",
            "value": f"{total_products:,}",
            "description": "Available products",
            "icon": "inventory",
            "color": "info"
        },
        {
            "title": "Revenue (30d)",
            "value": f"${revenue_month:,.2f}",
            "description": "Monthly revenue",
            "icon": "attach_money",
            "color": "warning"
        }
    ])

    return context
```

### Widget Colors

Customize widget appearance:

```python
{
    "title": "Active Users",
    "value": "1,234",
    "color": "primary",   # primary, success, warning, danger, info
    "icon": "people",
    "description": "Last 30 days"
}
```

Available colors:
- `primary` - Purple (default theme color)
- `success` - Green
- `warning` - Orange
- `danger` - Red
- `info` - Blue

## Model Admin Customization

### Basic Admin Registration

```python
# apps/blog/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'status')
        }),
        ('Metadata', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
```

### List Display Customization

```python
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        'id',
        'user_email',
        'total_amount',
        'status_badge',
        'created_at'
    ]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Customer'

    def total_amount(self, obj):
        return f"${obj.total:,.2f}"
    total_amount.short_description = 'Total'

    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return f'<span class="badge badge-{colors[obj.status]}">{obj.status}</span>'
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True
```

### Inline Editing

```python
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [OrderItemInline]
```

### Actions

Add custom bulk actions:

```python
@admin.register(Post)
class PostAdmin(ModelAdmin):
    actions = ['publish_posts', 'unpublish_posts']

    def publish_posts(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(
            request,
            f'{updated} post(s) published successfully.'
        )
    publish_posts.short_description = 'Publish selected posts'

    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(
            request,
            f'{updated} post(s) unpublished.'
        )
    unpublish_posts.short_description = 'Unpublish selected posts'
```

## Advanced Features

### Tabbed Interface

Organize fields in tabs:

```python
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'tax_rate')
        }),
        ('Inventory', {
            'fields': ('stock', 'reorder_level', 'supplier')
        }),
        ('Media', {
            'fields': ('image', 'gallery')
        }),
    )
```

### Filters

Add sidebar filters:

```python
@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_filter = [
        'status',
        'created_at',
        ('author', admin.RelatedFieldListFilter),
    ]
```

### Search

Configure search functionality:

```python
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    search_fields = [
        'name',
        'description',
        'sku',
        'category__name'
    ]
```

### Autocomplete

Enable autocomplete for foreign keys:

```python
@admin.register(Post)
class PostAdmin(ModelAdmin):
    autocomplete_fields = ['author', 'category']

@admin.register(User)
class UserAdmin(ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name']
```

## Sidebar Configuration

### Sidebar Settings

```python
UnfoldConfig(
    sidebar={
        "show_search": True,              # Enable search box
        "show_all_applications": False,   # Hide ungrouped apps
        "navigation": [...],               # Custom navigation
    }
)
```

### Search Box

Enable global search in sidebar:

```python
sidebar={
    "show_search": True,
}
```

Users can search for:
- Model names
- Navigation items
- Recent actions

## Accessing the Admin

### Login

Visit `http://127.0.0.1:8000/admin/` and login with:
- **Email**: `admin@example.com`
- **Password**: `admin123`

### Creating Superuser

Create additional admin users:

```bash
# Interactive prompt
python manage.py createsuperuser

# With credentials
python manage.py createsuperuser \
  --email admin@example.com \
  --noinput
```

### Permissions

Control admin access:

```python
@admin.register(Post)
class PostAdmin(ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete
        return request.user.is_superuser

    def get_queryset(self, request):
        # Users only see their own posts
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
```

## Best Practices

### 1. Organize Navigation Logically

Group related items together:

```python
# ✅ Good: Logical grouping
navigation=[
    {"title": "Content", "items": [...]},
    {"title": "E-Commerce", "items": [...]},
    {"title": "Users", "items": [...]},
]

# ❌ Bad: Random order
navigation=[
    {"title": "Orders", ...},
    {"title": "Posts", ...},
    {"title": "Products", ...},
]
```

### 2. Use Meaningful Dashboard Metrics

Show actionable business metrics:

```python
# ✅ Good: Actionable metrics
{
    "title": "Orders Today",
    "value": "23",
    "description": "+12% vs yesterday"
}

# ❌ Bad: Meaningless numbers
{
    "title": "Database Records",
    "value": "1,234,567"
}
```

### 3. Customize List Displays

Make lists informative and scannable:

```python
# ✅ Good: Relevant information
list_display = ['title', 'author', 'status', 'views', 'created_at']

# ❌ Bad: Too much or too little
list_display = ['id']
```

### 4. Add Helpful Actions

Provide bulk operations:

```python
# ✅ Good: Common operations
actions = ['publish_posts', 'archive_posts', 'export_csv']

# ❌ Bad: Only default delete action
```

## Related Topics

- [Configuration](./configuration) - Unfold configuration details
- [Authentication](./authentication) - User authentication setup
- [Project Structure](./project-structure) - Admin file organization

A well-designed admin interface improves productivity and user experience!
