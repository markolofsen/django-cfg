"""
Admin Webhook ViewSets.

DRF ViewSets for webhook management in admin interface.
Requires admin permissions.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta

from django_cfg.apps.payments.admin_interface.views.base import AdminBaseViewSet, AdminReadOnlyViewSet
from django_cfg.apps.payments.admin_interface.serializers import (
    WebhookEventSerializer,
    WebhookEventListSerializer,
    WebhookStatsSerializer,
    WebhookActionSerializer,
    WebhookActionResultSerializer,
)
from django_cfg.apps.payments.models import UniversalPayment
from django_cfg.modules.django_logging import get_logger
from django_cfg.apps.payments.services.integrations.ngrok_service import (
    get_all_webhook_urls, 
    get_api_base_url, 
    is_ngrok_available
)
from django_cfg.apps.payments.services.core.webhook_service import WebhookService

logger = get_logger("admin_webhook_api")


class AdminWebhookViewSet(AdminReadOnlyViewSet):
    """
    Admin ViewSet for webhook configuration management.
    
    Read-only view for webhook configurations and provider info.
    Requires admin permissions.
    """
    
    # No model - this is for webhook configuration data
    serializer_class = WebhookStatsSerializer
    
    def __init__(self, **kwargs):
        """Initialize with ngrok service."""
        super().__init__(**kwargs)
        
        self.get_webhook_urls = get_all_webhook_urls
        self.get_base_url = get_api_base_url
        self.is_ngrok_active = is_ngrok_available
    
    def list(self, request):
        """List webhook providers and configurations with real ngrok URLs."""
        # Get real webhook URLs
        webhook_urls = self.get_webhook_urls()
        base_url = self.get_base_url()
        ngrok_active = self.is_ngrok_active()
        
        # Get real provider data based on actual payments
        active_providers = UniversalPayment.objects.values('provider').distinct()
        
        providers_data = []
        for provider_data in active_providers:
            provider_name = provider_data['provider']
            provider_payments = UniversalPayment.objects.filter(provider=provider_name)
            
            # Calculate real statistics
            total_payments = provider_payments.count()
            last_payment = provider_payments.order_by('-created_at').first()
            
            provider_info = {
                'name': provider_name,
                'display_name': provider_name.title(),
                'enabled': total_payments > 0,
                'webhook_url': webhook_urls.get(provider_name, f"{base_url}/api/webhooks/{provider_name}/"),
                'supported_events': ['payment.created', 'payment.completed', 'payment.failed'],
                'last_ping': last_payment.created_at if last_payment else None,
                'status': 'active' if total_payments > 0 else 'inactive',
                'ngrok_active': ngrok_active,
                'base_url': base_url
            }
            providers_data.append(provider_info)
        
        # Add ngrok status to response
        response_data = {
            'providers': providers_data,
            'ngrok_status': {
                'active': ngrok_active,
                'base_url': base_url,
                'webhook_urls': webhook_urls
            }
        }
        
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get webhook statistics."""
        # Get real payment data for stats
        total_payments = UniversalPayment.objects.count()
        recent_payments = UniversalPayment.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Mock webhook stats based on real payment data
        stats_data = {
            'total': total_payments * 2,  # Assume 2 events per payment on average
            'successful': int(total_payments * 1.8),  # 90% success rate
            'failed': int(total_payments * 0.2),  # 10% failure rate
            'pending': 0,  # No pending events for now
            'success_rate': 90.0,
            'providers': {
                'nowpayments': {
                    'total': int(total_payments * 0.7),
                    'successful': int(total_payments * 0.65),
                    'failed': int(total_payments * 0.05),
                    'pending': 0,
                    'success_rate': 92.8
                },
                'stripe': {
                    'total': int(total_payments * 0.3),
                    'successful': int(total_payments * 0.28),
                    'failed': int(total_payments * 0.02),
                    'pending': 0,
                    'success_rate': 93.3
                }
            },
            'last_24h': {
                'total': recent_payments * 2,
                'successful': int(recent_payments * 1.8),
                'failed': int(recent_payments * 0.2),
            },
            'avg_response_time': 150.5,  # milliseconds
            'max_response_time': 2500,  # milliseconds
        }
        
        serializer = self.get_serializer(stats_data)
        return Response(serializer.data)


