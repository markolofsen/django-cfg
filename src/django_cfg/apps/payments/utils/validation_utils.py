"""
Validation utilities for payments module.

Basic validation functions for API keys and subscription access.
"""

from django_cfg.modules.django_logger import get_logger
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import APIKey, Subscription

User = get_user_model()
logger = get_logger("validation_utils")


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        key = APIKey.objects.select_related('user').get(
            key_value=api_key,
            is_active=True
        )
        
        # Check if key is expired
        if key.expires_at and key.expires_at < timezone.now():
            return False
            
        return True
        
    except APIKey.DoesNotExist:
        return False
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return False


def check_subscription_access(user_id: int, endpoint_group: str) -> Dict[str, Any]:
    """
    Check subscription access for user and endpoint group.
    
    Args:
        user_id: User ID
        endpoint_group: Endpoint group name
        
    Returns:
        Access check result dictionary
    """
    try:
        subscription = Subscription.objects.select_related('endpoint_group').get(
            user_id=user_id,
            endpoint_group__name=endpoint_group,
            status='active',
            expires_at__gt=timezone.now()
        )
        
        # Check usage limits
        usage_percentage = (subscription.current_usage / subscription.monthly_limit) * 100
        remaining_requests = subscription.monthly_limit - subscription.current_usage
        
        return {
            'allowed': remaining_requests > 0,
            'subscription_id': str(subscription.id),
            'remaining_requests': remaining_requests,
            'usage_percentage': usage_percentage,
            'reason': 'Active subscription' if remaining_requests > 0 else 'Usage limit exceeded'
        }
        
    except Subscription.DoesNotExist:
        return {
            'allowed': False,
            'reason': 'No active subscription found',
            'subscription_id': None,
            'remaining_requests': 0,
            'usage_percentage': 0
        }
    except Exception as e:
        logger.error(f"Error checking subscription access: {e}")
        return {
            'allowed': False,
            'reason': f'Access check failed: {str(e)}',
            'subscription_id': None,
            'remaining_requests': 0,
            'usage_percentage': 0
        }
