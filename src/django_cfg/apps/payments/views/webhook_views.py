"""
Webhook processing views with signature validation.
"""

import json
from django_cfg.modules.django_logger import get_logger
from typing import Dict, Any

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..services.core.payment_service import PaymentService
from ..tasks.webhook_processing import process_webhook_with_fallback
from ..services.security.webhook_validator import webhook_validator
from ..services.security.error_handler import error_handler, SecurityError, ValidationError

logger = get_logger("webhook_views")


@csrf_exempt
@require_http_methods(["POST"])
def webhook_handler(request, provider: str):
    """
    Main webhook handler with signature validation.
    
    Accepts webhooks from payment providers and processes them
    with proper validation and fallback mechanisms.
    """
    try:
        # Parse webhook data
        webhook_data = json.loads(request.body.decode('utf-8'))
        
        # Extract request headers
        request_headers = {
            key: value for key, value in request.META.items()
            if key.startswith('HTTP_')
        }
        
        # Generate idempotency key for deduplication
        idempotency_key = _generate_idempotency_key(provider, webhook_data, request_headers)
        
        logger.info(f"📥 Received webhook from {provider}, key: {idempotency_key}")
        
        # Validate webhook with enhanced security
        is_valid, validation_error = webhook_validator.validate_webhook(
            provider=provider,
            webhook_data=webhook_data,
            request_headers=request_headers,
            raw_body=request.body
        )
        
        if not is_valid:
            security_error = SecurityError(
                f"Webhook validation failed: {validation_error}",
                details={'provider': provider, 'validation_error': validation_error}
            )
            error_handler.handle_error(security_error, {
                'provider': provider,
                'webhook_data_keys': list(webhook_data.keys()),
                'headers_count': len(request_headers)
            }, request)
            
            return JsonResponse(
                {'error': 'Webhook validation failed', 'code': 'INVALID_WEBHOOK'}, 
                status=403
            )
        
        # Process webhook (async with fallback to sync)
        result = process_webhook_with_fallback(
            provider=provider,
            webhook_data=webhook_data,
            idempotency_key=idempotency_key,
            request_headers=request_headers
        )
        
        if result.get('success'):
            logger.info(f"✅ Webhook processed successfully: {idempotency_key}")
            return JsonResponse({
                'status': 'success',
                'idempotency_key': idempotency_key,
                'processing_mode': result.get('mode', 'unknown')
            })
        else:
            logger.error(f"❌ Webhook processing failed: {result.get('error')}")
            return JsonResponse({
                'status': 'error',
                'error': result.get('error', 'Processing failed'),
                'idempotency_key': idempotency_key
            }, status=400)
            
    except json.JSONDecodeError as e:
        validation_error = ValidationError(
            f"Invalid JSON in webhook from {provider}",
            details={'provider': provider, 'json_error': str(e)}
        )
        error_result = error_handler.handle_error(validation_error, {
            'provider': provider,
            'raw_body_length': len(request.body) if request.body else 0
        }, request)
        
        return JsonResponse({
            'error': 'Invalid JSON',
            'code': validation_error.error_code
        }, status=400)
        
    except Exception as e:
        # Handle unexpected errors with centralized error handler
        error_result = error_handler.handle_error(e, {
            'provider': provider,
            'operation': 'webhook_processing',
            'webhook_data_available': 'webhook_data' in locals()
        }, request)
    
        return JsonResponse({
            'error': 'Internal server error',
            'code': error_result.error.error_code
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_test(request):
    """
    Test webhook endpoint for development.
    
    Allows testing webhook processing without requiring
    actual payment provider signatures.
    """
    try:
        provider = request.data.get('provider', 'test')
        webhook_data = request.data.get('webhook_data', {})
        
        # Add test marker
        webhook_data['_test_webhook'] = True
        
        # Generate test idempotency key
        import uuid
        idempotency_key = f"test_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"🧪 Processing test webhook: {provider}")
        
        # Process with PaymentService directly (sync)
        payment_service = PaymentService()
        result = payment_service.process_webhook(
            provider=provider,
            webhook_data=webhook_data,
            request_headers={'HTTP_X_TEST': 'true'}
        )
        
        return Response({
            'status': 'success',
            'test_mode': True,
            'provider': provider,
            'idempotency_key': idempotency_key,
            'result': result.dict() if hasattr(result, 'dict') else result
        })
        
    except Exception as e:
        logger.error(f"❌ Test webhook error: {e}")
        return Response({
            'status': 'error',
            'error': str(e),
            'test_mode': True
        }, status=status.HTTP_400_BAD_REQUEST)


def _validate_webhook_signature(provider: str, webhook_data: Dict[str, Any], 
                               request_headers: Dict[str, str]) -> bool:
    """
    Validate webhook signature based on provider.
    
    Each provider has different signature validation methods.
    """
    try:
        if provider == 'nowpayments':
            return _validate_nowpayments_signature(webhook_data, request_headers)
        elif provider == 'cryptapi':
            return _validate_cryptapi_signature(webhook_data, request_headers)
        elif provider == 'test':
            return True  # Allow test webhooks
        else:
            logger.warning(f"Unknown provider for signature validation: {provider}")
            return False
            
    except Exception as e:
        logger.error(f"Signature validation error for {provider}: {e}")
        return False


def _validate_nowpayments_signature(webhook_data: Dict[str, Any], 
                                  request_headers: Dict[str, str]) -> bool:
    """Validate NowPayments webhook signature."""
    import hmac
    import hashlib
    from ..utils.config_utils import get_payments_config
    
    # Get IPN secret from config
    config = get_payments_config()
    if not config or not hasattr(config, 'providers') or 'nowpayments' not in config.providers:
        logger.warning("NowPayments IPN secret not configured, skipping validation")
        return True  # Allow if not configured (development mode)
    
    nowpayments_config = config.providers['nowpayments']
    ipn_secret = getattr(nowpayments_config, 'ipn_secret', None)
    
    if not ipn_secret:
        logger.warning("NowPayments IPN secret not configured, skipping validation")
        return True
    
    # Get signature from headers
    signature = request_headers.get('HTTP_X_NOWPAYMENTS_SIG')
    if not signature:
        logger.warning("No NowPayments signature found in headers")
        return False
    
    # Calculate expected signature
    payload = json.dumps(webhook_data, separators=(',', ':'), sort_keys=True)
    expected_signature = hmac.new(
        ipn_secret.encode(),
        payload.encode(),
        hashlib.sha512
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def _validate_cryptapi_signature(webhook_data: Dict[str, Any], 
                                request_headers: Dict[str, str]) -> bool:
    """Validate CryptAPI webhook signature."""
    # CryptAPI uses different validation method
    # For now, implement basic validation
    
    # Check if required fields are present
    required_fields = ['address_in', 'address_out', 'txid_in', 'value_coin', 'coin', 'confirmations']
    for field in required_fields:
        if field not in webhook_data:
            logger.warning(f"Missing required field in CryptAPI webhook: {field}")
            return False
    
    return True


def _generate_idempotency_key(provider: str, webhook_data: Dict[str, Any], 
                            request_headers: Dict[str, str]) -> str:
    """Generate idempotency key for webhook deduplication."""
    import hashlib
    
    # Use provider + payment ID + timestamp for uniqueness
    payment_id = (
        webhook_data.get('payment_id') or 
        webhook_data.get('order_id') or
        webhook_data.get('id') or
        'unknown'
    )
    
    timestamp = webhook_data.get('created_at') or webhook_data.get('timestamp')
    
    # Create hash from key components
    key_data = f"{provider}:{payment_id}:{timestamp}"
    return hashlib.md5(key_data.encode()).hexdigest()[:16]
