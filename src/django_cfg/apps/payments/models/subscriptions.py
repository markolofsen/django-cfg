"""
Subscription models for the universal payments system.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from .base import UUIDTimestampedModel, TimestampedModel

User = get_user_model()


class EndpointGroup(TimestampedModel):
    """API endpoint groups for subscription management."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Endpoint group name"
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable name"
    )
    description = models.TextField(
        blank=True,
        help_text="Group description"
    )
    
    # Pricing tiers
    basic_price = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Basic tier monthly price"
    )
    premium_price = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Premium tier monthly price"
    )
    enterprise_price = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Enterprise tier monthly price"
    )
    
    # Usage limits per tier
    basic_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Basic tier monthly usage limit"
    )
    premium_limit = models.PositiveIntegerField(
        default=10000,
        help_text="Premium tier monthly usage limit"
    )
    enterprise_limit = models.PositiveIntegerField(
        default=0,  # 0 = unlimited
        help_text="Enterprise tier monthly usage limit (0 = unlimited)"
    )
    
    # Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Is this endpoint group active"
    )
    require_api_key = models.BooleanField(
        default=True,
        help_text="Require API key for access"
    )
    
    # Import and assign manager
    from ..managers import EndpointGroupManager
    objects = EndpointGroupManager()
    
    class Meta:
        db_table = 'endpoint_groups'
        verbose_name = "Endpoint Group"
        verbose_name_plural = "Endpoint Groups"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return self.display_name
    
    def get_price_for_tier(self, tier: str) -> float:
        """Get price for specific tier."""
        tier_prices = {
            'basic': self.basic_price,
            'premium': self.premium_price,
            'enterprise': self.enterprise_price,
        }
        return tier_prices.get(tier, 0.0)
    
    def get_limit_for_tier(self, tier: str) -> int:
        """Get usage limit for specific tier."""
        tier_limits = {
            'basic': self.basic_limit,
            'premium': self.premium_limit,
            'enterprise': self.enterprise_limit,
        }
        return tier_limits.get(tier, 0)


class Subscription(UUIDTimestampedModel):
    """User subscriptions to endpoint groups."""
    
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        SUSPENDED = "suspended", "Suspended"
    
    class SubscriptionTier(models.TextChoices):
        BASIC = "basic", "Basic"
        PREMIUM = "premium", "Premium"
        ENTERPRISE = "enterprise", "Enterprise"
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        help_text="Subscriber"
    )
    endpoint_group = models.ForeignKey(
        EndpointGroup,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        help_text="Endpoint group"
    )
    
    # Subscription details
    tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.BASIC,
        help_text="Subscription tier"
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        help_text="Subscription status"
    )
    
    # Pricing
    monthly_price = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Monthly subscription price"
    )
    
    # Usage tracking
    usage_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Monthly usage limit (0 = unlimited)"
    )
    usage_current = models.PositiveIntegerField(
        default=0,
        help_text="Current month usage"
    )
    
    # Billing
    last_billed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last billing date"
    )
    next_billing = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Next billing date"
    )
    
    # Lifecycle
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Subscription expiration"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cancellation date"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional subscription metadata"
    )
    
    # Import and assign manager
    from ..managers import SubscriptionManager
    objects = SubscriptionManager()
    
    class Meta:
        db_table = 'user_subscriptions'
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['endpoint_group', 'status']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['next_billing']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['user', 'endpoint_group']]  # One subscription per user per group
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.endpoint_group.name} ({self.tier})"
    
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        now = timezone.now()
        
        return (
            self.status == self.SubscriptionStatus.ACTIVE and
            (self.expires_at is None or self.expires_at > now)
        )
    
    def is_usage_exceeded(self) -> bool:
        """Check if usage limit is exceeded."""
        return self.usage_limit > 0 and self.usage_current >= self.usage_limit
    
    def get_usage_percentage(self) -> float:
        """Get usage as percentage (0-100)."""
        if self.usage_limit == 0:
            return 0.0  # Unlimited
        
        return min((self.usage_current / self.usage_limit) * 100, 100.0)
    
    def can_use_api(self) -> bool:
        """Check if user can use API (active and not exceeded)."""
        return self.is_active() and not self.is_usage_exceeded()
    
    def increment_usage(self, count: int = 1):
        """Increment usage counter."""
        self.usage_current += count
        self.save(update_fields=['usage_current'])
    
    def reset_usage(self):
        """Reset usage counter (for new billing period)."""
        self.usage_current = 0
        self.save(update_fields=['usage_current'])
    
    def cancel(self):
        """Cancel subscription."""
        self.status = self.SubscriptionStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.save(update_fields=['status', 'cancelled_at'])
    
    def extend_billing_period(self):
        """Extend billing period by one month."""
        if self.next_billing:
            self.next_billing += timedelta(days=30)
        else:
            self.next_billing = timezone.now() + timedelta(days=30)
        
        if self.expires_at:
            self.expires_at += timedelta(days=30)
        else:
            self.expires_at = timezone.now() + timedelta(days=30)
        
        self.save(update_fields=['next_billing', 'expires_at'])
