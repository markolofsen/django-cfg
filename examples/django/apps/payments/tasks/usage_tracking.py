"""
Background tasks for API usage tracking and statistics.
"""
import dramatiq
import logging
import time
from typing import Dict, Any, List
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.core.cache import cache

from ..models import APIKey, Subscription
from .types import (
    TaskResult,
    UsageUpdateRequest,
    UsageUpdateResult,
    BatchUpdateResult,
    CleanupResult
)

logger = logging.getLogger(__name__)

@dramatiq.actor(queue_name="payments")
def update_api_key_usage_async(
    api_key_id: str, 
    ip_address: str = None,
    increment: int = 1
) -> UsageUpdateResult:
    """
    Update API key usage counters asynchronously.
    
    Args:
        api_key_id: API key UUID to update
        ip_address: Client IP address for logging
        increment: Number to increment (default: 1)
        
    Returns:
        Update result with statistics
    """
    start_time = time.time()
    
    try:
        with transaction.atomic():
            # Use F() expressions for atomic updates
            updated_count = APIKey.objects.filter(id=api_key_id).update(
                total_requests=F('total_requests') + increment,
                last_used_at=timezone.now(),
                updated_at=timezone.now()
            )
            
            if updated_count == 0:
                logger.warning(f"API key not found: {api_key_id}")
                return UsageUpdateResult(
                    status='error',
                    error='API key not found',
                    resource_id=api_key_id,
                    increment=increment
                )
            
            # Get updated values for logging
            api_key = APIKey.objects.get(id=api_key_id)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.debug(f"API key usage updated", extra={
                'api_key_id': api_key_id,
                'user_id': api_key.user.id,
                'total_requests': api_key.total_requests,
                'increment': increment,
                'ip_address': ip_address,
                'processing_time_ms': round(processing_time, 2)
            })
            
            return UsageUpdateResult(
                status='success',
                resource_id=api_key_id,
                total_requests=api_key.total_requests,
                increment=increment,
                user_id=api_key.user.id,
                processing_time_ms=round(processing_time, 2)
            )
            
    except Exception as e:
        logger.error(f"Failed to update API key usage", extra={
            'api_key_id': api_key_id,
            'error': str(e),
            'ip_address': ip_address
        })
        raise  # Re-raise for Dramatiq retry logic

@dramatiq.actor(queue_name="payments")
def update_subscription_usage_async(
    subscription_id: str,
    increment: int = 1
) -> UsageUpdateResult:
    """
    Update subscription usage counters asynchronously.
    
    Args:
        subscription_id: Subscription UUID to update
        increment: Number to increment (default: 1)
        
    Returns:
        Update result with statistics
    """
    start_time = time.time()
    
    try:
        with transaction.atomic():
            # Use F() expressions for atomic updates
            updated_count = Subscription.objects.filter(id=subscription_id).update(
                total_requests=F('total_requests') + increment,
                last_request_at=timezone.now(),
                updated_at=timezone.now()
            )
            
            if updated_count == 0:
                logger.warning(f"Subscription not found: {subscription_id}")
                return UsageUpdateResult(
                    status='error',
                    error='Subscription not found',
                    resource_id=subscription_id,
                    increment=increment
                )
            
            # Get updated values for logging
            subscription = Subscription.objects.get(id=subscription_id)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.debug(f"Subscription usage updated", extra={
                'subscription_id': subscription_id,
                'user_id': subscription.user.id,
                'total_requests': subscription.total_requests,
                'increment': increment,
                'processing_time_ms': round(processing_time, 2)
            })
            
            return UsageUpdateResult(
                status='success',
                resource_id=subscription_id,
                total_requests=subscription.total_requests,
                increment=increment,
                user_id=subscription.user.id,
                processing_time_ms=round(processing_time, 2)
            )
            
    except Exception as e:
        logger.error(f"Failed to update subscription usage", extra={
            'subscription_id': subscription_id,
            'error': str(e)
        })
        raise  # Re-raise for Dramatiq retry logic

