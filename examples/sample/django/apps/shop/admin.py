"""
Admin configuration for Shop app.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin for shop categories."""
    
    list_display = ['name', 'parent', 'products_count', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['products_count', 'created_at', 'updated_at']
    list_editable = ['is_active', 'sort_order']
    
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


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """Admin for products."""
    
    list_display = ['name', 'sku', 'category', 'price', 'sale_price', 'stock_quantity', 'status', 'is_featured']
    list_filter = ['status', 'is_featured', 'is_digital', 'category', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'sales_count', 'created_at', 'updated_at']
    list_editable = ['price', 'sale_price', 'stock_quantity', 'status', 'is_featured']
    
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


class OrderItemInline(TabularInline):
    """Inline for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'product_name', 'product_sku', 'created_at']
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'product_name', 'product_sku']


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """Admin for orders."""
    
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'shipped_at', 'delivered_at']
    search_fields = ['order_number', 'customer__username', 'customer__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    
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
