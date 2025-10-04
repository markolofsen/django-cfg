"""
Subscription service for the Universal Payment System v2.0.

Handles subscription management and access control.
"""

from typing import Optional, Dict, Any, List
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .base import BaseService
from ..types import (
    SubscriptionCreateRequest, SubscriptionResult, SubscriptionData,
    ServiceOperationResult
)
from ...models import Subscription, EndpointGroup, Tariff


class SubscriptionService(BaseService):
    """
    Subscription service with business logic and validation.
    
    Handles subscription operations using Pydantic validation and Django ORM managers.
    """
    
    def create_subscription(self, request: SubscriptionCreateRequest) -> SubscriptionResult:
        """
        Create new subscription for user.
        
        Args:
            request: Subscription creation request with validation
            
        Returns:
            SubscriptionResult: Created subscription information
        """
        try:
            # Validate request
            if isinstance(request, dict):
                request = SubscriptionCreateRequest(**request)
            
            self.logger.info("Creating subscription", extra={
                'user_id': request.user_id,
                'tier': request.tier,
                'duration_days': request.duration_days
            })
            
            # Get user
            try:
                user = User.objects.get(id=request.user_id)
            except User.DoesNotExist:
                return SubscriptionResult(
                    success=False,
                    message=f"User {request.user_id} not found",
                    error_code="user_not_found"
                )
            
            # Get tariff for tier
            try:
                tariff = Tariff.objects.get(tier=request.tier, is_active=True)
            except Tariff.DoesNotExist:
                return SubscriptionResult(
                    success=False,
                    message=f"Tariff for tier {request.tier} not found",
                    error_code="tariff_not_found"
                )
            
            # Cancel existing active subscriptions
            existing_active = Subscription.objects.filter(
                user=user,
                status=Subscription.SubscriptionStatus.ACTIVE
            )
            
            def create_subscription_transaction():
                # Cancel existing subscriptions
                for sub in existing_active:
                    sub.cancel("Replaced by new subscription")
                
                # Create new subscription
                expires_at = timezone.now() + timedelta(days=request.duration_days)
                
                subscription = Subscription.objects.create(
                    user=user,
                    tier=request.tier,
                    status=Subscription.SubscriptionStatus.ACTIVE,
                    requests_per_hour=tariff.requests_per_hour,
                    requests_per_day=tariff.requests_per_day,
                    monthly_cost_usd=tariff.monthly_price_usd,
                    auto_renew=request.auto_renew,
                    expires_at=expires_at
                )
                
                # Add endpoint groups
                if request.endpoint_groups:
                    endpoint_groups = EndpointGroup.objects.filter(
                        code__in=request.endpoint_groups,
                        is_enabled=True
                    )
                    subscription.endpoint_groups.set(endpoint_groups)
                else:
                    # Add default endpoint groups for tier
                    default_groups = self._get_default_endpoint_groups(request.tier)
                    subscription.endpoint_groups.set(default_groups)
                
                return subscription
            
            subscription = self._execute_with_transaction(create_subscription_transaction)
            
            # Convert to response data
            subscription_data = SubscriptionData.model_validate(subscription)
            
            self._log_operation(
                "create_subscription",
                True,
                subscription_id=str(subscription.id),
                user_id=request.user_id,
                tier=request.tier
            )
            
            return SubscriptionResult(
                success=True,
                message="Subscription created successfully",
                subscription_id=str(subscription.id),
                user_id=request.user_id,
                tier=subscription.tier,
                status=subscription.status,
                expires_at=subscription.expires_at,
                data={'subscription': subscription_data.model_dump()}
            )
            
        except Exception as e:
            return SubscriptionResult(**self._handle_exception(
                "create_subscription", e,
                user_id=request.user_id if hasattr(request, 'user_id') else None
            ).model_dump())
    
    def get_user_subscription(self, user_id: int) -> SubscriptionResult:
        """
        Get active subscription for user.
        
        Args:
            user_id: User ID
            
        Returns:
            SubscriptionResult: Active subscription or free tier
        """
        try:
            self.logger.debug("Getting user subscription", extra={'user_id': user_id})
            
            # Check user exists
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return SubscriptionResult(
                    success=False,
                    message=f"User {user_id} not found",
                    error_code="user_not_found"
                )
            
            # Get active subscription
            subscription = Subscription.objects.get_active_for_user(user)
            
            if not subscription:
                # Create free subscription if none exists
                subscription = Subscription.objects.create_free_subscription(user)
            
            # Convert to response data
            subscription_data = SubscriptionData.model_validate(subscription)
            
            # Calculate requests remaining
            requests_remaining = self._calculate_requests_remaining(subscription)
            
            return SubscriptionResult(
                success=True,
                message="Subscription retrieved successfully",
                subscription_id=str(subscription.id),
                user_id=user_id,
                tier=subscription.tier,
                status=subscription.status,
                expires_at=subscription.expires_at,
                requests_remaining=requests_remaining,
                data={'subscription': subscription_data.model_dump()}
            )
            
        except Exception as e:
            return SubscriptionResult(**self._handle_exception(
                "get_user_subscription", e,
                user_id=user_id
            ).model_dump())
    
    def check_access(self, user_id: int, endpoint_group: str) -> ServiceOperationResult:
        """
        Check if user has access to endpoint group.
        
        Args:
            user_id: User ID
            endpoint_group: Endpoint group code
            
        Returns:
            ServiceOperationResult: Access check result
        """
        try:
            self.logger.debug("Checking endpoint access", extra={
                'user_id': user_id,
                'endpoint_group': endpoint_group
            })
            
            # Get user subscription
            subscription_result = self.get_user_subscription(user_id)
            if not subscription_result.success:
                return self._create_error_result(
                    subscription_result.message,
                    subscription_result.error_code
                )
            
            subscription = Subscription.objects.get(id=subscription_result.subscription_id)
            
            # Check if subscription is active and not expired
            if not subscription.is_active():
                return self._create_error_result(
                    "Subscription is not active",
                    "subscription_inactive"
                )
            
            # Check endpoint group access
            has_access = subscription.has_access_to_endpoint_group(endpoint_group)
            
            if not has_access:
                return self._create_error_result(
                    f"Access denied to endpoint group: {endpoint_group}",
                    "access_denied"
                )
            
            # Check rate limits
            rate_limit_result = self._check_rate_limits(subscription)
            if not rate_limit_result.success:
                return rate_limit_result
            
            return self._create_success_result(
                "Access granted",
                {
                    'user_id': user_id,
                    'endpoint_group': endpoint_group,
                    'subscription_id': str(subscription.id),
                    'tier': subscription.tier,
                    'requests_remaining': self._calculate_requests_remaining(subscription)
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "check_access", e,
                user_id=user_id,
                endpoint_group=endpoint_group
            )
    
    def increment_usage(self, user_id: int) -> ServiceOperationResult:
        """
        Increment subscription usage counter.
        
        Args:
            user_id: User ID
            
        Returns:
            ServiceOperationResult: Usage increment result
        """
        try:
            # Get user subscription
            subscription_result = self.get_user_subscription(user_id)
            if not subscription_result.success:
                return self._create_error_result(
                    subscription_result.message,
                    subscription_result.error_code
                )
            
            subscription = Subscription.objects.get(id=subscription_result.subscription_id)
            
            # Increment usage using manager
            success = subscription.increment_usage()
            
            if success:
                return self._create_success_result(
                    "Usage incremented successfully",
                    {
                        'user_id': user_id,
                        'subscription_id': str(subscription.id),
                        'total_requests': subscription.total_requests,
                        'requests_remaining': self._calculate_requests_remaining(subscription)
                    }
                )
            else:
                return self._create_error_result(
                    "Failed to increment usage",
                    "increment_failed"
                )
                
        except Exception as e:
            return self._handle_exception(
                "increment_usage", e,
                user_id=user_id
            )
    
    def renew_subscription(self, subscription_id: str, duration_days: int = 30) -> SubscriptionResult:
        """
        Renew existing subscription.
        
        Args:
            subscription_id: Subscription ID
            duration_days: Renewal duration in days
            
        Returns:
            SubscriptionResult: Renewal result
        """
        try:
            self.logger.info("Renewing subscription", extra={
                'subscription_id': subscription_id,
                'duration_days': duration_days
            })
            
            # Get subscription
            try:
                subscription = Subscription.objects.get(id=subscription_id)
            except Subscription.DoesNotExist:
                return SubscriptionResult(
                    success=False,
                    message=f"Subscription {subscription_id} not found",
                    error_code="subscription_not_found"
                )
            
            # Renew using manager
            success = subscription.renew(duration_days)
            
            if success:
                subscription.refresh_from_db()
                subscription_data = SubscriptionData.model_validate(subscription)
                
                self._log_operation(
                    "renew_subscription",
                    True,
                    subscription_id=subscription_id,
                    duration_days=duration_days,
                    new_expires_at=subscription.expires_at.isoformat()
                )
                
                return SubscriptionResult(
                    success=True,
                    message="Subscription renewed successfully",
                    subscription_id=str(subscription.id),
                    user_id=subscription.user.id,
                    tier=subscription.tier,
                    status=subscription.status,
                    expires_at=subscription.expires_at,
                    data={'subscription': subscription_data.model_dump()}
                )
            else:
                return SubscriptionResult(
                    success=False,
                    message="Failed to renew subscription",
                    error_code="renewal_failed"
                )
                
        except Exception as e:
            return SubscriptionResult(**self._handle_exception(
                "renew_subscription", e,
                subscription_id=subscription_id
            ).model_dump())
    
    def cancel_subscription(self, subscription_id: str, reason: str = None) -> SubscriptionResult:
        """
        Cancel subscription.
        
        Args:
            subscription_id: Subscription ID
            reason: Cancellation reason
            
        Returns:
            SubscriptionResult: Cancellation result
        """
        try:
            self.logger.info("Cancelling subscription", extra={
                'subscription_id': subscription_id,
                'reason': reason
            })
            
            # Get subscription
            try:
                subscription = Subscription.objects.get(id=subscription_id)
            except Subscription.DoesNotExist:
                return SubscriptionResult(
                    success=False,
                    message=f"Subscription {subscription_id} not found",
                    error_code="subscription_not_found"
                )
            
            # Cancel using manager
            success = subscription.cancel(reason)
            
            if success:
                subscription.refresh_from_db()
                subscription_data = SubscriptionData.model_validate(subscription)
                
                self._log_operation(
                    "cancel_subscription",
                    True,
                    subscription_id=subscription_id,
                    reason=reason
                )
                
                return SubscriptionResult(
                    success=True,
                    message="Subscription cancelled successfully",
                    subscription_id=str(subscription.id),
                    user_id=subscription.user.id,
                    tier=subscription.tier,
                    status=subscription.status,
                    data={'subscription': subscription_data.model_dump()}
                )
            else:
                return SubscriptionResult(
                    success=False,
                    message="Failed to cancel subscription",
                    error_code="cancellation_failed"
                )
                
        except Exception as e:
            return SubscriptionResult(**self._handle_exception(
                "cancel_subscription", e,
                subscription_id=subscription_id
            ).model_dump())
    
    def get_subscription_stats(self, days: int = 30) -> ServiceOperationResult:
        """
        Get subscription statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            ServiceOperationResult: Subscription statistics
        """
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Overall stats
            overall_stats = Subscription.objects.aggregate(
                total_subscriptions=models.Count('id'),
                active_subscriptions=models.Count(
                    'id',
                    filter=models.Q(status=Subscription.SubscriptionStatus.ACTIVE)
                ),
                expired_subscriptions=models.Count(
                    'id',
                    filter=models.Q(status=Subscription.SubscriptionStatus.EXPIRED)
                ),
                cancelled_subscriptions=models.Count(
                    'id',
                    filter=models.Q(status=Subscription.SubscriptionStatus.CANCELLED)
                )
            )
            
            # Tier breakdown
            tier_breakdown = Subscription.objects.values('tier').annotate(
                count=models.Count('id'),
                active_count=models.Count(
                    'id',
                    filter=models.Q(status=Subscription.SubscriptionStatus.ACTIVE)
                )
            ).order_by('-count')
            
            # Recent activity
            recent_stats = Subscription.objects.filter(
                created_at__gte=since
            ).aggregate(
                new_subscriptions=models.Count('id'),
                total_requests=models.Sum('total_requests'),
                avg_requests=models.Avg('total_requests')
            )
            
            stats = {
                'period_days': days,
                'overall_stats': overall_stats,
                'tier_breakdown': list(tier_breakdown),
                'recent_stats': recent_stats,
                'generated_at': timezone.now().isoformat()
            }
            
            return self._create_success_result(
                f"Subscription statistics for {days} days",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("get_subscription_stats", e)
    
    def _get_default_endpoint_groups(self, tier: str) -> List[EndpointGroup]:
        """Get default endpoint groups for subscription tier."""
        tier_groups = {
            'free': ['payments', 'balance'],
            'basic': ['payments', 'balance', 'subscriptions'],
            'pro': ['payments', 'balance', 'subscriptions', 'analytics'],
            'enterprise': ['payments', 'balance', 'subscriptions', 'analytics', 'admin']
        }
        
        group_codes = tier_groups.get(tier, ['payments'])
        return EndpointGroup.objects.filter(
            code__in=group_codes,
            is_enabled=True
        )
    
    def _calculate_requests_remaining(self, subscription: Subscription) -> int:
        """Calculate remaining requests for today."""
        # Simple calculation - in production this would check daily usage
        return max(0, subscription.requests_per_day - subscription.total_requests)
    
    def _check_rate_limits(self, subscription: Subscription) -> ServiceOperationResult:
        """Check if subscription has exceeded rate limits."""
        # Simplified rate limit check
        if subscription.total_requests >= subscription.requests_per_day:
            return self._create_error_result(
                "Daily request limit exceeded",
                "rate_limit_exceeded"
            )
        
        return self._create_success_result("Rate limits OK")
    
    def health_check(self) -> ServiceOperationResult:
        """Perform subscription service health check."""
        try:
            # Check database connectivity
            subscription_count = Subscription.objects.count()
            active_count = Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.ACTIVE
            ).count()
            
            # Check for expired subscriptions that need cleanup
            expired_count = Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.ACTIVE,
                expires_at__lt=timezone.now()
            ).count()
            
            stats = {
                'total_subscriptions': subscription_count,
                'active_subscriptions': active_count,
                'expired_needing_cleanup': expired_count,
                'service_name': 'SubscriptionService'
            }
            
            return self._create_success_result(
                "SubscriptionService is healthy",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("health_check", e)