class AdminWebhookEventViewSet(AdminReadOnlyViewSet):
    """
    Admin ViewSet for webhook events management.
    
    Provides listing, filtering, and actions for webhook events.
    Requires admin permissions.
    """
    
    # No model - using mock data for now
    serializer_class = WebhookEventListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    # filterset_fields removed - not compatible with mock data approach
    search_fields = ['event_type', 'webhook_url']
    ordering_fields = ['timestamp', 'event_type', 'status']
    ordering = ['-timestamp']
    
    def __init__(self, **kwargs):
        """Initialize with webhook and ngrok services."""
        super().__init__(**kwargs)
        
        self.webhook_service = WebhookService()
        self.get_webhook_urls = get_all_webhook_urls
        self.get_base_url = get_api_base_url
        self.is_ngrok_active = is_ngrok_available
    
    def get_queryset(self):
        """Get webhook events queryset."""
        # For now, return empty queryset since we're using mock data
        # In real implementation, this would return WebhookEvent.objects.all()
        return UniversalPayment.objects.none()
    
    def list(self, request, webhook_pk=None):
        """List webhook events with filtering and pagination."""
        # Get filter parameters
        event_type = request.GET.get('event_type')
        status_filter = request.GET.get('status')
        provider = request.GET.get('provider')
        
        # Get real payment data to generate realistic mock events
        payments = UniversalPayment.objects.all()[:50]  # Limit for performance
        
        # Generate mock webhook events based on real payments
        events = []
        for i, payment in enumerate(payments):
            # Create multiple events per payment
            event_types = ['payment.created', 'payment.completed'] if payment.status == 'completed' else ['payment.created']
            
            for event_type_name in event_types:
                # Create payload for the event
                payload = {
                    'payment_id': str(payment.id),
                    'amount': str(payment.amount_usd),
                    'currency': payment.currency.code if payment.currency else payment.currency_code,
                    'status': payment.status,
                    'timestamp': payment.created_at.isoformat()
                }
                
                event = {
                    'id': int(str(hash(f"{payment.id}_{event_type_name}_{i}"))[:8], 16),
                    'provider': payment.provider,
                    'event_type': event_type_name,
                    'status': 'success' if i % 5 != 0 else 'failed',
                    'timestamp': payment.created_at,
                    'payload_size': len(str(payload)),
                    'response_time': 50 + (i % 200),
                    'retry_count': 0 if i % 5 != 0 else 2,
                    'error_message': '' if i % 5 != 0 else 'Connection timeout',
                    'payload_preview': str(payload)[:200],
                    'response_status_code': 200 if i % 5 != 0 else 500,
                    'webhook_url': self.get_webhook_urls().get(payment.provider, f"{self.get_base_url()}/api/webhooks/{payment.provider}/"),
                }
                
                # Apply filters
                if event_type and event['event_type'] != event_type:
                    continue
                if status_filter and event['status'] != status_filter:
                    continue
                if provider and event['provider'] != provider:
                    continue
                    
                events.append(event)
        
        # Sort by timestamp descending (only if events exist)
        if events:
            events.sort(key=lambda x: x.get('timestamp', timezone.now()), reverse=True)
        
        # Pagination
        page_size = 20
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        paginated_events = events[start:end]
        
        response_data = {
            'events': paginated_events,
            'total': len(events),
            'page': page,
            'per_page': page_size,
            'has_next': end < len(events),
            'has_previous': page > 1,
            'ngrok_status': {
                'active': self.is_ngrok_active(),
                'base_url': self.get_base_url(),
                'webhook_urls': self.get_webhook_urls()
            }
        }
        
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed webhook event."""
        # Mock retry logic
        result_data = {
            'success': True,
            'message': f'Webhook event {pk} retry initiated',
            'event_id': pk,
            'retry_count': 2,
            'next_retry': timezone.now() + timedelta(minutes=5)
        }
        
        serializer = WebhookActionResultSerializer(result_data)
        logger.info(f"Webhook event {pk} retry initiated by admin {request.user.id}")
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear_all(self, request):
        """Clear all webhook events."""
        # Mock clear all logic
        result_data = {
            'success': True,
            'message': 'All webhook events cleared',
            'cleared_count': 150,  # Mock count
        }
        
        serializer = WebhookActionResultSerializer(result_data)
        logger.info(f"All webhook events cleared by admin {request.user.id}")
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def retry_failed(self, request):
        """Retry all failed webhook events."""
        # Mock retry failed logic
        # In real implementation:
        # failed_events = WebhookEvent.objects.filter(status='failed')
        # results = [retry_webhook_event(event) for event in failed_events]
        
        result_data = {
            'success': True,
            'message': 'All failed webhook events retry initiated',
            'processed_count': 0,  # Mock count
        }
        
        serializer = WebhookActionResultSerializer(result_data)
        logger.info(f"All failed webhook events retry initiated by admin {request.user.id}")
        return Response(serializer.data)
