"""
Subscription managers for the Universal Payment System v2.0.

Optimized querysets and managers for subscription and endpoint group operations.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django_cfg.modules.django_logger import get_logger

logger = get_logger("subscription_managers")


class SubscriptionQuerySet(models.QuerySet):
    """
    Optimized queryset for subscription operations.
    
    Provides efficient queries for subscription management and access control.
    """
    
    def optimized(self):
        """Prevent N+1 queries with select_related and prefetch_related."""
        return self.select_related('user').prefetch_related('endpoint_groups')
    
    def by_user(self, user):
        """Filter subscriptions by user."""
        return self.filter(user=user)
    
    def by_tier(self, tier):
        """Filter by subscription tier."""
        return self.filter(tier=tier)
    
    def by_status(self, status):
        """Filter by subscription status."""
        return self.filter(status=status)
    
    # Status-based filters
    def active(self):
        """
        Get active subscriptions that are not expired.
        
        Returns subscriptions with status='active' and expires_at > now.
        """
        return self.filter(
            status='active',
            expires_at__gt=timezone.now()
        )
    
    def inactive(self):
        """Get inactive subscriptions."""
        return self.filter(status='inactive')
    
    def suspended(self):
        """Get suspended subscriptions."""
        return self.filter(status='suspended')
    
    def cancelled(self):
        """Get cancelled subscriptions."""
        return self.filter(status='cancelled')
    
    def expired(self):
        """
        Get expired subscriptions.
        
        Returns subscriptions where expires_at <= now, regardless of status.
        """
        return self.filter(expires_at__lte=timezone.now())
    
    def expiring_soon(self, days=7):
        """
        Get subscriptions expiring in the next N days.
        
        Args:
            days: Number of days to look ahead (default: 7)
        """
        soon = timezone.now() + timedelta(days=days)
        return self.filter(
            expires_at__lte=soon,
            expires_at__gt=timezone.now(),
            status='active'
        )
    
    # Tier-based filters
    def free_tier(self):
        """Get free tier subscriptions."""
        return self.filter(tier='free')
    
    def basic_tier(self):
        """Get basic tier subscriptions."""
        return self.filter(tier='basic')
    
    def pro_tier(self):
        """Get pro tier subscriptions."""
        return self.filter(tier='pro')
    
    def enterprise_tier(self):
        """Get enterprise tier subscriptions."""
        return self.filter(tier='enterprise')
    
    def paid_tiers(self):
        """Get paid tier subscriptions (non-free)."""
        return self.exclude(tier='free')
    
    # Time-based filters
    def created_recently(self, days=30):
        """
        Get subscriptions created in the last N days.
        
        Args:
            days: Number of days to look back (default: 30)
        """
        since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=since)
    
    def renewed_recently(self, days=30):
        """
        Get subscriptions renewed in the last N days.
        
        Args:
            days: Number of days to look back (default: 30)
        """
        since = timezone.now() - timedelta(days=days)
        return self.filter(updated_at__gte=since, status='active')
    
    # Usage-based filters
    def with_usage(self):
        """Get subscriptions that have been used (total_requests > 0)."""
        return self.filter(total_requests__gt=0)
    
    def without_usage(self):
        """Get subscriptions that have never been used."""
        return self.filter(total_requests=0)
    
    def high_usage(self, threshold=1000):
        """
        Get subscriptions with high usage.
        
        Args:
            threshold: Request count threshold (default: 1000)
        """
        return self.filter(total_requests__gte=threshold)
    
    def recent_usage(self, hours=24):
        """
        Get subscriptions used in the last N hours.
        
        Args:
            hours: Number of hours to look back (default: 24)
        """
        since = timezone.now() - timedelta(hours=hours)
        return self.filter(last_request_at__gte=since)
    
    # Auto-renewal filters
    def auto_renewing(self):
        """Get subscriptions with auto-renewal enabled."""
        return self.filter(auto_renew=True)
    
    def manual_renewal(self):
        """Get subscriptions with manual renewal."""
        return self.filter(auto_renew=False)
    
    # Endpoint access filters
    def with_endpoint_access(self, endpoint_group_code):
        """
        Get subscriptions with access to specific endpoint group.
        
        Args:
            endpoint_group_code: Endpoint group code to check
        """
        return self.filter(
            endpoint_groups__code=endpoint_group_code,
            endpoint_groups__is_enabled=True
        )
    
    # Aggregation methods
    def total_revenue(self):
        """Get total monthly revenue from active subscriptions."""
        result = self.active().aggregate(total=models.Sum('monthly_cost_usd'))
        return result['total'] or 0.0
    
    def average_cost(self):
        """Get average monthly cost."""
        result = self.aggregate(avg=models.Avg('monthly_cost_usd'))
        return result['avg'] or 0.0
    
    def count_by_tier(self):
        """Get count of subscriptions grouped by tier."""
        return self.values('tier').annotate(count=models.Count('id')).order_by('tier')
    
    def count_by_status(self):
        """Get count of subscriptions grouped by status."""
        return self.values('status').annotate(count=models.Count('id')).order_by('status')
    
    def usage_stats(self):
        """Get usage statistics."""
        return self.aggregate(
            total_requests=models.Sum('total_requests'),
            avg_requests=models.Avg('total_requests'),
            max_requests=models.Max('total_requests'),
            active_users=models.Count('user', distinct=True)
        )


class SubscriptionManager(models.Manager):
    """
    Manager for subscription operations with business logic.
    
    Provides high-level methods for subscription management and access control.
    """
    
    def get_queryset(self):
        """Return optimized queryset by default."""
        return SubscriptionQuerySet(self.model, using=self._db)
    
    def optimized(self):
        """Get optimized queryset."""
        return self.get_queryset().optimized()
    
    # Status-based methods
    def active(self):
        """Get active subscriptions."""
        return self.get_queryset().active()
    
    def expired(self):
        """Get expired subscriptions."""
        return self.get_queryset().expired()
    
    def expiring_soon(self, days=7):
        """Get subscriptions expiring soon."""
        return self.get_queryset().expiring_soon(days)
    
    # Tier-based methods
    def by_tier(self, tier):
        """Get subscriptions by tier."""
        return self.get_queryset().by_tier(tier)
    
    def free_tier(self):
        """Get free tier subscriptions."""
        return self.get_queryset().free_tier()
    
    def paid_tiers(self):
        """Get paid tier subscriptions."""
        return self.get_queryset().paid_tiers()
    
    # User methods
    def get_active_for_user(self, user):
        """
        Get active subscription for user.
        
        Args:
            user: User instance
        
        Returns:
            Subscription or None: Active subscription if exists
        """
        try:
            return self.active().get(user=user)
        except self.model.DoesNotExist:
            return None
    
    def has_active_subscription(self, user):
        """
        Check if user has an active subscription.
        
        Args:
            user: User instance
        
        Returns:
            bool: True if user has active subscription
        """
        return self.active().filter(user=user).exists()
    
    def get_or_create_free_subscription(self, user):
        """
        Get existing subscription or create free tier subscription for user.
        
        Args:
            user: User instance
        
        Returns:
            tuple: (Subscription, created)
        """
        # Check for existing active subscription
        existing = self.get_active_for_user(user)
        if existing:
            return existing, False
        
        # Create free subscription
        subscription = self.model.create_free_subscription(user)
        
        logger.info(f"Created free subscription for user", extra={
            'user_id': user.id,
            'subscription_id': str(subscription.id)
        })
        
        return subscription, True
    
    # Access control methods
    def check_endpoint_access(self, user, endpoint_group_code):
        """
        Check if user has access to specific endpoint group.
        
        Args:
            user: User instance
            endpoint_group_code: Endpoint group code to check
        
        Returns:
            bool: True if user has access
        """
        subscription = self.get_active_for_user(user)
        if not subscription:
            return False
        
        return subscription.has_access_to_endpoint_group(endpoint_group_code)
    
    def get_user_rate_limits(self, user):
        """
        Get rate limits for user based on their subscription.
        
        Args:
            user: User instance
        
        Returns:
            dict: Rate limit information
        """
        subscription = self.get_active_for_user(user)
        if not subscription:
            return {
                'requests_per_hour': 0,
                'requests_per_day': 0,
                'has_access': False
            }
        
        return {
            'requests_per_hour': subscription.requests_per_hour,
            'requests_per_day': subscription.requests_per_day,
            'has_access': True,
            'tier': subscription.tier,
            'expires_at': subscription.expires_at
        }
    
    # Maintenance methods
    def cleanup_expired(self, dry_run=True):
        """
        Mark expired subscriptions as expired status.
        
        Args:
            dry_run: If True, only return count without making changes
        
        Returns:
            int: Number of subscriptions that would be/were updated
        """
        expired_subscriptions = self.filter(
            expires_at__lte=timezone.now(),
            status__in=['active', 'suspended']
        )
        count = expired_subscriptions.count()
        
        if not dry_run and count > 0:
            expired_subscriptions.update(status='expired')
            logger.info(f"Marked {count} subscriptions as expired")
        
        return count
    
    def process_auto_renewals(self, dry_run=True):
        """
        Process auto-renewal for subscriptions expiring soon.
        
        Args:
            dry_run: If True, only return count without making changes
        
        Returns:
            int: Number of subscriptions that would be/were renewed
        """
        # Get subscriptions expiring in the next 24 hours with auto-renewal
        expiring_subscriptions = self.filter(
            expires_at__lte=timezone.now() + timedelta(hours=24),
            expires_at__gt=timezone.now(),
            auto_renew=True,
            status='active'
        )
        
        count = expiring_subscriptions.count()
        
        if not dry_run and count > 0:
            for subscription in expiring_subscriptions:
                try:
                    subscription.renew(duration_days=30)
                    logger.info(f"Auto-renewed subscription", extra={
                        'subscription_id': str(subscription.id),
                        'user_id': subscription.user.id
                    })
                except Exception as e:
                    logger.error(f"Failed to auto-renew subscription: {e}", extra={
                        'subscription_id': str(subscription.id),
                        'user_id': subscription.user.id
                    })
        
        return count
    
    # Statistics methods
    def get_subscription_stats(self, days=30):
        """
        Get subscription statistics for the last N days.
        
        Args:
            days: Number of days to analyze (default: 30)
        
        Returns:
            dict: Subscription statistics
        """
        queryset = self.get_queryset()
        recent_queryset = queryset.created_recently(days)
        
        stats = {
            'total_subscriptions': queryset.count(),
            'active_subscriptions': queryset.active().count(),
            'expired_subscriptions': queryset.expired().count(),
            'new_subscriptions': recent_queryset.count(),
            'total_revenue': queryset.total_revenue(),
            'average_cost': queryset.average_cost(),
            'by_tier': list(queryset.count_by_tier()),
            'by_status': list(queryset.count_by_status()),
            'usage_stats': queryset.usage_stats(),
            'auto_renewing': queryset.auto_renewing().count(),
            'expiring_soon': queryset.expiring_soon(7).count(),
        }
        
        logger.info(f"Generated subscription stats for {days} days", extra={
            'days': days,
            'total_subscriptions': stats['total_subscriptions'],
            'active_subscriptions': stats['active_subscriptions']
        })
        
        return stats
    
    def get_tier_analytics(self):
        """
        Get detailed analytics by subscription tier.
        
        Returns:
            dict: Tier-based analytics
        """
        analytics = {}
        
        for tier_code, tier_name in self.model.SubscriptionTier.choices:
            tier_subscriptions = self.by_tier(tier_code)
            
            analytics[tier_code] = {
                'name': tier_name,
                'total_count': tier_subscriptions.count(),
                'active_count': tier_subscriptions.active().count(),
                'revenue': tier_subscriptions.total_revenue(),
                'average_usage': tier_subscriptions.aggregate(
                    avg=models.Avg('total_requests')
                )['avg'] or 0,
                'conversion_rate': 0.0  # Would need additional logic for conversion tracking
            }
        
        return analytics
    
    # Business logic methods
    def activate_subscription(self, subscription_id):
        """
        Activate subscription (business logic in manager).
        
        Args:
            subscription_id: Subscription ID or instance
        
        Returns:
            bool: True if subscription was activated successfully
        """
        try:
            if isinstance(subscription_id, str):
                subscription = self.get(id=subscription_id)
            else:
                subscription = subscription_id
            
            subscription.status = subscription.model.SubscriptionStatus.ACTIVE
            subscription.save(update_fields=['status', 'updated_at'])
            
            logger.info(f"Subscription activated", extra={
                'subscription_id': str(subscription.id),
                'user_id': subscription.user.id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate subscription: {e}", extra={
                'subscription_id': str(subscription_id) if hasattr(subscription_id, 'id') else subscription_id
            })
            return False
    
    def suspend_subscription(self, subscription_id, reason=None):
        """
        Suspend subscription (business logic in manager).
        
        Args:
            subscription_id: Subscription ID or instance
            reason: Suspension reason
        
        Returns:
            bool: True if subscription was suspended successfully
        """
        try:
            if isinstance(subscription_id, str):
                subscription = self.get(id=subscription_id)
            else:
                subscription = subscription_id
            
            subscription.status = subscription.model.SubscriptionStatus.SUSPENDED
            subscription.save(update_fields=['status', 'updated_at'])
            
            logger.warning(f"Subscription suspended", extra={
                'subscription_id': str(subscription.id),
                'user_id': subscription.user.id,
                'reason': reason
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to suspend subscription: {e}", extra={
                'subscription_id': str(subscription_id) if hasattr(subscription_id, 'id') else subscription_id
            })
            return False
    
    def cancel_subscription(self, subscription_id, reason=None):
        """
        Cancel subscription (business logic in manager).
        
        Args:
            subscription_id: Subscription ID or instance
            reason: Cancellation reason
        
        Returns:
            bool: True if subscription was cancelled successfully
        """
        try:
            if isinstance(subscription_id, str):
                subscription = self.get(id=subscription_id)
            else:
                subscription = subscription_id
            
            subscription.status = self.model.SubscriptionStatus.CANCELLED
            subscription.save(update_fields=['status', 'updated_at'])
            
            logger.info(f"Subscription cancelled", extra={
                'subscription_id': str(subscription.id),
                'user_id': subscription.user.id,
                'reason': reason
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}", extra={
                'subscription_id': str(subscription_id) if hasattr(subscription_id, 'id') else subscription_id
            })
            return False
    
    def renew_subscription(self, subscription_id, duration_days=30):
        """
        Renew subscription (business logic in manager).
        
        Args:
            subscription_id: Subscription ID or instance
            duration_days: Duration in days to extend
        
        Returns:
            bool: True if subscription was renewed successfully
        """
        try:
            if isinstance(subscription_id, str):
                subscription = self.get(id=subscription_id)
            else:
                subscription = subscription_id
            
            from datetime import timedelta
            
            if subscription.expires_at <= timezone.now():
                # If expired, start from now
                subscription.starts_at = timezone.now()
                subscription.expires_at = subscription.starts_at + timedelta(days=duration_days)
            else:
                # If not expired, extend from current expiration
                subscription.expires_at += timedelta(days=duration_days)
            
            subscription.status = self.model.SubscriptionStatus.ACTIVE
            subscription.save(update_fields=['starts_at', 'expires_at', 'status', 'updated_at'])
            
            logger.info(f"Subscription renewed", extra={
                'subscription_id': str(subscription.id),
                'user_id': subscription.user.id,
                'duration_days': duration_days,
                'new_expires_at': subscription.expires_at.isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to renew subscription: {e}", extra={
                'subscription_id': str(subscription_id) if hasattr(subscription_id, 'id') else subscription_id
            })
            return False
    
    def increment_subscription_usage(self, subscription_id):
        """
        Increment usage counter for subscription (business logic in manager).
        
        Args:
            subscription_id: Subscription ID or instance
        
        Returns:
            bool: True if usage was incremented successfully
        """
        try:
            if isinstance(subscription_id, str):
                subscription = self.get(id=subscription_id)
            else:
                subscription = subscription_id
            
            subscription.total_requests += 1
            subscription.last_request_at = timezone.now()
            subscription.save(update_fields=['total_requests', 'last_request_at', 'updated_at'])
            
            logger.debug(f"Incremented subscription usage", extra={
                'subscription_id': str(subscription.id),
                'user_id': subscription.user.id,
                'total_requests': subscription.total_requests
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment subscription usage: {e}", extra={
                'subscription_id': str(subscription_id) if hasattr(subscription_id, 'id') else subscription_id
            })
            return False
