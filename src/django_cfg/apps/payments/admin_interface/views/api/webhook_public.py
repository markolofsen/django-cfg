"""
Public Webhook ViewSets.

DRF ViewSets for public webhook functionality.
No authentication required.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone

from django_cfg.apps.payments.admin_interface.serializers import WebhookStatsSerializer
from django_cfg.modules.django_logger import get_logger

logger = get_logger("webhook_public_api")


class WebhookTestViewSet(viewsets.ViewSet):
    """
    Public ViewSet for webhook testing functionality.
    
    Allows testing webhook endpoints without admin permissions.
    Perfect for development and integration testing.
    """
    
    permission_classes = [AllowAny]  # Explicitly allow any user
    serializer_class = WebhookStatsSerializer  # For schema generation
    
    @action(detail=False, methods=['post'])
    def test(self, request):
        """
        Test webhook endpoint.
        
        Sends a test webhook to the specified URL with the given event type.
        Useful for developers to test their webhook implementations.
        """
        webhook_url = request.data.get('webhook_url')
        event_type = request.data.get('event_type')
        
        if not webhook_url or not event_type:
            return Response({
                'success': False,
                'error': 'webhook_url and event_type are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: In real implementation, send actual HTTP request to webhook_url
        # For now, return mock success response
        
        logger.info(f"Test webhook sent to {webhook_url} with event type {event_type}")
        
        return Response({
            'success': True,
            'message': f'Test webhook sent to {webhook_url} with event type {event_type}',
            'webhook_url': webhook_url,
            'event_type': event_type,
            'timestamp': timezone.now().isoformat(),
            'test_payload': {
                'event': event_type,
                'data': {
                    'id': 'test_payment_123',
                    'amount': '100.00',
                    'currency': 'USD',
                    'status': 'completed',
                    'created_at': timezone.now().isoformat()
                },
                'timestamp': timezone.now().isoformat()
            }
        })
