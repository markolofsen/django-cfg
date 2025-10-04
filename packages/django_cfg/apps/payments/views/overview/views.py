"""
💰 Payments Overview Dashboard Views

API views for payments dashboard data using existing models.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter

from .services import (
    PaymentsDashboardMetricsService,
    PaymentsUsageChartService,
    RecentPaymentsService,
    PaymentsAnalyticsService,
)
from .serializers import (
    PaymentsDashboardOverviewSerializer,
    PaymentsMetricsSerializer,
    PaymentsChartResponseSerializer,
    TimePeriodSerializer,
    RecentPaymentSerializer,
    RecentTransactionSerializer,
    BalanceOverviewSerializer,
    SubscriptionOverviewSerializer,
    APIKeysOverviewSerializer,
)


@extend_schema_view(
    overview=extend_schema(
        summary="Payments Dashboard Overview",
        description="Get complete payments dashboard overview with metrics, recent payments, and analytics",
        responses={200: PaymentsDashboardOverviewSerializer}
    ),
    metrics=extend_schema(
        summary="Payments Dashboard Metrics",
        description="Get payments dashboard metrics including balance, subscriptions, API keys, and payments",
        responses={200: PaymentsMetricsSerializer}
    ),
    chart_data=extend_schema(
        summary="Payments Chart Data",
        description="Get chart data for payments visualization",
        parameters=[
            OpenApiParameter(
                name='period',
                description='Time period for chart data',
                required=False,
                type=str,
                enum=['7d', '30d', '90d', '1y'],
                default='30d'
            )
        ],
        responses={200: PaymentsChartResponseSerializer}
    ),
    recent_payments=extend_schema(
        summary="Recent Payments",
        description="Get recent payments for the user",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Number of payments to return',
                required=False,
                type=int,
                default=10
            )
        ],
        responses={200: RecentPaymentSerializer(many=True)}
    ),
    recent_transactions=extend_schema(
        summary="Recent Transactions",
        description="Get recent balance transactions for the user",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Number of transactions to return',
                required=False,
                type=int,
                default=10
            )
        ],
        responses={200: RecentTransactionSerializer(many=True)}
    ),
    payment_analytics=extend_schema(
        summary="Payment Analytics",
        description="Get analytics for payments by currency and provider",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Number of analytics items to return',
                required=False,
                type=int,
                default=10
            )
        ],
        responses={200: 'object'}  # Generic object since it's a dict with currency_analytics and provider_analytics
    ),
    balance_overview=extend_schema(
        summary="Balance Overview",
        description="Get user balance overview",
        responses={200: BalanceOverviewSerializer}
    ),
    subscription_overview=extend_schema(
        summary="Subscription Overview",
        description="Get current subscription overview",
        responses={200: SubscriptionOverviewSerializer}
    ),
    api_keys_overview=extend_schema(
        summary="API Keys Overview",
        description="Get API keys overview",
        responses={200: APIKeysOverviewSerializer}
    )
)
class PaymentsDashboardViewSet(viewsets.GenericViewSet):
    """
    Payments dashboard data endpoints
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get complete payments dashboard overview
        """
        # Initialize services
        metrics_service = PaymentsDashboardMetricsService(request.user)
        chart_service = PaymentsUsageChartService(request.user)
        payments_service = RecentPaymentsService(request.user)
        
        # Get all data
        data = {
            'metrics': metrics_service.get_dashboard_metrics(),
            'recent_payments': payments_service.get_recent_payments(limit=10),
            'recent_transactions': payments_service.get_recent_transactions(limit=10),
            'chart_data': chart_service.get_chart_data(period='30d')
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Get payments dashboard metrics only
        """
        service = PaymentsDashboardMetricsService(request.user)
        metrics = service.get_dashboard_metrics()
        return Response(metrics)
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """
        Get payments usage chart data
        """
        period = request.query_params.get('period', '30d')
        
        # Validate period
        serializer = TimePeriodSerializer(data={'period': period})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = PaymentsUsageChartService(request.user)
        data = service.get_chart_data(period)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def recent_payments(self, request):
        """
        Get recent payments
        """
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Max 50 payments
        
        service = RecentPaymentsService(request.user)
        payments = service.get_recent_payments(limit)
        return Response(payments)
    
    @action(detail=False, methods=['get'])
    def recent_transactions(self, request):
        """
        Get recent balance transactions
        """
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Max 50 transactions
        
        service = RecentPaymentsService(request.user)
        transactions = service.get_recent_transactions(limit)
        return Response(transactions)
    
    @action(detail=False, methods=['get'])
    def payment_analytics(self, request):
        """
        Get payment analytics
        """
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 20)  # Max 20 analytics items
        
        service = PaymentsAnalyticsService(request.user)
        analytics = {
            'currency_analytics': service.get_payment_analytics(limit),
            'provider_analytics': service.get_provider_analytics(),
        }
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def balance_overview(self, request):
        """
        Get balance overview only
        """
        service = PaymentsDashboardMetricsService(request.user)
        balance = service.get_balance_overview()
        return Response(balance)
    
    @action(detail=False, methods=['get'])
    def subscription_overview(self, request):
        """
        Get subscription overview only
        """
        service = PaymentsDashboardMetricsService(request.user)
        subscription = service.get_subscription_overview()
        return Response(subscription)
    
    @action(detail=False, methods=['get'])
    def api_keys_overview(self, request):
        """
        Get API keys overview only
        """
        service = PaymentsDashboardMetricsService(request.user)
        api_keys = service.get_api_keys_overview()
        return Response(api_keys)
