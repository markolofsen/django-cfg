"""
Subscription Service - Core subscription management and access control.

This service handles subscription creation, renewal, access validation,
and usage tracking with Redis caching.
"""

from typing import Dict, Any, Optional, List
from django_cfg.modules.django_logger import get_logger
from datetime import datetime, timedelta, timezone as dt_timezone

from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from pydantic import BaseModel, Field, ValidationError
from decimal import Decimal

from ...models import Subscription, EndpointGroup, Tariff
from ..internal_types import ServiceOperationResult, SubscriptionInfo, EndpointGroupInfo

User = get_user_model()
logger = get_logger("subscription_service")


class SubscriptionRequest(BaseModel):
    """Type-safe subscription request"""
    user_id: int = Field(gt=0, description="User ID")
    endpoint_group_name: str = Field(min_length=1, description="Endpoint group name")
    tariff_id: Optional[str] = Field(None, description="Specific tariff ID")
    billing_period: str = Field(default='monthly', pattern='^(monthly|yearly)$', description="Billing period")
    auto_renew: bool = Field(default=True, description="Auto-renewal setting")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SubscriptionResult(BaseModel):
    """Type-safe subscription operation result"""
    success: bool
    subscription_id: Optional[str] = None
    endpoint_group_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class AccessCheck(BaseModel):
    """Type-safe access check result"""
    allowed: bool
    subscription_id: Optional[str] = None
    reason: Optional[str] = None
    remaining_requests: Optional[int] = None
    usage_percentage: Optional[float] = None
    required_subscription: Optional[str] = None
    current_usage: Optional[int] = None
    monthly_limit: Optional[int] = None


