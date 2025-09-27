"""
Admin Statistics ViewSets.

DRF ViewSets for comprehensive statistics in admin interface.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta


from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.models import UniversalPayment
from ..base import AdminReadOnlyViewSet
from django_cfg.apps.payments.admin_interface.serializers import AdminPaymentStatsSerializer, WebhookStatsSerializer

logger = get_logger("admin_stats_api")


class AdminStatsViewSet(AdminReadOnlyViewSet):
    """
    Admin ViewSet for comprehensive system statistics.
    
    Provides aggregated statistics across all system components.
    """
    
    # No model - this is for aggregated statistics
    serializer_class = AdminPaymentStatsSerializer
    
    def list(self, request):
        """Get overview statistics."""
        now = timezone.now()
        
        # Payment statistics
        payments_queryset = UniversalPayment.objects.all()
        
        payment_stats = {
            'total_payments': payments_queryset.count(),
            'total_amount_usd': payments_queryset.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0,
            'successful_payments': payments_queryset.filter(status='completed').count(),
            'failed_payments': payments_queryset.filter(status='failed').count(),
            'pending_payments': payments_queryset.filter(status__in=['pending', 'confirming']).count(),
        }
        
        # Calculate success rate
        total = payment_stats['total_payments']
        if total > 0:
            payment_stats['success_rate'] = (payment_stats['successful_payments'] / total) * 100
        else:
            payment_stats['success_rate'] = 0
        
        # Time-based payment stats
        payment_stats['last_24h'] = {
            'count': payments_queryset.filter(created_at__gte=now - timedelta(hours=24)).count(),
            'amount': payments_queryset.filter(created_at__gte=now - timedelta(hours=24)).aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0,
        }
        
        # Mock webhook statistics (replace with real data)
        webhook_stats = {
            'total_events': 156,
            'successful_events': 142,
            'failed_events': 12,
            'pending_events': 2,
            'webhook_success_rate': 91.0,
        }
        
        # System health metrics
        system_stats = {
            'active_users_24h': 45,  # Mock data
            'api_requests_24h': 1250,  # Mock data
            'avg_response_time': 245.5,  # Mock data
            'uptime_percentage': 99.9,  # Mock data
        }
        
        return Response({
            'payments': payment_stats,
            'webhooks': webhook_stats,
            'system': system_stats,
            'last_updated': now.isoformat(),
        })
    
    @action(detail=False, methods=['get'])
    def payments(self, request):
        """Get detailed payment statistics."""
        queryset = UniversalPayment.objects.all()
        now = timezone.now()
        
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
            total_amount=Sum('amount_usd'),
            successful=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed'))
        ):
            provider = provider_data['provider']
            provider_stats[provider] = {
                'count': provider_data['count'],
                'total_amount': provider_data['total_amount'] or 0,
                'successful': provider_data['successful'],
                'failed': provider_data['failed'],
                'success_rate': (provider_data['successful'] / provider_data['count'] * 100) if provider_data['count'] > 0 else 0,
            }
        
        # Currency breakdown
        currency_stats = {}
        for currency_data in queryset.values('currency__code').annotate(
            count=Count('id'),
            total_amount=Sum('amount_usd')
        ):
            currency_stats[currency_data['currency__code']] = {
                'count': currency_data['count'],
                'total_amount': currency_data['total_amount'] or 0,
            }
        
        # Time-based stats
        time_ranges = {
            'last_24h': now - timedelta(hours=24),
            'last_7d': now - timedelta(days=7),
            'last_30d': now - timedelta(days=30),
        }
        
        time_stats = {}
        for period, start_date in time_ranges.items():
            period_queryset = queryset.filter(created_at__gte=start_date)
            time_stats[period] = {
                'count': period_queryset.count(),
                'amount': period_queryset.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0,
                'successful': period_queryset.filter(status='completed').count(),
                'failed': period_queryset.filter(status='failed').count(),
            }
        
        stats_data = {
            'total_payments': total_payments,
            'total_amount_usd': total_amount,
            'successful_payments': successful,
            'failed_payments': failed,
            'pending_payments': pending,
            'success_rate': round(success_rate, 2),
            'by_provider': provider_stats,
            'by_currency': currency_stats,
            **time_stats,
        }
        
        serializer = AdminPaymentStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def webhooks(self, request):
        """Get detailed webhook statistics."""
        # Mock webhook statistics - replace with real data from webhook event model
        stats_data = {
            'total': 156,
            'successful': 142,
            'failed': 12,
            'pending': 2,
            'success_rate': 91.0,
            'providers': {
                'nowpayments': {'total': 89, 'successful': 85, 'failed': 4, 'success_rate': 95.5},
                'stripe': {'total': 45, 'successful': 42, 'failed': 3, 'success_rate': 93.3},
                'cryptapi': {'total': 22, 'successful': 15, 'failed': 5, 'pending': 2, 'success_rate': 68.2},
            },
            'last_24h': {
                'total': 23,
                'successful': 21,
                'failed': 2,
            },
            'avg_response_time': 245.5,
            'max_response_time': 3000,
        }
        
        serializer = WebhookStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def system(self, request):
        """Get system health and performance statistics."""
        # Mock system statistics - replace with real metrics
        system_data = {
            'uptime': '99.9%',
            'active_users_24h': 45,
            'api_requests_24h': 1250,
            'avg_response_time_ms': 245.5,
            'error_rate_24h': 0.8,
            'database_connections': 12,
            'memory_usage': '68%',
            'cpu_usage': '23%',
            'disk_usage': '45%',
        }
        
        return Response(system_data)
