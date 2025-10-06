"""
DRF Views for Shop app.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, F
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Category, Product, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    OrderListSerializer, OrderDetailSerializer, ShopStatsSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List categories",
        description="Get a list of all shop categories",
        tags=["Shop - Categories"]
    ),
    retrieve=extend_schema(
        summary="Get category",
        description="Get details of a specific category",
        tags=["Shop - Categories"]
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for shop categories."""
    
    queryset = Category.objects.filter(is_active=True).annotate(
        active_products_count=Count('products', filter=Q(products__status='active'))
    ).prefetch_related('children')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'products_count']
    ordering = ['sort_order', 'name']


@extend_schema_view(
    list=extend_schema(
        summary="List products",
        description="Get a paginated list of products",
        tags=["Shop - Products"]
    ),
    retrieve=extend_schema(
        summary="Get product",
        description="Get detailed information about a specific product",
        tags=["Shop - Products"]
    ),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products."""
    
    queryset = Product.objects.filter(status='active').select_related('category')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured', 'is_digital', 'status']
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'views_count', 'sales_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        else:
            return ProductDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to track product views."""
        instance = self.get_object()
        
        # Update views count
        Product.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get featured products",
        description="Get featured products",
        tags=["Shop - Products"]
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products."""
        products = Product.objects.filter(status='active', is_featured=True)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get shop statistics",
        description="Get comprehensive shop statistics",
        responses={200: ShopStatsSerializer},
        tags=["Shop - Products"]
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get shop statistics."""
        stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(status='active').count(),
            'out_of_stock_products': Product.objects.filter(
                status='active', manage_stock=True, stock_quantity=0
            ).count(),
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'total_revenue': Order.objects.filter(
                status__in=['delivered', 'shipped']
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'popular_products': Product.objects.filter(status='active').order_by('-sales_count')[:5],
            # Note: 'customer' removed from select_related for multi-database compatibility
            'recent_orders': Order.objects.order_by('-created_at')[:5]
        }
        
        serializer = ShopStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List orders",
        description="Get a list of orders (admin only)",
        tags=["Shop - Orders"]
    ),
    retrieve=extend_schema(
        summary="Get order",
        description="Get details of a specific order",
        tags=["Shop - Orders"]
    ),
)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for orders."""
    
    # Note: 'customer' removed from select_related for multi-database compatibility
    # Customer (User) is in 'default' DB, Order is in 'shop_db' - SQLite can't JOIN across DBs
    queryset = Order.objects.prefetch_related('items__product')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['order_number', 'customer__username', 'customer__email']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        else:
            return OrderDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Regular users can only see their own orders
        if not self.request.user.is_staff:
            queryset = queryset.filter(customer=self.request.user)
        
        return queryset
