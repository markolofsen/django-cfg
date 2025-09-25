"""
Decorators for API access control and endpoint registration.
"""

import functools
from django_cfg.modules.django_logger import get_logger
from typing import Optional, List, Callable, Any
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from .models import EndpointGroup, Subscription

logger = get_logger("decorators")


def require_api_key(func: Callable) -> Callable:
    """
    Decorator to require valid API key for function-based views.
    Works with APIAccessMiddleware.
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'payment_api_key'):
            return JsonResponse({
                'error': {
                    'code': 'MISSING_API_KEY',
                    'message': 'Valid API key required',
                    'timestamp': timezone.now().isoformat(),
                }
            }, status=401)
        
        return func(request, *args, **kwargs)
    
    return wrapper


def require_subscription(endpoint_group_name: str):
    """
    Decorator to require active subscription for specific endpoint group.
    
    Args:
        endpoint_group_name: Name of the endpoint group to check
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Check if middleware already validated subscription
            if hasattr(request, 'payment_subscription'):
                subscription = request.payment_subscription
                if subscription.endpoint_group.name == endpoint_group_name:
                    return func(request, *args, **kwargs)
            
            # If not validated by middleware, check manually
            if not hasattr(request, 'payment_api_key'):
                return JsonResponse({
                    'error': {
                        'code': 'MISSING_API_KEY',
                        'message': 'Valid API key required',
                        'timestamp': timezone.now().isoformat(),
                    }
                }, status=401)
            
            try:
                endpoint_group = EndpointGroup.objects.get(
                    name=endpoint_group_name,
                    is_active=True
                )
                
                subscription = Subscription.objects.filter(
                    user=request.payment_api_key.user,
                    endpoint_group=endpoint_group,
                    status='active',
                    expires_at__gt=timezone.now()
                ).first()
                
                if not subscription:
                    return JsonResponse({
                        'error': {
                            'code': 'NO_SUBSCRIPTION',
                            'message': f'Active subscription required for {endpoint_group.display_name}',
                            'timestamp': timezone.now().isoformat(),
                        }
                    }, status=403)
                
                # Store subscription in request
                request.payment_subscription = subscription
                
                return func(request, *args, **kwargs)
                
            except EndpointGroup.DoesNotExist:
                logger.error(f"Endpoint group '{endpoint_group_name}' not found")
                return JsonResponse({
                    'error': {
                        'code': 'INVALID_ENDPOINT_GROUP',
                        'message': 'Invalid endpoint group',
                        'timestamp': timezone.now().isoformat(),
                    }
                }, status=500)
        
        return wrapper
    return decorator


def require_tier(minimum_tier: str):
    """
    Decorator to require minimum subscription tier.
    
    Args:
        minimum_tier: Minimum required tier (basic, premium, enterprise)
    """
    tier_hierarchy = {
        'basic': 1,
        'premium': 2,
        'enterprise': 3,
    }
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'payment_subscription'):
                return JsonResponse({
                    'error': {
                        'code': 'NO_SUBSCRIPTION',
                        'message': 'Active subscription required',
                        'timestamp': timezone.now().isoformat(),
                    }
                }, status=403)
            
            subscription = request.payment_subscription
            current_tier_level = tier_hierarchy.get(subscription.tier, 0)
            required_tier_level = tier_hierarchy.get(minimum_tier, 999)
            
            if current_tier_level < required_tier_level:
                return JsonResponse({
                    'error': {
                        'code': 'INSUFFICIENT_TIER',
                        'message': f'Tier {minimum_tier} or higher required',
                        'current_tier': subscription.tier,
                        'required_tier': minimum_tier,
                        'timestamp': timezone.now().isoformat(),
                    }
                }, status=403)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def track_usage(cost_per_request: float = 0.0):
    """
    Decorator to track API usage and deduct costs.
    
    Args:
        cost_per_request: Cost to deduct per successful request
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Execute the function
            response = func(request, *args, **kwargs)
            
            # Track usage if successful and we have subscription
            if (hasattr(request, 'payment_subscription') and 
                hasattr(response, 'status_code') and
                200 <= response.status_code < 300 and
                cost_per_request > 0):
                
                try:
                    from .models import Transaction
                    
                    subscription = request.payment_subscription
                    
                    # Create billing transaction
                    Transaction.objects.create(
                        user=subscription.user,
                        subscription=subscription,
                        transaction_type='debit',
                        amount_usd=-cost_per_request,
                        description=f"API usage: {request.method} {request.path}",
                        metadata={
                            'endpoint': request.path,
                            'method': request.method,
                            'cost_per_request': cost_per_request,
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error tracking usage: {e}")
            
            return response
        
        return wrapper
    return decorator


def register_endpoint(endpoint_group_name: str, 
                     display_name: Optional[str] = None,
                     description: Optional[str] = None,
                     require_api_key: bool = True):
    """
    Decorator to automatically register endpoint with the system.
    This creates or updates EndpointGroup records.
    
    Args:
        endpoint_group_name: Internal name for the endpoint group
        display_name: Human-readable name
        description: Description of the endpoint functionality
        require_api_key: Whether this endpoint requires API key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Auto-register endpoint group if it doesn't exist
            try:
                endpoint_group, created = EndpointGroup.objects.get_or_create(
                    name=endpoint_group_name,
                    defaults={
                        'display_name': display_name or endpoint_group_name.replace('_', ' ').title(),
                        'description': description or f'Auto-registered endpoint group: {endpoint_group_name}',
                        'require_api_key': require_api_key,
                        'is_active': True,
                    }
                )
                
                if created:
                    logger.info(f"Auto-registered endpoint group: {endpoint_group_name}")
                
            except Exception as e:
                logger.error(f"Error auto-registering endpoint group: {e}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_usage_limit(func: Callable) -> Callable:
    """
    Decorator to check subscription usage limits before processing request.
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request, 'payment_subscription'):
            subscription = request.payment_subscription
            
            # Check if usage limit exceeded
            if (subscription.usage_limit > 0 and 
                subscription.usage_current >= subscription.usage_limit):
                
                return JsonResponse({
                    'error': {
                        'code': 'USAGE_EXCEEDED',
                        'message': 'Monthly usage limit exceeded',
                        'current_usage': subscription.usage_current,
                        'usage_limit': subscription.usage_limit,
                        'reset_date': subscription.next_billing.isoformat() if subscription.next_billing else None,
                        'timestamp': timezone.now().isoformat(),
                    }
                }, status=429)
        
        return func(request, *args, **kwargs)
    
    return wrapper


# Utility decorator combinations
def api_endpoint(endpoint_group_name: str, 
                minimum_tier: str = 'basic',
                cost_per_request: float = 0.0):
    """
    Combination decorator for typical API endpoint protection.
    
    Args:
        endpoint_group_name: Name of the endpoint group
        minimum_tier: Minimum subscription tier required
        cost_per_request: Cost to charge per successful request
    """
    def decorator(func: Callable) -> Callable:
        # Apply decorators in reverse order (they wrap from inside out)
        decorated_func = func
        decorated_func = track_usage(cost_per_request)(decorated_func)
        decorated_func = check_usage_limit(decorated_func)
        decorated_func = require_tier(minimum_tier)(decorated_func)
        decorated_func = require_subscription(endpoint_group_name)(decorated_func)
        decorated_func = require_api_key(decorated_func)
        decorated_func = register_endpoint(endpoint_group_name)(decorated_func)
        
        return decorated_func
    
    return decorator
