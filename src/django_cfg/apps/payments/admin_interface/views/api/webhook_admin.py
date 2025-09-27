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
from django_cfg.apps.payments.services.core.webhook_service import WebhookService
from django_cfg.apps.payments.models import UniversalPayment
from django_cfg.modules.django_logger import get_logger

logger = get_logger("admin_webhook_api")


class AdminWebhookViewSet(AdminReadOnlyViewSet):
    """
    Admin ViewSet for webhook configuration management.
    
    Read-only view for webhook configurations and provider info.
    Requires admin permissions.
    """
    
    # No model - this is for webhook configuration data
    serializer_class = WebhookStatsSerializer
    
    def list(self, request):
        """List webhook providers and configurations."""
        # Mock webhook provider data - replace with real configuration
        providers_data = [
            {
                'name': 'nowpayments',
                'display_name': 'NowPayments',
                'enabled': True,
                'webhook_url': 'https://api.nowpayments.io/v1/webhooks',
                'supported_events': ['payment.created', 'payment.completed', 'payment.failed'],
                'last_ping': timezone.now() - timedelta(minutes=5),
                'status': 'active'
            },
            {
                'name': 'stripe',
                'display_name': 'Stripe',
                'enabled': False,
                'webhook_url': 'https://api.stripe.com/v1/webhooks',
                'supported_events': ['payment_intent.succeeded', 'payment_intent.payment_failed'],
                'last_ping': None,
                'status': 'inactive'
            }
        ]
        
        serializer = self.get_serializer(providers_data, many=True)
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
            'total_events': total_payments * 2,  # Assume 2 events per payment on average
            'successful_events': int(total_payments * 1.8),  # 90% success rate
            'failed_events': int(total_payments * 0.2),  # 10% failure rate
            'success_rate': 90.0,
            'recent_events': recent_payments * 2,
            'providers': {
                'nowpayments': {
                    'total': int(total_payments * 0.7),
                    'successful': int(total_payments * 0.65),
                    'failed': int(total_payments * 0.05),
                    'success_rate': 92.8
                },
                'stripe': {
                    'total': int(total_payments * 0.3),
                    'successful': int(total_payments * 0.28),
                    'failed': int(total_payments * 0.02),
                    'success_rate': 93.3
                }
            },
            'events_by_type': {
                'payment.created': int(total_payments * 1.0),
                'payment.completed': int(total_payments * 0.8),
                'payment.failed': int(total_payments * 0.2),
            },
            'recent_activity': [
                {
                    'timestamp': timezone.now() - timedelta(minutes=i*5),
                    'event_type': 'payment.created' if i % 3 == 0 else 'payment.completed',
                    'provider': 'nowpayments' if i % 2 == 0 else 'stripe',
                    'status': 'success' if i % 4 != 0 else 'failed'
                }
                for i in range(10)
            ]
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'status', 'provider']
    search_fields = ['event_type', 'webhook_url']
    ordering_fields = ['created_at', 'event_type', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get webhook events queryset."""
        # For now, return empty queryset since we're using mock data
        # In real implementation, this would return WebhookEvent.objects.all()
        return UniversalPayment.objects.none()
    
    def list(self, request):
        """List webhook events with filtering and pagination."""
        # Get filter parameters
        event_type = request.query_params.get('event_type')
        status_filter = request.query_params.get('status')
        provider = request.query_params.get('provider')
        
        # Get real payment data to generate realistic mock events
        payments = UniversalPayment.objects.all()[:50]  # Limit for performance
        
        # Generate mock webhook events based on real payments
        events = []
        for i, payment in enumerate(payments):
            # Create multiple events per payment
            event_types = ['payment.created', 'payment.completed'] if payment.status == 'completed' else ['payment.created']
            
            for event_type_name in event_types:
                event = {
                    'id': f"evt_{payment.id}_{event_type_name.split('.')[1]}",
                    'event_type': event_type_name,
                    'webhook_url': f'https://example.com/webhook/{payment.id}',
                    'status': 'success' if i % 5 != 0 else 'failed',
                    'provider': 'nowpayments' if i % 2 == 0 else 'stripe',
                    'created_at': payment.created_at,
                    'response_code': 200 if i % 5 != 0 else 500,
                    'response_time': f"{50 + (i % 200)}ms",
                    'attempts': 1 if i % 5 != 0 else 3,
                    'payload': {
                        'payment_id': str(payment.id),
                        'amount': str(payment.amount),
                        'currency': payment.currency,
                        'status': payment.status,
                        'timestamp': payment.created_at.isoformat()
                    }
                }
                
                # Apply filters
                if event_type and event['event_type'] != event_type:
                    continue
                if status_filter and event['status'] != status_filter:
                    continue
                if provider and event['provider'] != provider:
                    continue
                    
                events.append(event)
        
        # Sort by created_at descending
        events.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Pagination
        page_size = 20
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        paginated_events = events[start:end]
        
        response_data = {
            'events': paginated_events,
            'total': len(events),
            'page': page,
            'per_page': page_size,
            'has_next': end < len(events),
            'has_previous': page > 1
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