@dramatiq.actor(queue_name="payments")
def batch_update_usage_counters() -> BatchUpdateResult:
    """
    Batch update usage counters from cache to reduce database load.
    
    This task processes accumulated usage data from Redis cache
    and performs batch updates to the database.
    
    Returns:
        Batch processing results
    """
    start_time = time.time()
    api_keys_updated = 0
    subscriptions_updated = 0
    errors = []
    
    try:
        # Process API key usage counters
        api_key_pattern = "api_usage_pending:*"
        api_key_keys = cache.keys(api_key_pattern)
        
        for cache_key in api_key_keys:
            try:
                # Extract API key ID from cache key
                api_key_id = cache_key.split(':')[-1]
                pending_count = cache.get(cache_key, 0)
                
                if pending_count > 0:
                    # Update in background
                    update_api_key_usage_async.send(
                        api_key_id=api_key_id,
                        increment=pending_count
                    )
                    
                    # Clear cache
                    cache.delete(cache_key)
                    api_keys_updated += 1
                    
            except Exception as e:
                errors.append({
                    'type': 'api_key',
                    'cache_key': cache_key,
                    'error': str(e)
                })
        
        # Process subscription usage counters
        subscription_pattern = "subscription_usage_pending:*"
        subscription_keys = cache.keys(subscription_pattern)
        
        for cache_key in subscription_keys:
            try:
                # Extract subscription ID from cache key
                subscription_id = cache_key.split(':')[-1]
                pending_count = cache.get(cache_key, 0)
                
                if pending_count > 0:
                    # Update in background
                    update_subscription_usage_async.send(
                        subscription_id=subscription_id,
                        increment=pending_count
                    )
                    
                    # Clear cache
                    cache.delete(cache_key)
                    subscriptions_updated += 1
                    
            except Exception as e:
                errors.append({
                    'type': 'subscription',
                    'cache_key': cache_key,
                    'error': str(e)
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Batch usage update completed", extra={
            'api_keys_updated': api_keys_updated,
            'subscriptions_updated': subscriptions_updated,
            'errors_count': len(errors),
            'processing_time_ms': round(processing_time, 2)
        })
        
        return BatchUpdateResult(
            status='success',
            api_keys_updated=api_keys_updated,
            subscriptions_updated=subscriptions_updated,
            errors=errors,
            total_items=api_keys_updated + subscriptions_updated,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Batch usage update failed: {e}")
        errors.append({
            'type': 'batch_processing',
            'error': str(e)
        })
        return BatchUpdateResult(
            status='error',
            api_keys_updated=api_keys_updated,
            subscriptions_updated=subscriptions_updated,
            errors=errors,
            total_items=api_keys_updated + subscriptions_updated,
            error=str(e)
        )

@dramatiq.actor(queue_name="payments")
def cleanup_stale_usage_cache() -> CleanupResult:
    """
    Cleanup stale usage tracking cache entries.
    
    Removes old cache entries that might have been left behind
    due to processing errors or system restarts.
    
    Returns:
        Cleanup results
    """
    try:
        cleanup_count = 0
        
        # Cleanup old API key usage cache
        api_key_keys = cache.keys("api_usage_pending:*")
        for key in api_key_keys:
            # Check if cache entry is older than 1 hour
            ttl = cache.ttl(key)
            if ttl is not None and ttl < 3600:  # Less than 1 hour remaining
                cache.delete(key)
                cleanup_count += 1
        
        # Cleanup old subscription usage cache
        subscription_keys = cache.keys("subscription_usage_pending:*")
        for key in subscription_keys:
            ttl = cache.ttl(key)
            if ttl is not None and ttl < 3600:
                cache.delete(key)
                cleanup_count += 1
        
        logger.info(f"Cleaned up {cleanup_count} stale cache entries")
        
        return CleanupResult(
            status='completed',
            cleaned_entries=cleanup_count,
            cleanup_type='stale_usage_cache'
        )
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        return CleanupResult(
            status='error',
            error=str(e),
            cleaned_entries=0,
            cleanup_type='stale_usage_cache'
        )
