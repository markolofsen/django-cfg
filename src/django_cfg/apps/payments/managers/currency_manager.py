"""
Manager for Currency model.
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from typing import List, Optional, TYPE_CHECKING
from decimal import Decimal

from django_cfg.modules.django_logger import get_logger
from django_cfg.modules.django_currency import convert_currency, get_exchange_rate, CurrencyError

if TYPE_CHECKING:
    from ..services.internal_types import CurrencyOptionModel

logger = get_logger("currency_manager")


class CurrencyManager(models.Manager):
    """Manager for clean Currency model."""
    
    def fiat(self):
        """Get only fiat currencies."""
        return self.filter(currency_type='fiat')
    
    def crypto(self):
        """Get only cryptocurrencies."""
        return self.filter(currency_type='crypto')
    
    def by_code(self, code: str):
        """Get currency by code (case insensitive)."""
        return self.filter(code__iexact=code).first()
    
    def search(self, query: str):
        """Search currencies by code or name."""
        return self.filter(
            models.Q(code__icontains=query) |
            models.Q(name__icontains=query)
        )
    
    def get_usd_rate(self, currency_code_or_instance, force_refresh: bool = False) -> float:
        """
        Get USD exchange rate for currency (with 24h cache).
        
        Args:
            currency_code_or_instance: Currency code (e.g., 'BTC') or Currency instance
            force_refresh: If True, skip cache and fetch fresh rate
            
        Returns:
            float: 1 CURRENCY = X USD
        """
        try:
            # Handle both Currency instance and string code
            if hasattr(currency_code_or_instance, 'code'):
                # Currency instance passed
                currency = currency_code_or_instance
                currency_code = currency.code
            else:
                # String code passed
                currency_code = str(currency_code_or_instance).upper()
                currency = self.filter(code=currency_code).first()
            
            # Return cached rate if fresh and not forcing refresh
            if not force_refresh and currency and currency.usd_rate is not None and currency.rate_updated_at:
                # Check if cache is still fresh (24 hours)
                if timezone.now() - currency.rate_updated_at < timedelta(hours=24):
                    logger.debug(f"Using cached USD rate for {currency_code}: ${float(currency.usd_rate):.8f}")
                    return float(currency.usd_rate)
            
            # Cache miss, expired, or forced refresh - fetch fresh rate
            logger.info(f"Fetching fresh USD rate for {currency_code} (force_refresh={force_refresh})")
            rate = get_exchange_rate(currency_code, 'USD')
            rate_decimal = Decimal(str(rate)).quantize(Decimal('0.00000001'))
            
            # Update cache
            if currency:
                currency.usd_rate = rate_decimal
                currency.rate_updated_at = timezone.now()
                currency.save(update_fields=['usd_rate', 'rate_updated_at'])
                logger.info(f"Updated USD rate for {currency_code}: ${rate:.8f}")
            else:
                logger.warning(f"Currency {currency_code} not found in database for rate caching")
            
            return round(rate, 8)
            
        except CurrencyError as e:
            logger.warning(f"Failed to get USD rate for {currency_code}: {e}")
            # Return cached rate if available, even if stale
            if currency and currency.usd_rate is not None:
                logger.info(f"Using stale cached rate for {currency_code} due to API error")
                return float(currency.usd_rate)
            return 0.0
    
    def get_tokens_per_usd(self, currency_code: str) -> float:
        """Get how many tokens you can buy for 1 USD."""
        usd_rate = self.get_usd_rate(currency_code)
        if usd_rate > 0:
            return round(1.0 / usd_rate, 8)
        return 0.0
    
    def convert_to_usd(self, amount: float, currency_code: str) -> float:
        """Convert currency amount to USD."""
        usd_rate = self.get_usd_rate(currency_code)
        return round(amount * usd_rate, 2)
    
    def convert_from_usd(self, usd_amount: float, currency_code: str) -> float:
        """Convert USD amount to target currency."""
        tokens_per_usd = self.get_tokens_per_usd(currency_code)
        return round(usd_amount * tokens_per_usd, 8)
    
    def get_or_create_normalized(self, code: str, defaults: dict = None):
        """Simple get_or_create with uppercase code normalization."""
        normalized_code = code.upper().strip() if code else ''
        if not normalized_code:
            raise ValueError(f"Empty currency code: '{code}'")
        
        creation_defaults = defaults or {}
        creation_defaults['code'] = normalized_code
        
        return self.get_or_create(code__iexact=normalized_code, defaults=creation_defaults)


class NetworkManager(models.Manager):
    """Manager for Network model."""
    
    def by_code(self, code: str):
        """Get network by code (case insensitive)."""
        return self.filter(code__iexact=code).first()
    
    def get_or_create_normalized(self, code: str, defaults: dict = None):
        """Get or create network with normalized code."""
        normalized_code = code.lower().strip() if code else ''
        if not normalized_code:
            raise ValueError(f"Empty network code: '{code}'")
        
        creation_defaults = defaults or {}
        creation_defaults['code'] = normalized_code
        
        return self.get_or_create(code__iexact=normalized_code, defaults=creation_defaults)


class ProviderCurrencyManager(models.Manager):
    """Manager for ProviderCurrency model."""
    
    def enabled(self):
        """Get only enabled provider currencies."""
        return self.filter(is_enabled=True)
    
    def for_provider(self, provider_name: str):
        """Get currencies for specific provider."""
        return self.filter(provider_name__iexact=provider_name)
    
    def for_base_currency(self, currency_code: str):
        """Get provider currencies for base currency."""
        return self.filter(base_currency__code__iexact=currency_code)
    
    def for_network(self, network_code: str):
        """Get provider currencies for network."""
        return self.filter(network__code__iexact=network_code)
    
    def enabled_for_provider(self, provider_name: str):
        """Get enabled currencies for provider."""
        return self.enabled().filter(provider_name__iexact=provider_name)
    
    def popular(self):
        """Get popular currencies."""
        return self.filter(is_popular=True)
    
    def stable(self):
        """Get stable currencies."""
        return self.filter(is_stable=True)
    
    def get_currency_options_for_provider(self, provider_name: str):
        """
        Get flat list of currency options for single select dropdown.
        
        Returns:
            List[dict]: List of currency option dictionaries
        """
        provider_currencies = self.enabled_for_provider(provider_name).select_related(
            'base_currency', 'network'
        ).order_by('is_popular', 'is_stable', 'base_currency__code', 'network__code')
        
        options = []
        for pc in provider_currencies:
            # Create display name: "USDT (Ethereum)" or "BTC" for native currencies
            if pc.network:
                display_name = f"{pc.base_currency.code} ({pc.network.name})"
            else:
                display_name = pc.base_currency.code
            
            # Get exchange rates using Currency manager
            from ..models import Currency
            usd_rate = Currency.objects.get_usd_rate(pc.base_currency.code)
            tokens_per_usd = Currency.objects.get_tokens_per_usd(pc.base_currency.code)
            
            option = {
                'provider_currency_code': pc.provider_currency_code,
                'display_name': display_name,
                'base_currency_code': pc.base_currency.code,
                'base_currency_name': pc.base_currency.name,
                'network_code': pc.network.code if pc.network else None,
                'network_name': pc.network.name if pc.network else None,
                'currency_type': pc.base_currency.currency_type,
                'is_popular': pc.is_popular,
                'is_stable': pc.is_stable,
                'available_for_payment': pc.available_for_payment,
                'available_for_payout': pc.available_for_payout,
                'min_amount': str(pc.min_amount) if pc.min_amount else None,
                'max_amount': str(pc.max_amount) if pc.max_amount else None,
                'logo_url': pc.logo_url,
                # Exchange rates
                'usd_rate': usd_rate,
                'tokens_per_usd': tokens_per_usd
            }
            options.append(option)
        
        # Sort: popular first, then stable, then alphabetically
        def sort_key(option):
            return (
                0 if option['is_popular'] else 1,     # Popular first
                0 if option['is_stable'] else 1,      # Then stable  
                option['base_currency_code'],         # Then by base currency
                option['network_name'] or ''          # Then by network
            )
        
        options.sort(key=sort_key)
        return options
    
    def get_usd_rates_for_provider(self, provider_name: str):
        """
        Get USD exchange rates for all provider currencies.
        
        Returns:
            dict: {provider_currency_code: {'rate': 0.0001, 'tokens_per_usd': 10000}}
        """
        provider_currencies = self.enabled_for_provider(provider_name).select_related('base_currency')
        rates = {}
        
        for pc in provider_currencies:
            try:
                # Get rate: 1 BASE_CURRENCY = X USD
                usd_rate = get_exchange_rate(pc.base_currency.code, 'USD')
                
                # Calculate tokens per 1 USD
                if usd_rate > 0:
                    tokens_per_usd = 1.0 / usd_rate
                else:
                    tokens_per_usd = 0.0
                
                rates[pc.provider_currency_code] = {
                    'usd_rate': round(usd_rate, 8),
                    'tokens_per_usd': round(tokens_per_usd, 2),
                    'base_currency': pc.base_currency.code,
                    'updated_at': timezone.now().isoformat()
                }
                
            except CurrencyError as e:
                logger.warning(f"Failed to get rate for {pc.base_currency.code}: {e}")
                rates[pc.provider_currency_code] = {
                    'usd_rate': 0.0,
                    'tokens_per_usd': 0.0,
                    'base_currency': pc.base_currency.code,
                    'error': str(e)
                }
        
        return rates
    
    def convert_amount(self, amount: float, from_currency_code: str, to_currency: str = 'USD'):
        """
        Convert amount from provider currency to target currency.
        
        Args:
            amount: Amount to convert
            from_currency_code: Provider currency code (e.g., 'USDTERC20')
            to_currency: Target currency (default: 'USD')
            
        Returns:
            dict: {'amount': converted_amount, 'rate': exchange_rate, 'from': base_currency}
        """
        try:
            # Find provider currency and get base currency
            pc = self.get(provider_currency_code=from_currency_code)
            base_currency = pc.base_currency.code
            
            # Convert via base currency
            converted_amount = convert_currency(amount, base_currency, to_currency)
            rate = get_exchange_rate(base_currency, to_currency)
            
            return {
                'amount': round(converted_amount, 2),
                'rate': round(rate, 8),
                'from': base_currency,
                'to': to_currency,
                'original_amount': amount,
                'provider_code': from_currency_code
            }
            
        except (CurrencyError, self.model.DoesNotExist) as e:
            logger.error(f"Conversion failed for {from_currency_code}: {e}")
            return {
                'amount': 0.0,
                'rate': 0.0,
                'error': str(e)
            }