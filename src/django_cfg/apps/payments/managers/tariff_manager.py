"""
Tariff managers.
"""

from django.db import models


class TariffManager(models.Manager):
    """Manager for Tariff model."""
    
    def get_active_tariffs(self):
        """Get active tariffs."""
        return self.filter(is_active=True).order_by('monthly_price')
    
    def get_free_tariffs(self):
        """Get free tariffs."""
        return self.filter(monthly_price=0, is_active=True)
    
    def get_paid_tariffs(self):
        """Get paid tariffs."""
        return self.filter(monthly_price__gt=0, is_active=True)


class TariffEndpointGroupManager(models.Manager):
    """Manager for TariffEndpointGroup model."""
    
    def get_enabled_for_tariff(self, tariff):
        """Get enabled endpoint groups for tariff."""
        return self.filter(tariff=tariff, is_enabled=True)
