"""
API Key managers for the Universal Payment System v2.0.

Optimized querysets and managers for API key operations.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django_cfg.modules.django_logger import get_logger

logger = get_logger("api_key_managers")


class APIKeyQuerySet(models.QuerySet):
    """
    Optimized queryset for API key operations.
    
    Provides efficient queries for API key management and validation.
    """
    
    def active(self):
        """Get active API keys."""
        return self.filter(is_active=True)
    
    def expired(self):
        """Get expired API keys."""
        now = timezone.now()
        return self.filter(expires_at__lte=now)
    
    def expiring_soon(self, days=7):
        """
        Get API keys expiring in the next N days.
        
        Args:
            days: Number of days to look ahead (default: 7)
        """
        soon = timezone.now() + timedelta(days=days)
        return self.filter(
            expires_at__lte=soon,
            expires_at__gt=timezone.now(),
            is_active=True
        )
    
    def by_user(self, user):
        """Filter API keys by user."""
        return self.filter(user=user)
    
    def valid(self):
        """Get valid API keys (active and not expired)."""
        now = timezone.now()
        return self.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )
    
    def recent_usage(self, hours=24):
        """
        Get API keys used in the last N hours.
        
        Args:
            hours: Number of hours to look back (default: 24)
        """
        since = timezone.now() - timedelta(hours=hours)
        return self.filter(last_used_at__gte=since)


class APIKeyManager(models.Manager):
    """
    Manager for API key operations with business logic.
    
    Provides high-level methods for API key management and validation.
    """
    
    def get_queryset(self):
        """Return custom queryset."""
        return APIKeyQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active API keys."""
        return self.get_queryset().active()
    
    def valid(self):
        """Get valid API keys."""
        return self.get_queryset().valid()
    
    def expired(self):
        """Get expired API keys."""
        return self.get_queryset().expired()
    
    def expiring_soon(self, days=7):
        """Get API keys expiring soon."""
        return self.get_queryset().expiring_soon(days)
    
    def by_user(self, user):
        """Get API keys by user."""
        return self.get_queryset().by_user(user)
    
    # Business logic methods
    def increment_api_key_usage(self, api_key_id, ip_address=None):
        """
        Increment API key usage counter (business logic in manager).
        
        Args:
            api_key_id: API key ID or instance
            ip_address: IP address making the request (for logging)
        
        Returns:
            bool: True if usage was incremented successfully
        """
        try:
            if isinstance(api_key_id, str):
                api_key = self.get(id=api_key_id)
            else:
                api_key = api_key_id
            
            api_key.total_requests += 1
            api_key.last_used_at = timezone.now()
            api_key.save(update_fields=['total_requests', 'last_used_at', 'updated_at'])
            
            logger.debug(f"Incremented API key usage", extra={
                'api_key_id': str(api_key.id),
                'user_id': api_key.user.id,
                'total_requests': api_key.total_requests,
                'ip_address': ip_address
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment API key usage: {e}", extra={
                'api_key_id': str(api_key_id) if hasattr(api_key_id, 'id') else api_key_id,
                'ip_address': ip_address
            })
            return False
    
    def deactivate_api_key(self, api_key_id, reason=None):
        """
        Deactivate API key (business logic in manager).
        
        Args:
            api_key_id: API key ID or instance
            reason: Deactivation reason
        
        Returns:
            bool: True if API key was deactivated successfully
        """
        try:
            if isinstance(api_key_id, str):
                api_key = self.get(id=api_key_id)
            else:
                api_key = api_key_id
            
            api_key.is_active = False
            api_key.save(update_fields=['is_active', 'updated_at'])
            
            logger.info(f"API key deactivated", extra={
                'api_key_id': str(api_key.id),
                'user_id': api_key.user.id,
                'reason': reason
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate API key: {e}", extra={
                'api_key_id': str(api_key_id) if hasattr(api_key_id, 'id') else api_key_id
            })
            return False
    
    def extend_api_key_expiry(self, api_key_id, days):
        """
        Extend API key expiration (business logic in manager).
        
        Args:
            api_key_id: API key ID or instance
            days: Number of days to extend
        
        Returns:
            bool: True if expiry was extended successfully
        """
        try:
            if isinstance(api_key_id, str):
                api_key = self.get(id=api_key_id)
            else:
                api_key = api_key_id
            
            if api_key.expires_at:
                api_key.expires_at += timedelta(days=days)
            else:
                api_key.expires_at = timezone.now() + timedelta(days=days)
            
            api_key.save(update_fields=['expires_at', 'updated_at'])
            
            logger.info(f"Extended API key expiry", extra={
                'api_key_id': str(api_key.id),
                'user_id': api_key.user.id,
                'days_extended': days,
                'new_expires_at': api_key.expires_at.isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to extend API key expiry: {e}", extra={
                'api_key_id': str(api_key_id) if hasattr(api_key_id, 'id') else api_key_id
            })
            return False
    
    def create_api_key_for_user(self, user, name="Default API Key", expires_in_days=None):
        """
        Create new API key for user (business logic in manager).
        
        Args:
            user: User instance
            name: Name for the API key
            expires_in_days: Days until expiration (None = never expires)
        
        Returns:
            APIKey: Created API key
        """
        try:
            expires_at = None
            if expires_in_days:
                expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            api_key = self.create(
                user=user,
                name=name,
                expires_at=expires_at
            )
            
            logger.info(f"Created API key for user", extra={
                'api_key_id': str(api_key.id),
                'user_id': user.id,
                'key_name': name,
                'expires_in_days': expires_in_days
            })
            
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}", extra={
                'user_id': user.id,
                'key_name': name
            })
            raise
    
    def get_valid_api_key(self, key_value):
        """
        Get valid API key by key value (business logic in manager).
        
        Args:
            key_value: API key string
        
        Returns:
            APIKey or None: Valid API key if found
        """
        try:
            api_key = self.get(key=key_value, is_active=True)
            
            # Check if expired
            if api_key.expires_at and timezone.now() > api_key.expires_at:
                logger.debug(f"API key is expired", extra={
                    'api_key_id': str(api_key.id),
                    'expires_at': api_key.expires_at.isoformat()
                })
                return None
            
            return api_key
            
        except self.model.DoesNotExist:
            logger.debug(f"API key not found or inactive", extra={
                'key_prefix': key_value[:8] if len(key_value) >= 8 else key_value
            })
            return None
    
    def cleanup_expired_keys(self, dry_run=True):
        """
        Deactivate expired API keys.
        
        Args:
            dry_run: If True, only return count without making changes
        
        Returns:
            int: Number of API keys that would be/were deactivated
        """
        expired_keys = self.expired().filter(is_active=True)
        count = expired_keys.count()
        
        if not dry_run and count > 0:
            expired_keys.update(is_active=False)
            logger.info(f"Deactivated {count} expired API keys")
        
        return count
    
    def get_api_key_stats(self, days=30):
        """
        Get API key statistics.
        
        Args:
            days: Number of days to analyze (default: 30)
        
        Returns:
            dict: API key statistics
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_keys': queryset.count(),
            'active_keys': queryset.active().count(),
            'expired_keys': queryset.expired().count(),
            'expiring_soon': queryset.expiring_soon(7).count(),
            'recent_usage': queryset.recent_usage(24).count(),
            'valid_keys': queryset.valid().count(),
        }
        
        # Usage statistics
        usage_stats = queryset.aggregate(
            total_requests=models.Sum('total_requests'),
            avg_requests=models.Avg('total_requests'),
            max_requests=models.Max('total_requests')
        )
        stats.update(usage_stats)
        
        logger.info(f"Generated API key stats", extra={
            'days': days,
            'total_keys': stats['total_keys'],
            'active_keys': stats['active_keys']
        })
        
        return stats
