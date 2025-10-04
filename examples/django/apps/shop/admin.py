"""
Admin configuration for Shop app using django-cfg admin system.
"""

from django.contrib import admin
from django.db.models import Count, Sum
from unfold.admin import ModelAdmin, TabularInline
from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    MoneyDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action,
)

from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for shop categories with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['parent']

    # List configuration
    list_display = [
        'name_display',
        'parent_display',
        'products_count_display',
        'active_display',
        'sort_order',
        'created_display'
    ]
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['products_count', 'created_at', 'updated_at']
    list_editable = ['sort_order']

    # Autocomplete
    autocomplete_fields = ['parent']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image', 'parent')
        }),
        ('Settings', {
            'fields': ('is_active', 'sort_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('products_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @display(description="Category", ordering="name")
    def name_display(self, obj):
        """Display category name."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=obj.name,
            variant="info",
            config=StatusBadgeConfig(show_icons=False)
        )

    @display(description="Parent")
    def parent_display(self, obj):
        """Display parent category."""
        return obj.parent.name if obj.parent else "—"

    @display(description="Products")
    def products_count_display(self, obj):
        """Display products count."""
        return self.display_count_simple(obj, 'products_count', 'products')

    @display(description="Status", label=True)
    def active_display(self, obj):
        """Display active status."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        if obj.is_active:
            return StatusBadge.create(text="Active", variant="success")
        return StatusBadge.create(text="Inactive", variant="secondary")

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')

    # Actions
    @action(description="Activate categories", variant=ActionVariant.SUCCESS)
    def activate_categories(self, request, queryset):
        """Activate selected categories."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} categories.")

    @action(description="Deactivate categories", variant=ActionVariant.WARNING)
    def deactivate_categories(self, request, queryset):
        """Deactivate selected categories."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} categories.")


@admin.register(Product)
class ProductAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for products with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['category']

    # List configuration
    list_display = [
        'name_display',
        'sku_display',
        'category_display',
        'price_display',
        'sale_price_display',
        'stock_display',
        'status_display',
        'featured_display',
        'stats_display'
    ]
    list_filter = ['status', 'is_featured', 'is_digital', 'category', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'sales_count', 'created_at', 'updated_at']

    # Autocomplete
    autocomplete_fields = ['category']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'manage_stock')
        }),
        ('Classification', {
            'fields': ('category',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'is_digital')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Physical Properties', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'sales_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Status configuration
    PRODUCT_STATUS_CONFIG = StatusBadgeConfig(
        custom_mappings={
            'draft': 'secondary',
            'active': 'success',
            'inactive': 'warning',
            'out_of_stock': 'danger'
        },
        show_icons=True
    )

    # Money configuration
    MONEY_CONFIG = MoneyDisplayConfig(
        currency="USD",
        show_sign=True,
        thousand_separator=True,
        decimal_places=2
    )

    @display(description="Product", ordering="name")
    def name_display(self, obj):
        """Display product name."""
        return obj.name

    @display(description="SKU")
    def sku_display(self, obj):
        """Display SKU as badge."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=obj.sku,
            variant="primary",
            config=StatusBadgeConfig(show_icons=False)
        )

    @display(description="Category")
    def category_display(self, obj):
        """Display category."""
        if not obj.category:
            return "—"
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(text=obj.category.name, variant="info")

    @display(description="Price")
    def price_display(self, obj):
        """Display price."""
        return self.display_money_amount(obj, 'price', self.MONEY_CONFIG)

    @display(description="Sale Price")
    def sale_price_display(self, obj):
        """Display sale price."""
        if not obj.sale_price:
            return "—"
        return self.display_money_amount(obj, 'sale_price', self.MONEY_CONFIG)

    @display(description="Stock")
    def stock_display(self, obj):
        """Display stock quantity."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        if obj.stock_quantity <= 0:
            variant = "danger"
        elif obj.stock_quantity < 10:
            variant = "warning"
        else:
            variant = "success"
        return StatusBadge.create(text=str(obj.stock_quantity), variant=variant)

    @display(description="Status", label=True)
    def status_display(self, obj):
        """Display product status."""
        return self.display_status_auto(obj, 'status', self.PRODUCT_STATUS_CONFIG)

    @display(description="Featured")
    def featured_display(self, obj):
        """Display featured status."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        if obj.is_featured:
            return StatusBadge.create(text="★ Featured", variant="warning")
        return "—"

    @display(description="Stats")
    def stats_display(self, obj):
        """Display statistics."""
        from django.utils.html import format_html
        return format_html(
            '<small>👁 {} | 🛒 {}</small>',
            obj.views_count,
            obj.sales_count
        )

    # Actions
    @action(description="Mark as active", variant=ActionVariant.SUCCESS)
    def mark_active(self, request, queryset):
        """Mark products as active."""
        updated = queryset.update(status='active')
        self.message_user(request, f"Marked {updated} products as active.")

    @action(description="Mark as out of stock", variant=ActionVariant.DANGER)
    def mark_out_of_stock(self, request, queryset):
        """Mark products as out of stock."""
        updated = queryset.update(status='out_of_stock', stock_quantity=0)
        self.message_user(request, f"Marked {updated} products as out of stock.")

    @action(description="Feature products", variant=ActionVariant.INFO)
    def feature_products(self, request, queryset):
        """Mark products as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Marked {updated} products as featured.")


class OrderItemInline(TabularInline):
    """Inline for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'product_name', 'product_sku', 'created_at']
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'product_name', 'product_sku']


@admin.register(Order)
class OrderAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for orders with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['customer']
    annotations = {
        'items_count': Count('items')
    }

    # List configuration
    list_display = [
        'order_number_display',
        'customer_display',
        'status_display',
        'items_count_display',
        'total_display',
        'created_display'
    ]
    list_filter = ['status', 'created_at', 'shipped_at', 'delivered_at']
    search_fields = ['order_number', 'customer__username', 'customer__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    # Autocomplete
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        ('Addresses', {
            'fields': ('billing_address', 'shipping_address')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

    # Status configuration
    ORDER_STATUS_CONFIG = StatusBadgeConfig(
        custom_mappings={
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary'
        },
        show_icons=True
    )

    # Money configuration
    MONEY_CONFIG = MoneyDisplayConfig(
        currency="USD",
        show_sign=True,
        thousand_separator=True,
        decimal_places=2
    )

    @display(description="Order #", ordering="order_number")
    def order_number_display(self, obj):
        """Display order number."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=f"#{obj.order_number}",
            variant="info",
            config=StatusBadgeConfig(show_icons=False)
        )

    @display(description="Customer", header=True)
    def customer_display(self, obj):
        """Display customer with avatar."""
        return self.display_user_with_avatar(obj, 'customer')

    @display(description="Status", label=True)
    def status_display(self, obj):
        """Display order status."""
        return self.display_status_auto(obj, 'status', self.ORDER_STATUS_CONFIG)

    @display(description="Items")
    def items_count_display(self, obj):
        """Display items count."""
        return self.display_count_simple(obj, 'items_count', 'items')

    @display(description="Total")
    def total_display(self, obj):
        """Display total amount."""
        return self.display_money_amount(obj, 'total_amount', self.MONEY_CONFIG)

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')

    # Actions
    @action(description="Mark as processing", variant=ActionVariant.INFO)
    def mark_processing(self, request, queryset):
        """Mark orders as processing."""
        updated = queryset.update(status='processing')
        self.message_user(request, f"Marked {updated} orders as processing.")

    @action(description="Mark as shipped", variant=ActionVariant.PRIMARY)
    def mark_shipped(self, request, queryset):
        """Mark orders as shipped."""
        from django.utils import timezone
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f"Marked {updated} orders as shipped.")

    @action(description="Mark as delivered", variant=ActionVariant.SUCCESS)
    def mark_delivered(self, request, queryset):
        """Mark orders as delivered."""
        from django.utils import timezone
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f"Marked {updated} orders as delivered.")

    @action(description="Cancel orders", variant=ActionVariant.DANGER)
    def cancel_orders(self, request, queryset):
        """Cancel selected orders."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"Cancelled {updated} orders.")
