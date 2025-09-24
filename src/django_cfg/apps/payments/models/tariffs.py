"""
Tariff models for the universal payments system.
"""

from django.db import models
from django.core.validators import MinValueValidator
from .base import TimestampedModel


class Tariff(TimestampedModel):
    """Simple tariff plans for API access."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Tariff name"
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable tariff name"
    )
    description = models.TextField(
        blank=True,
        help_text="Tariff description"
    )
    
    # Pricing
    monthly_price = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Monthly price in USD"
    )
    
    # Limits
    request_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Monthly request limit (0 = unlimited)"
    )
    
    # Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Is this tariff active"
    )
    
    # Import and assign manager
    from ..managers import TariffManager
    objects = TariffManager()
    
    class Meta:
        db_table = 'tariffs'
        verbose_name = "Tariff"
        verbose_name_plural = "Tariffs"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['monthly_price']),
        ]
        ordering = ['monthly_price']
    
    def __str__(self):
        return f"{self.display_name} (${self.monthly_price}/month)"
    
    @property
    def is_free(self) -> bool:
        """Check if this is a free tariff."""
        return self.monthly_price == 0


class TariffEndpointGroup(TimestampedModel):
    """Simple association between tariffs and endpoint groups."""
    
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.CASCADE,
        related_name='endpoint_groups',
        help_text="Tariff plan"
    )
    from .subscriptions import EndpointGroup
    endpoint_group = models.ForeignKey(
        EndpointGroup,
        on_delete=models.CASCADE,
        related_name='tariffs',
        help_text="Endpoint group"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        help_text="Is this endpoint group enabled for this tariff"
    )
    
    # Import and assign manager
    from ..managers import TariffEndpointGroupManager
    objects = TariffEndpointGroupManager()
    
    class Meta:
        db_table = 'tariff_endpoint_groups'
        verbose_name = "Tariff Endpoint Group"
        verbose_name_plural = "Tariff Endpoint Groups"
        unique_together = [['tariff', 'endpoint_group']]
    
    def __str__(self):
        return f"{self.tariff.name} - {self.endpoint_group.name}"
