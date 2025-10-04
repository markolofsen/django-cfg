"""
Tariff models for the Universal Payment System v2.0.

Handles pricing tiers and endpoint group associations.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .base import TimestampedModel
from .subscriptions import EndpointGroup


class Tariff(TimestampedModel):
    """
    Tariff model for subscription pricing tiers.
    
    Defines pricing and limits for different subscription levels.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Tariff name (e.g., 'Free', 'Basic', 'Pro')"
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Tariff code (e.g., 'free', 'basic', 'pro')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this tariff includes"
    )
    
    # Pricing
    monthly_price_usd = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Monthly price in USD"
    )
    
    yearly_price_usd = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="Yearly price in USD (optional discount)"
    )
    
    # Rate limits
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
    
    requests_per_month = models.PositiveIntegerField(
        default=30000,
        validators=[MinValueValidator(1), MaxValueValidator(10000000)],
        help_text="API requests allowed per month"
    )
    
    # Features
    max_api_keys = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum number of API keys allowed"
    )
    
    supports_webhooks = models.BooleanField(
        default=True,
        help_text="Whether webhooks are supported"
    )
    
    priority_support = models.BooleanField(
        default=False,
        help_text="Whether priority support is included"
    )
    
    # Availability
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this tariff is available for new subscriptions"
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this tariff is publicly visible"
    )
    
    # Ordering
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order for display (lower numbers first)"
    )
    
    class Meta:
        db_table = 'payments_tariffs'
        verbose_name = 'Tariff'
        verbose_name_plural = 'Tariffs'
        ordering = ['sort_order', 'monthly_price_usd']
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return f"{self.name} - ${self.monthly_price_usd:.2f}/month"
    
    def clean(self):
        """Validate tariff data."""
        if self.code:
            self.code = self.code.lower().replace(' ', '_')
        
        # Validate rate limits hierarchy
        if self.requests_per_day < self.requests_per_hour:
            raise ValidationError("Daily limit cannot be less than hourly limit")
        
        if self.requests_per_month < self.requests_per_day:
            raise ValidationError("Monthly limit cannot be less than daily limit")
        
        # Validate yearly pricing
        if self.yearly_price_usd and self.yearly_price_usd >= (self.monthly_price_usd * 12):
            raise ValidationError("Yearly price should be less than 12x monthly price")
    
    @property
    def is_free(self) -> bool:
        """Check if this is a free tariff."""
        return self.monthly_price_usd == 0.0
    
    @property
    def yearly_discount_percentage(self) -> float:
        """Calculate yearly discount percentage."""
        if not self.yearly_price_usd or self.monthly_price_usd == 0:
            return 0.0
        
        yearly_equivalent = self.monthly_price_usd * 12
        discount = yearly_equivalent - self.yearly_price_usd
        return (discount / yearly_equivalent) * 100
    
    @property
    def price_display(self) -> str:
        """Formatted price display."""
        if self.is_free:
            return "Free"
        return f"${self.monthly_price_usd:.2f}/month"
    
    @property
    def yearly_price_display(self) -> str:
        """Formatted yearly price display."""
        if not self.yearly_price_usd:
            return "N/A"
        if self.yearly_price_usd == 0:
            return "Free"
        return f"${self.yearly_price_usd:.2f}/year"


class TariffEndpointGroup(TimestampedModel):
    """
    Association between tariffs and endpoint groups.
    
    Defines which API endpoints are available for each tariff.
    """
    
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.CASCADE,
        related_name='endpoint_groups'
    )
    
    endpoint_group = models.ForeignKey(
        EndpointGroup,
        on_delete=models.CASCADE,
        related_name='tariffs'
    )
    
    # Override default rate limits for this specific combination
    custom_rate_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Custom rate limit for this endpoint group (overrides tariff default)"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        help_text="Whether this endpoint group is enabled for this tariff"
    )
    
    class Meta:
        db_table = 'payments_tariff_endpoint_groups'
        verbose_name = 'Tariff Endpoint Group'
        verbose_name_plural = 'Tariff Endpoint Groups'
        unique_together = [['tariff', 'endpoint_group']]
        ordering = ['tariff__sort_order', 'endpoint_group__name']
    
    def __str__(self):
        return f"{self.tariff.name} - {self.endpoint_group.name}"
    
    @property
    def effective_rate_limit(self) -> int:
        """Get effective rate limit (custom or tariff default)."""
        return self.custom_rate_limit or self.tariff.requests_per_hour
