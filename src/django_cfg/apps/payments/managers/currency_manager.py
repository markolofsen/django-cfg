"""
Manager for Currency model.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from typing import List, Optional


class CurrencyManager(models.Manager):
    """Manager for Currency model with convenient query methods."""
    
    def active(self):
        """Get only active currencies."""
        return self.filter(is_active=True)
    
    def fiat(self):
        """Get only fiat currencies."""
        return self.filter(currency_type='fiat')
    
    def crypto(self):
        """Get only cryptocurrencies."""
        return self.filter(currency_type='crypto')
    
    def active_fiat(self):
        """Get active fiat currencies."""
        return self.filter(currency_type='fiat', is_active=True)
    
    def active_crypto(self):
        """Get active cryptocurrencies.""" 
        return self.filter(currency_type='crypto', is_active=True)
    
    def by_code(self, code: str):
        """Get currency by code (case insensitive)."""
        return self.filter(code__iexact=code).first()
    
    def supported_for_payments(self, min_amount: float = None):
        """Get currencies supported for payments."""
        queryset = self.active()
        if min_amount:
            queryset = queryset.filter(min_payment_amount__lte=min_amount)
        return queryset
    
    def recently_updated(self, hours: int = 24):
        """Get currencies updated within the last N hours."""
        threshold = timezone.now() - timedelta(hours=hours)
        return self.filter(rate_updated_at__gte=threshold)
    
    def outdated(self, days: int = 7):
        """Get currencies with outdated rates."""
        threshold = timezone.now() - timedelta(days=days)
        return self.filter(
            models.Q(rate_updated_at__lt=threshold) | 
            models.Q(rate_updated_at__isnull=True)
        )
    
    def top_crypto_by_value(self, limit: int = 10):
        """Get top cryptocurrencies by USD value."""
        return self.active_crypto().order_by('-usd_rate')[:limit]
    
    def search(self, query: str):
        """Search currencies by code or name."""
        return self.filter(
            models.Q(code__icontains=query) |
            models.Q(name__icontains=query)
        )


class CurrencyNetworkManager(models.Manager):
    """Manager for CurrencyNetwork model."""
    
    def active(self):
        """Get only active networks."""
        return self.filter(is_active=True)
    
    def for_currency(self, currency_code: str):
        """Get networks for a specific currency."""
        return self.filter(currency__code__iexact=currency_code)
    
    def active_for_currency(self, currency_code: str):
        """Get active networks for a specific currency."""
        return self.active().filter(currency__code__iexact=currency_code)