class SubscriptionService:
    """
    Universal subscription management service.
    
    Handles subscription lifecycle, access control, and usage tracking
    with support for multiple active subscriptions per user.
    """
    
    def __init__(self):
        """Initialize subscription service with dependencies"""
        pass
    
    def create_subscription(self, subscription_data: dict) -> 'ServiceOperationResult':
        """
        Create new subscription for user.
        
        Args:
            subscription_data: Dictionary with subscription details
            
        Returns:
            ServiceOperationResult with subscription details
        """
        try:
            # Get user
            user = User.objects.get(id=subscription_data['user_id'])
            
            # Get endpoint group
            endpoint_group = EndpointGroup.objects.get(
                name=subscription_data['endpoint_group_name'],
                is_active=True
            )
            
            with transaction.atomic():
                # Check for existing active subscription
                existing = Subscription.objects.filter(
                    user=user,
                    endpoint_group=endpoint_group,
                    status=Subscription.SubscriptionStatus.ACTIVE,
                    expires_at__gt=timezone.now()
                ).first()
                
                if existing:
                    return ServiceOperationResult(
                        success=False,
                        error_message=f"User already has active subscription for '{subscription_data['endpoint_group_name']}'"
                    )
                
                # Create subscription
                subscription = Subscription.objects.create(
                    user=user,
                    endpoint_group=endpoint_group,
                    tier=Subscription.SubscriptionTier.BASIC,
                    status=Subscription.SubscriptionStatus.ACTIVE,
                    monthly_price=endpoint_group.basic_price,
                    usage_limit=endpoint_group.basic_limit,
                    usage_current=0,
                    expires_at=timezone.now() + timedelta(days=30),
                    next_billing=timezone.now() + timedelta(days=30)
                )
                
                # Log subscription creation
                logger.info(
                    f"New subscription created: {subscription_data['endpoint_group_name']} "
                    f"for user {user.email} (expires: {subscription.expires_at})"
                )
                
                
                return ServiceOperationResult(
                    success=True,
                    data={'subscription_id': str(subscription.id)}
                )
                
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}", exc_info=True)
            
            return ServiceOperationResult(
                success=False,
                error_message=f"Internal error: {str(e)}"
            )
    
    def check_endpoint_access(
        self,
        user: User,
        endpoint_group_name: str,
        use_cache: bool = True
    ) -> AccessCheck:
        """
        Check if user has access to endpoint group.
        
        Args:
            user: User object
            endpoint_group_name: Name of endpoint group
            use_cache: Whether to use Redis cache
            
        Returns:
            AccessCheck with access status and details
        """
        try:
            # Try cache first
            if use_cache:
                cache_key = f"access:{user.id}:{endpoint_group_name}"
                cached = self.cache.get_cache(cache_key)
                if cached:
                    return AccessCheck(**cached)
            
            # Check active subscription
            subscription = Subscription.objects.filter(
                user=user,
                endpoint_group__name=endpoint_group_name,
                status=Subscription.Status.ACTIVE,
                expires_at__gt=timezone.now()
            ).select_related('endpoint_group', 'tariff').first()
            
            if not subscription:
                result = AccessCheck(
                    allowed=False,
                    reason='no_active_subscription',
                    required_subscription=endpoint_group_name
                )
            elif not subscription.can_make_request():
                result = AccessCheck(
                    allowed=False,
                    reason='usage_limit_exceeded',
                    subscription_id=str(subscription.id),
                    current_usage=subscription.current_usage,
                    monthly_limit=subscription.get_monthly_limit()
                )
            else:
                result = AccessCheck(
                    allowed=True,
                    subscription_id=str(subscription.id),
                    remaining_requests=subscription.remaining_requests(),
                    usage_percentage=subscription.usage_percentage
                )
            
            # Cache result for 1 minute
            if use_cache:
                cache_data = result.dict()
                self.cache.set_cache(f"access:{user.id}:{endpoint_group_name}", cache_data, ttl=60)
            
            return result
            
        except Exception as e:
            logger.error(f"Access check failed for user {user.id}, endpoint {endpoint_group_name}: {e}")
            return AccessCheck(
                allowed=False,
                reason='check_failed'
            )
    
    def record_api_usage(
        self,
        user: User,
        endpoint_group_name: str,
        usage_count: int = 1
    ) -> bool:
        """
        Record API usage for user's subscription.
        
        Args:
            user: User object
            endpoint_group_name: Name of endpoint group
            usage_count: Number of requests to record
            
        Returns:
            True if usage was recorded, False otherwise
        """
        try:
            with transaction.atomic():
                subscription = Subscription.objects.filter(
                    user=user,
                    endpoint_group__name=endpoint_group_name,
                    status=Subscription.Status.ACTIVE,
                    expires_at__gt=timezone.now()
                ).first()
                
                if not subscription:
                    logger.warning(f"No active subscription found for user {user.id}, endpoint {endpoint_group_name}")
                    return False
                
                # Update usage
                subscription.current_usage += usage_count
                subscription.save(update_fields=['current_usage', 'updated_at'])
                
                # Invalidate access cache
                self.cache.delete_key(f"access:{user.id}:{endpoint_group_name}")
                
                return True
                
        except Exception as e:
            logger.error(f"Usage recording failed for user {user.id}: {e}")
            return False
    
    def get_user_subscriptions(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List['SubscriptionInfo']:
        """
        Get user's subscriptions.
        
        Args:
            user_id: User ID
            active_only: Return only active subscriptions
            
        Returns:
            List of subscription dictionaries
        """
        try:
            
            # Query subscriptions
            queryset = Subscription.objects.filter(user_id=user_id)
            
            if active_only:
                queryset = queryset.filter(
                    status=Subscription.SubscriptionStatus.ACTIVE,
                    expires_at__gt=timezone.now()
                )
            
            subscriptions = queryset.select_related(
                'endpoint_group'
            ).order_by('-created_at')
            
            result = [
                SubscriptionInfo(
                    id=str(sub.id),
                    endpoint_group=EndpointGroupInfo(
                        id=str(sub.endpoint_group.id),
                        name=sub.endpoint_group.name,
                        display_name=sub.endpoint_group.display_name
                    ),
                    status=sub.status,
                    tier=sub.tier,
                    monthly_price=Decimal(str(sub.monthly_price)),
                    usage_current=sub.usage_current,
                    usage_limit=sub.usage_limit,
                    usage_percentage=sub.usage_current / sub.usage_limit if sub.usage_limit else 0.0,
                    remaining_requests=sub.usage_limit - sub.usage_current if sub.usage_limit else 0,
                    expires_at=sub.expires_at,
                    next_billing=sub.next_billing,
                    created_at=sub.created_at
                )
                for sub in subscriptions
            ]
            
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting subscriptions for user {user_id}: {e}")
            return []
    
    def cancel_subscription(
        self,
        user: User,
        subscription_id: str,
        reason: str = 'user_request'
    ) -> SubscriptionResult:
        """
        Cancel user subscription.
        
        Args:
            user: User object
            subscription_id: Subscription UUID
            reason: Cancellation reason
            
        Returns:
            SubscriptionResult with cancellation status
        """
        try:
            with transaction.atomic():
                subscription = Subscription.objects.filter(
                    id=subscription_id,
                    user=user,
                    status=Subscription.Status.ACTIVE
                ).first()
                
                if not subscription:
                    return SubscriptionResult(
                        success=False,
                        error_code='SUBSCRIPTION_NOT_FOUND',
                        error_message="Active subscription not found"
                    )
                
                # Cancel subscription
                subscription.status = Subscription.Status.CANCELLED
                subscription.auto_renew = False
                subscription.next_billing_at = None
                subscription.metadata = {
                    **subscription.metadata,
                    'cancellation_reason': reason,
                    'cancelled_at': timezone.now().isoformat()
                }
                subscription.save()
                
                
                return SubscriptionResult(
                    success=True,
                    subscription_id=str(subscription.id)
                )
                
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}", exc_info=True)
            return SubscriptionResult(
                success=False,
                error_code='INTERNAL_ERROR',
                error_message=f"Cancellation failed: {str(e)}"
            )
    
    def renew_subscription(
        self,
        subscription_id: str,
        billing_period: Optional[str] = None
    ) -> SubscriptionResult:
        """
        Renew expired or expiring subscription.
        
        Args:
            subscription_id: Subscription UUID
            billing_period: New billing period (optional)
            
        Returns:
            SubscriptionResult with renewal status
        """
        try:
            with transaction.atomic():
                subscription = Subscription.objects.filter(
                    id=subscription_id
                ).first()
                
                if not subscription:
                    return SubscriptionResult(
                        success=False,
                        error_code='SUBSCRIPTION_NOT_FOUND',
                        error_message="Subscription not found"
                    )
                
                # Calculate new expiry based on billing period
                now = timezone.now()
                if billing_period == 'yearly':
                    new_expiry = now + timedelta(days=365)
                else:  # Default to monthly
                    new_expiry = now + timedelta(days=30)
                
                # Update subscription using correct enum
                subscription.expires_at = new_expiry
                subscription.next_billing = new_expiry
                subscription.status = subscription.SubscriptionStatus.ACTIVE  # Use proper enum
                subscription.usage_current = 0  # Reset usage counter
                subscription.save()
                
                
                return SubscriptionResult(
                    success=True,
                    subscription_id=str(subscription.id),
                    expires_at=subscription.expires_at
                )
                
        except Exception as e:
            logger.error(f"Subscription renewal failed: {e}", exc_info=True)
            return SubscriptionResult(
                success=False,
                error_code='INTERNAL_ERROR',
                error_message=f"Renewal failed: {str(e)}"
            )
    
    
    def get_subscription_analytics(
        self,
        user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get subscription analytics for user.
        
        Args:
            user: User object
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Analytics data dictionary
        """
        try:
            if not start_date:
                start_date = timezone.now() - timedelta(days=30)
            if not end_date:
                end_date = timezone.now()
            
            # Get subscriptions in date range
            subscriptions = Subscription.objects.filter(
                user=user,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).select_related('endpoint_group')
            
            # Calculate analytics
            total_subscriptions = subscriptions.count()
            active_subscriptions = subscriptions.filter(
                status=Subscription.Status.ACTIVE,
                expires_at__gt=timezone.now()
            ).count()
            
            usage_by_endpoint = {}
            for sub in subscriptions:
                endpoint_name = sub.endpoint_group.name
                if endpoint_name not in usage_by_endpoint:
                    usage_by_endpoint[endpoint_name] = {
                        'usage': 0,
                        'limit': 0,
                        'percentage': 0
                    }
                usage_by_endpoint[endpoint_name]['usage'] += sub.current_usage
                usage_by_endpoint[endpoint_name]['limit'] += sub.get_monthly_limit()
            
            # Calculate usage percentages
            for endpoint_data in usage_by_endpoint.values():
                if endpoint_data['limit'] > 0:
                    endpoint_data['percentage'] = (endpoint_data['usage'] / endpoint_data['limit']) * 100
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_subscriptions': total_subscriptions,
                    'active_subscriptions': active_subscriptions,
                    'cancelled_subscriptions': subscriptions.filter(
                        status=Subscription.Status.CANCELLED
                    ).count()
                },
                'usage_by_endpoint': usage_by_endpoint,
                'total_usage': sum(data['usage'] for data in usage_by_endpoint.values()),
                'total_limit': sum(data['limit'] for data in usage_by_endpoint.values())
            }
            
        except Exception as e:
            logger.error(f"Analytics calculation failed for user {user.id}: {e}")
            return {
                'error': str(e),
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
    
    def check_access(
        self,
        user_id: int,
        endpoint_group: str,
        increment_usage: bool = False
    ) -> Dict[str, Any]:
        """
        Check if user has access to endpoint group.
        
        Args:
            user_id: User ID
            endpoint_group: Endpoint group name
            increment_usage: Whether to increment usage count
            
        Returns:
            Access check result
        """
        try:
            subscription = Subscription.objects.select_related('endpoint_group').get(
                user_id=user_id,
                endpoint_group__name=endpoint_group,
                status=Subscription.SubscriptionStatus.ACTIVE,
                expires_at__gt=timezone.now()
            )
            
            # Check usage limit
            if subscription.usage_limit and subscription.usage_current >= subscription.usage_limit:
                return {
                    'has_access': False,
                    'reason': 'usage_limit_exceeded',
                    'usage_current': subscription.usage_current,
                    'usage_limit': subscription.usage_limit
                }
            
            # Increment usage if requested
            if increment_usage:
                subscription.usage_current += 1
                subscription.save(update_fields=['usage_current'])
            
            return {
                'has_access': True,
                'subscription_id': str(subscription.id),
                'usage_current': subscription.usage_current,
                'usage_limit': subscription.usage_limit,
                'remaining_requests': subscription.usage_limit - subscription.usage_current if subscription.usage_limit else None
            }
            
        except Subscription.DoesNotExist:
            return {
                'has_access': False,
                'reason': 'no_active_subscription'
            }
        except Exception as e:
            logger.error(f"Error checking access for user {user_id}, endpoint {endpoint_group}: {e}")
            return {
                'has_access': False,
                'reason': 'internal_error'
            }
    
    def increment_usage(
        self,
        user_id: int,
        endpoint_group: str,
        amount: int = 1
    ) -> 'ServiceOperationResult':
        """
        Increment usage for user's subscription.
        
        Args:
            user_id: User ID
            endpoint_group: Endpoint group name
            amount: Amount to increment
            
        Returns:
            Usage increment result
        """
        try:
            subscription = Subscription.objects.select_related('endpoint_group').get(
                user_id=user_id,
                endpoint_group__name=endpoint_group,
                status=Subscription.SubscriptionStatus.ACTIVE,
                expires_at__gt=timezone.now()
            )
            
            subscription.usage_current += amount
            subscription.save(update_fields=['usage_current'])
            
            
            return ServiceOperationResult(
                success=True,
                data={
                    'usage_current': subscription.usage_current,
                    'usage_limit': subscription.usage_limit,
                    'remaining_requests': subscription.usage_limit - subscription.usage_current if subscription.usage_limit else None
                }
            )
            
        except Subscription.DoesNotExist:
            return ServiceOperationResult(
                success=False,
                error_message='no_active_subscription'
            )
        except Exception as e:
            logger.error(f"Error incrementing usage for user {user_id}, endpoint {endpoint_group}: {e}")
            return ServiceOperationResult(
                success=False,
                error_message='internal_error'
            )
