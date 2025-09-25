"""
Webhook Processing Tasks

Simple webhook processing with fallback to sync processing.
Uses existing Dramatiq configuration and graceful degradation.
"""

from django_cfg.modules.django_logger import get_logger
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone

# Use existing dramatiq setup
import dramatiq

from ..services.core.payment_service import PaymentService
from ..models.events import PaymentEvent

logger = get_logger("webhook_processing")


@dramatiq.actor(
    queue_name="payments",
    priority=3          # High priority for webhooks
)
def process_webhook_async(
    provider: str, 
    webhook_data: dict, 
    idempotency_key: str,
    request_headers: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Process payment webhook asynchronously.
    
    Args:
        provider: Payment provider name (nowpayments, cryptapi, etc.)
        webhook_data: Raw webhook payload from provider
        idempotency_key: Unique key to prevent duplicate processing
        request_headers: HTTP headers for webhook validation
        
    Returns:
        Processing results with success/error status
        
    Raises:
        Exception: If processing fails after retries
    """
    start_time = timezone.now()
    
    try:
        # Log task start
        logger.info(f"🚀 Processing webhook async: {provider}, key: {idempotency_key}")
        
        # Check for duplicate processing
        if _is_webhook_already_processed(idempotency_key):
            logger.info(f"✅ Webhook already processed: {idempotency_key}")
            return {"success": True, "message": "Already processed", "duplicate": True}
        
        # Process webhook
        with transaction.atomic():
            payment_service = PaymentService()
            result = payment_service.process_webhook(
                provider=provider,
                webhook_data=webhook_data, 
                request_headers=request_headers
            )
            
            # Mark as processed
            _mark_webhook_processed(idempotency_key, result.dict())
            
            processing_time = (timezone.now() - start_time).total_seconds()
            
            logger.info(
                f"✅ Webhook processed successfully: {idempotency_key}, "
                f"time: {processing_time:.2f}s"
            )
            
            return {
                "success": True,
                "idempotency_key": idempotency_key,
                "processing_time_seconds": processing_time,
                "result": result.dict()
            }
            
    except Exception as e:
        processing_time = (timezone.now() - start_time).total_seconds()
        
        logger.error(
            f"❌ Webhook processing failed: {idempotency_key}, "
            f"error: {str(e)}, time: {processing_time:.2f}s"
        )
        
        # Re-raise for Dramatiq retry mechanism
        raise


def process_webhook_with_fallback(
    provider: str,
    webhook_data: dict,
    idempotency_key: str,
    request_headers: Optional[dict] = None,
    force_sync: bool = False
):
    """
    Process webhook with automatic async/sync fallback.
    
    If Dramatiq is unavailable, processes synchronously.
    If force_sync=True, skips async processing.
    """
    if force_sync:
        logger.info(f"Processing webhook synchronously (forced): {provider}")
        return _process_webhook_sync(provider, webhook_data, idempotency_key, request_headers)
    
    try:
        # Try async processing
        process_webhook_async.send(
            provider=provider,
            webhook_data=webhook_data,
            idempotency_key=idempotency_key,
            request_headers=request_headers
        )
        logger.info(f"Webhook queued for async processing: {idempotency_key}")
        return {"success": True, "mode": "async", "queued": True}
        
    except Exception as e:
        logger.warning(f"Async processing failed, falling back to sync: {e}")
        return _process_webhook_sync(provider, webhook_data, idempotency_key, request_headers)


def _process_webhook_sync(
    provider: str,
    webhook_data: dict,
    idempotency_key: str,
    request_headers: Optional[dict] = None
):
    """Fallback sync webhook processing."""
    logger.info(f"Processing webhook synchronously: {provider}")
    
    try:
        payment_service = PaymentService()
        result = payment_service.process_webhook(
            provider=provider,
            webhook_data=webhook_data,
            request_headers=request_headers
        )
        
        _mark_webhook_processed(idempotency_key, result.dict())
        
        return {
            "success": True,
            "mode": "sync",
            "result": result.dict()
        }
        
    except Exception as e:
        logger.error(f"Sync webhook processing failed: {e}")
        raise


def _is_webhook_already_processed(idempotency_key: str) -> bool:
    """Check if webhook was already processed."""
    return PaymentEvent.objects.filter(
        idempotency_key=idempotency_key,
        event_type=PaymentEvent.EventType.WEBHOOK_PROCESSED
    ).exists()


def _mark_webhook_processed(idempotency_key: str, result_data: dict):
    """Mark webhook as processed."""
    import os
    
    PaymentEvent.objects.create(
        payment_id=result_data.get('payment_id', 'unknown'),
        event_type=PaymentEvent.EventType.WEBHOOK_PROCESSED,
        event_data=result_data,
        idempotency_key=idempotency_key,
        processed_by=f"worker-{os.getpid()}"
    )
