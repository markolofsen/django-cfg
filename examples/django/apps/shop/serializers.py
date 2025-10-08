"""
DRF Serializers for Shop app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem
from typing import Any, Dict, List

User = get_user_model()


class ShopCategorySerializer(serializers.ModelSerializer):
    """Serializer for shop categories."""
    
    products_count = serializers.IntegerField(read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'parent', 'meta_title', 'meta_description',
            'products_count', 'children', 'is_active',
            'sort_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'products_count', 'created_at', 'updated_at']
    
    def get_children(self, obj) -> List[Dict[str, Any]]:
        if obj.children.filter(is_active=True).exists():
            return ShopCategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view."""

    category = ShopCategorySerializer(read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'sale_price',
            'current_price', 'is_on_sale', 'discount_percentage',
            'category', 'image', 'status', 'is_featured', 'is_digital',
            'stock_quantity', 'is_in_stock', 'views_count', 'sales_count',
            'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view."""

    category = ShopCategorySerializer(read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'sale_price', 'current_price', 'is_on_sale', 'discount_percentage',
            'sku', 'stock_quantity', 'manage_stock', 'is_in_stock',
            'category', 'image', 'status', 'is_featured', 'is_digital',
            'meta_title', 'meta_description', 'views_count', 'sales_count',
            'weight', 'length', 'width', 'height',
            'created_at', 'updated_at'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'quantity', 'unit_price', 'total_price',
            'product_name', 'product_sku', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'product_name', 'product_sku', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view."""
    
    customer = serializers.StringRelatedField(read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'status',
            'subtotal', 'total_amount', 'items_count',
            'created_at', 'updated_at'
        ]
    
    def get_items_count(self, obj) -> int:
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for order detail view."""
    
    customer = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'status',
            'subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount',
            'billing_address', 'shipping_address',
            'customer_notes', 'admin_notes',
            'items', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]


class ShopStatsSerializer(serializers.Serializer):
    """Serializer for shop statistics."""
    
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    popular_products = ProductListSerializer(many=True)
    recent_orders = OrderListSerializer(many=True)
