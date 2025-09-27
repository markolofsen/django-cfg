"""
Subscription models for the Universal Payment System v2.0.

Handles user subscriptions and API access control.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .base import UUIDTimestampedModel

User = get_user_model()


class EndpointGroup(models.Model):
    """
    API endpoint group for subscription management.
    
    Groups related API endpoints for subscription-based access control.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Endpoint group name (e.g., 'Payment API', 'Balance API')"
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Endpoint group code (e.g., 'payments', 'balance')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what this endpoint group provides"
    )
    
    # Access control
    is_enabled = models.BooleanField(
        default=True,
        help_text="Whether this endpoint group is available"
    )
    
    requires_subscription = models.BooleanField(
        default=True,
        help_text="Whether access requires an active subscription"
    )
    
    # Rate limiting defaults
    default_rate_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Default requests per hour for this endpoint group"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_endpoint_groups'
        verbose_name = 'Endpoint Group'
        verbose_name_plural = 'Endpoint Groups'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Validate endpoint group data."""
        if self.code:
            self.code = self.code.lower().replace(' ', '_')


class SubscriptionQuerySet(models.QuerySet):
    """Optimized queryset for subscription operations."""
    
    def optimized(self):
        """Prevent N+1 queries."""
        return self.select_related('user').prefetch_related('endpoint_groups')
    
    def active(self):
        """Get active subscriptions."""
        return self.filter(
            status=Subscription.SubscriptionStatus.ACTIVE,
            expires_at__gt=timezone.now()
        )
    
    def expired(self):
        """Get expired subscriptions."""
        return self.filter(expires_at__lte=timezone.now())
    
    def by_tier(self, tier):
        """Filter by subscription tier."""
        return self.filter(tier=tier)
    
    def by_user(self, user):
        """Filter by user."""
        return self.filter(user=user)


class Subscription(UUIDTimestampedModel):
    """
    User subscription model for API access control.
    
    Manages user subscriptions with different tiers and access levels.
    """
    
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"
    
    class SubscriptionTier(models.TextChoices):
        FREE = "free", "Free Tier"
        BASIC = "basic", "Basic Tier"
        PRO = "pro", "Pro Tier"
        ENTERPRISE = "enterprise", "Enterprise Tier"
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_subscriptions',
        help_text="User who owns this subscription"
    )
    
    tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.FREE,
        help_text="Subscription tier"
    )
    
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        help_text="Subscription status"
    )
    
    # Access control
    endpoint_groups = models.ManyToManyField(
        EndpointGroup,
        related_name='subscriptions',
        blank=True,
        help_text="Endpoint groups accessible with this subscription"
    )
    
    # Rate limiting
    requests_per_hour = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
        help_text="API requests allowed per hour"
    )
    
    requests_per_day = models.PositiveIntegerField(
        default=1000,
        validators=[MinValueValidator(1), MaxValueValidator(1000000)],
        help_text="API requests allowed per day"
    )
    
    # Subscription period
    starts_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this subscription starts"
    )
    
    expires_at = models.DateTimeField(
        help_text="When this subscription expires"
    )
    
    # Billing information
    monthly_cost_usd = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Monthly cost in USD"
    )
    
    # Usage tracking
    total_requests = models.PositiveIntegerField(
        default=0,
        help_text="Total API requests made with this subscription"
    )
    
    last_request_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last API request was made"
    )
    
    # Auto-renewal
    auto_renew = models.BooleanField(
        default=False,
        help_text="Whether to automatically renew this subscription"
    )
    
    # Manager
    from .managers.subscription_managers import SubscriptionManager
    objects = SubscriptionManager()
    
    class Meta:
        db_table = 'payments_subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['tier', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='active'),
                name='one_active_subscription_per_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tier} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Override save to set default expiration."""
        if not self.expires_at:
            # Default to 30 days from start
            self.expires_at = self.starts_at + timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate subscription data."""
        if self.expires_at and self.starts_at and self.expires_at <= self.starts_at:
            raise ValidationError("Expiration date must be after start date")
        
        if self.requests_per_day < self.requests_per_hour:
            raise ValidationError("Daily limit cannot be less than hourly limit")
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active and not expired."""
        return (
            self.status == self.SubscriptionStatus.ACTIVE and
            self.expires_at > timezone.now()
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        return timezone.now() > self.expires_at
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining until expiration."""
        if self.is_expired:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    @property
    def usage_percentage(self) -> float:
        """Get usage percentage for current period."""
        # This would need to be calculated based on actual usage tracking
        # For now, return 0.0 as placeholder
        return 0.0
    
    @property
    def tier_display(self) -> str:
        """Get display name for tier."""
        return self.get_tier_display()
    
    @property
    def status_color(self) -> str:
        """Get color for status display."""
        colors = {
            self.SubscriptionStatus.ACTIVE: 'success',
            self.SubscriptionStatus.INACTIVE: 'secondary',
            self.SubscriptionStatus.SUSPENDED: 'warning',
            self.SubscriptionStatus.CANCELLED: 'danger',
            self.SubscriptionStatus.EXPIRED: 'danger',
        }
        return colors.get(self.status, 'secondary')
    
    def activate(self):
        """Activate subscription (delegates to manager)."""
        return self.__class__.objects.activate_subscription(self)
    
    def suspend(self, reason=None):
        """Suspend subscription (delegates to manager)."""
        return self.__class__.objects.suspend_subscription(self, reason)
    
    def cancel(self, reason=None):
        """Cancel subscription (delegates to manager)."""
        return self.__class__.objects.cancel_subscription(self, reason)
    
    def renew(self, duration_days: int = 30):
        """Renew subscription (delegates to manager)."""
        return self.__class__.objects.renew_subscription(self, duration_days)
    
    def has_access_to_endpoint_group(self, endpoint_group_code: str) -> bool:
        """Check if subscription has access to specific endpoint group."""
        if not self.is_active:
            return False
        
        return self.endpoint_groups.filter(
            code=endpoint_group_code,
            is_enabled=True
        ).exists()
    
    def increment_usage(self):
        """Increment usage counter (delegates to manager)."""
        return self.__class__.objects.increment_subscription_usage(self)
    
    @classmethod
    def get_active_for_user(cls, user: User) -> 'Subscription':
        """Get active subscription for user (delegates to manager)."""
        return cls.objects.get_active_for_user(user)
    
    @classmethod
    def create_free_subscription(cls, user: User) -> 'Subscription':
        """Create free tier subscription for user (delegates to manager)."""
        return cls.objects.create_free_subscription(user)
