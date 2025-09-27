"""
Admin Payment ViewSets.

DRF ViewSets for payment management in admin interface.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from django_cfg.apps.payments.admin_interface.views.base import AdminBaseViewSet
from django_cfg.apps.payments.models import UniversalPayment
from django_cfg.apps.payments.admin_interface.serializers import (
    AdminPaymentListSerializer,
    AdminPaymentDetailSerializer,
    AdminPaymentCreateSerializer,
    AdminPaymentUpdateSerializer,
    AdminPaymentStatsSerializer,
)
from django_cfg.modules.django_logger import get_logger

logger = get_logger("admin_payment_api")


class AdminPaymentViewSet(AdminBaseViewSet):
    """
    Admin ViewSet for payment management.
    
    Provides full CRUD operations for payments with admin-specific features.
    """
    
    queryset = UniversalPayment.objects.select_related('user').order_by('-created_at')
    serializer_class = AdminPaymentDetailSerializer
    
    serializer_classes = {
        'list': AdminPaymentListSerializer,
        'create': AdminPaymentCreateSerializer,
        'update': AdminPaymentUpdateSerializer,
        'partial_update': AdminPaymentUpdateSerializer,
        'stats': AdminPaymentStatsSerializer,
    }
    
    filterset_fields = ['status', 'provider', 'currency__code', 'user']
    search_fields = ['internal_payment_id', 'transaction_hash', 'description', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'amount_usd', 'status']
    
    def get_queryset(self):
        """Optimized queryset for admin interface."""
        queryset = super().get_queryset()
        
        # Add filters based on query params
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        provider_filter = self.request.query_params.get('provider')
        if provider_filter:
            queryset = queryset.filter(provider=provider_filter)
        
        # Date range filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive payment statistics."""
        queryset = self.get_queryset()
        
        # Basic stats
        total_payments = queryset.count()
        total_amount = queryset.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
        
        # Status breakdown
        status_stats = queryset.values('status').annotate(count=Count('id'))
        successful = sum(s['count'] for s in status_stats if s['status'] in ['completed', 'confirmed'])
        failed = sum(s['count'] for s in status_stats if s['status'] == 'failed')
        pending = sum(s['count'] for s in status_stats if s['status'] in ['pending', 'confirming'])
        
        success_rate = (successful / total_payments * 100) if total_payments > 0 else 0
        
        # Provider breakdown
        provider_stats = {}
        for provider_data in queryset.values('provider').annotate(
            count=Count('id'),
            total_amount=Sum('amount_usd')
        ):
            provider_stats[provider_data['provider']] = {
                'count': provider_data['count'],
                'total_amount': provider_data['total_amount'] or 0,
            }
        
        # Currency breakdown
        currency_stats = {}
        for currency_data in queryset.values('currency_code').annotate(
            count=Count('id'),
            total_amount=Sum('amount_usd')
        ):
            currency_stats[currency_data['currency_code']] = {
                'count': currency_data['count'],
                'total_amount': currency_data['total_amount'] or 0,
            }
        
        # Time-based stats
        now = timezone.now()
        last_24h = queryset.filter(created_at__gte=now - timedelta(hours=24)).aggregate(
            count=Count('id'),
            amount=Sum('amount_usd')
        )
        last_7d = queryset.filter(created_at__gte=now - timedelta(days=7)).aggregate(
            count=Count('id'),
            amount=Sum('amount_usd')
        )
        last_30d = queryset.filter(created_at__gte=now - timedelta(days=30)).aggregate(
            count=Count('id'),
            amount=Sum('amount_usd')
        )
        
        stats_data = {
            'total_payments': total_payments,
            'total_amount_usd': total_amount,
            'successful_payments': successful,
            'failed_payments': failed,
            'pending_payments': pending,
            'success_rate': round(success_rate, 2),
            'by_provider': provider_stats,
            'by_currency': currency_stats,
            'last_24h': {
                'count': last_24h['count'] or 0,
                'amount': last_24h['amount'] or 0,
            },
            'last_7d': {
                'count': last_7d['count'] or 0,
                'amount': last_7d['amount'] or 0,
            },
            'last_30d': {
                'count': last_30d['count'] or 0,
                'amount': last_30d['amount'] or 0,
            },
        }
        
        serializer = self.get_serializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a payment."""
        payment = self.get_object()
        
        if payment.status not in ['pending', 'confirming']:
            return Response(
                {'error': 'Payment cannot be cancelled in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = UniversalPayment.PaymentStatus.CANCELLED
        payment.save()
        
        logger.info(f"Payment {payment.id} cancelled by admin {request.user.id}")
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a payment."""
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = UniversalPayment.PaymentStatus.REFUNDED
        payment.save()
        
        logger.info(f"Payment {payment.id} refunded by admin {request.user.id}")
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
