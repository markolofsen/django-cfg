"""
Webhook API ViewSets for Universal Payment System v2.0.

Handles incoming webhooks from payment providers with universal support.
"""

import json
import logging
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ...services.core.webhook_service import WebhookService
from ...services.types import WebhookValidationRequest, WebhookProcessingResult
from django_cfg.modules.django_logger import get_logger

logger = get_logger("webhook_views")


@method_decorator(csrf_exempt, name='dispatch')
class UniversalWebhookView(APIView):
    """
    Universal webhook handler for all payment providers.
    
    Features:
    - Provider-agnostic webhook processing
    - Signature validation and security
    - Idempotency and replay protection
    - Comprehensive logging and monitoring
    - Integration with ngrok for development
    """
    
    permission_classes = [AllowAny]  # Webhooks don't use standard auth
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.webhook_service = WebhookService()
    
    def post(self, request: HttpRequest, provider: str) -> JsonResponse:
        """
        Handle incoming webhook from any payment provider.
        
        Args:
            request: HTTP request with webhook payload
            provider: Provider name (nowpayments, cryptapi, etc.)
            
        Returns:
            JsonResponse: Processing result
        """
        
        start_time = timezone.now()
        request_id = self._generate_request_id()
        
        logger.info(f"📥 Webhook received", extra={
            'provider': provider,
            'request_id': request_id,
            'content_type': request.content_type,
            'content_length': len(request.body) if request.body else 0,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')
        })
        
        try:
            # Parse webhook payload
            webhook_payload = self._parse_webhook_payload(request)
            if not webhook_payload:
                return self._error_response(
                    "Invalid webhook payload",
                    status.HTTP_400_BAD_REQUEST,
                    request_id
                )
            
            # Extract headers for signature validation
            webhook_headers = self._extract_webhook_headers(request)
            
            # Get signature from headers (provider-specific)
            signature = self._extract_signature(provider, webhook_headers)
            
            # Create validation request
            validation_request = WebhookValidationRequest(
                provider=provider,
                payload=webhook_payload,
                signature=signature,
                headers=webhook_headers,
                timestamp=start_time.isoformat(),
                request_id=request_id
            )
            
            # Process webhook
            result = self.webhook_service.process_webhook(validation_request)
            
            # Log processing result
            processing_time = (timezone.now() - start_time).total_seconds()
            
            logger.info(f"🔄 Webhook processed", extra={
                'provider': provider,
                'request_id': request_id,
                'success': result.success,
                'processing_time_ms': round(processing_time * 1000, 2),
                'actions_taken': getattr(result, 'actions_taken', []),
                'payment_id': getattr(result, 'payment_id', None)
            })
            
            # Return appropriate response
            if result.success:
                return self._success_response(result, request_id)
            else:
                return self._error_response(
                    result.error_message,
                    status.HTTP_400_BAD_REQUEST if 'validation' in result.error_message.lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
                    request_id,
                    result
                )
                
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON payload", extra={
                'provider': provider,
                'request_id': request_id,
                'error': str(e)
            })
            return self._error_response(
                "Invalid JSON payload",
                status.HTTP_400_BAD_REQUEST,
                request_id
            )
            
        except Exception as e:
            logger.error(f"Webhook processing error", extra={
                'provider': provider,
                'request_id': request_id,
                'error': str(e),
                'error_type': type(e).__name__
            })
            return self._error_response(
                "Internal server error",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                request_id
            )
    
    def get(self, request: HttpRequest, provider: str) -> JsonResponse:
        """
        Handle GET requests for webhook endpoint info.
        
        Useful for debugging and provider configuration verification.
        """
        
        logger.info(f"📋 Webhook info requested", extra={
            'provider': provider,
            'ip': self._get_client_ip(request)
        })
        
        # Get webhook URL using ngrok integration
        webhook_url = self._get_webhook_url(request, provider)
        
        info = {
            'provider': provider,
            'webhook_url': webhook_url,
            'supported_methods': ['POST'],
            'expected_headers': self._get_expected_headers(provider),
            'timestamp': timezone.now().isoformat(),
            'service_status': 'active'
        }
        
        return JsonResponse(info, status=status.HTTP_200_OK)
    
    # ===== HELPER METHODS =====
    
    def _parse_webhook_payload(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        """Parse webhook payload from request body."""
        try:
            if not request.body:
                return None
            
            # Handle different content types
            content_type = request.content_type.lower()
            
            if 'application/json' in content_type:
                return json.loads(request.body.decode('utf-8'))
            elif 'application/x-www-form-urlencoded' in content_type:
                # Some providers send form data
                from urllib.parse import parse_qs
                parsed = parse_qs(request.body.decode('utf-8'))
                # Convert single-item lists to values
                return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            else:
                # Try JSON as fallback
                return json.loads(request.body.decode('utf-8'))
                
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse webhook payload: {e}")
            return None
    
    def _extract_webhook_headers(self, request: HttpRequest) -> Dict[str, str]:
        """Extract relevant headers for webhook validation."""
        headers = {}
        
        # Extract all HTTP headers
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_X_CUSTOM_HEADER to x-custom-header
                header_name = key[5:].lower().replace('_', '-')
                headers[header_name] = value
        
        # Add some non-HTTP headers that might be useful
        headers['content-type'] = request.content_type
        headers['content-length'] = str(len(request.body)) if request.body else '0'
        
        return headers
    
    def _extract_signature(self, provider: str, headers: Dict[str, str]) -> Optional[str]:
        """Extract signature from headers based on provider."""
        
        # Provider-specific signature header mapping
        signature_headers = {
            'nowpayments': 'x-nowpayments-sig',
            'stripe': 'stripe-signature',
            'cryptapi': 'x-cryptapi-signature',
            'cryptomus': 'sign',
        }
        
        signature_header = signature_headers.get(provider.lower())
        if signature_header:
            return headers.get(signature_header)
        
        # Fallback: look for common signature headers
        common_headers = ['signature', 'x-signature', 'authorization']
        for header in common_headers:
            if header in headers:
                return headers[header]
        
        return None
    
    def _get_expected_headers(self, provider: str) -> Dict[str, str]:
        """Get expected headers for each provider."""
        from ...services.integrations import get_webhook_provider_info, is_provider_supported
        
        if not is_provider_supported(provider):
            return {'content-type': 'application/json'}
        
        provider_info = get_webhook_provider_info(provider)
        return {
            provider_info.signature_header: f'{provider_info.signature_algorithm} signature',
            'content-type': provider_info.content_type
        }
    
    def _get_webhook_url(self, request: HttpRequest, provider: str) -> str:
        """Get webhook URL using ngrok integration."""
        from ...services.integrations import get_webhook_url_for_provider
        return get_webhook_url_for_provider(provider)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _success_response(self, result: WebhookProcessingResult, request_id: str) -> JsonResponse:
        """Create success response."""
        
        response_data = {
            'success': True,
            'message': 'Webhook processed successfully',
            'request_id': request_id,
            'provider': result.provider,
            'processed': result.processed,
            'timestamp': timezone.now().isoformat()
        }
        
        # Add optional fields if available
        if hasattr(result, 'payment_id') and result.payment_id:
            response_data['payment_id'] = result.payment_id
        
        if hasattr(result, 'actions_taken') and result.actions_taken:
            response_data['actions_taken'] = result.actions_taken
        
        if hasattr(result, 'status_after') and result.status_after:
            response_data['payment_status'] = result.status_after
        
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    
    def _error_response(
        self, 
        message: str, 
        status_code: int, 
        request_id: str,
        result: Optional[WebhookProcessingResult] = None
    ) -> JsonResponse:
        """Create error response."""
        
        response_data = {
            'success': False,
            'error': message,
            'request_id': request_id,
            'timestamp': timezone.now().isoformat()
        }
        
        if result:
            response_data['provider'] = result.provider
            response_data['processed'] = getattr(result, 'processed', False)
        
        return JsonResponse(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_health_check(request):
    """
    Health check endpoint for webhook service.
    
    Returns service status and recent activity metrics.
    """
    
    try:
        from ...services.integrations import is_ngrok_available, get_api_base_url
        
        webhook_service = WebhookService()
        health_result = webhook_service.health_check()
        
        # Add ngrok status
        health_data = health_result.data if health_result.success else {}
        health_data.update({
            'ngrok_available': is_ngrok_available(),
            'api_base_url': get_api_base_url(),
        })
        
        if health_result.success:
            return Response({
                'status': 'healthy',
                'service': 'webhook_service',
                'timestamp': timezone.now().isoformat(),
                'details': health_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'unhealthy',
                'service': 'webhook_service',
                'error': health_result.message,
                'timestamp': timezone.now().isoformat(),
                'details': health_data
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        logger.error(f"Webhook health check failed: {e}")
        return Response({
            'status': 'error',
            'service': 'webhook_service',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_stats(request):
    """
    Get webhook processing statistics.
    
    Query parameters:
    - days: Number of days to analyze (default: 30)
    """
    
    try:
        days = int(request.GET.get('days', 30))
        if days < 1 or days > 365:
            days = 30
        
        webhook_service = WebhookService()
        stats_result = webhook_service.get_webhook_stats(days)
        
        if stats_result.success:
            return Response({
                'success': True,
                'stats': stats_result.data,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': stats_result.message,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except ValueError:
        return Response({
            'success': False,
            'error': 'Invalid days parameter',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Webhook stats failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def supported_providers(request):
    """
    Get list of supported webhook providers.
    
    Returns provider information and webhook URLs.
    """
    
    try:
        from ...services.integrations import get_all_webhook_urls, get_all_providers_info
        
        # Get all providers info dynamically
        providers_info = get_all_providers_info()
        webhook_urls = get_all_webhook_urls()
        
        # Build provider list
        providers_list = []
        for provider_name, info in providers_info.items():
            providers_list.append({
                'name': provider_name,
                'display_name': info['display_name'],
                'signature_header': info['signature_header'],
                'signature_algorithm': info['signature_algorithm'],
                'webhook_url': webhook_urls.get(provider_name, f"http://localhost:8000/api/webhooks/{provider_name}/"),
                'content_type': info['content_type']
            })
        
        return Response({
            'success': True,
            'providers': providers_list,
            'total_count': len(providers_list),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Supported providers endpoint failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== LEGACY FUNCTION-BASED VIEW FOR COMPATIBILITY =====

@csrf_exempt
@require_http_methods(["POST", "GET"])
def webhook_handler(request, provider: str):
    """
    Legacy function-based webhook handler for compatibility.
    
    Delegates to UniversalWebhookView for actual processing.
    """
    
    view = UniversalWebhookView()
    
    if request.method == 'POST':
        return view.post(request, provider)
    elif request.method == 'GET':
        return view.get(request, provider)
    else:
        return JsonResponse({
            'error': 'Method not allowed',
            'allowed_methods': ['POST', 'GET']
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
