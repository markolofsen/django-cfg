"""
Currency managers for the Universal Payment System v2.0.

Optimized querysets and managers for currency operations with django_currency integration.
"""

from django.db import models
from django_cfg.modules.django_logger import get_logger

logger = get_logger("currency_managers")


class CurrencyQuerySet(models.QuerySet):
    """
    Optimized queryset for currency operations.
    
    Provides efficient queries for currency management and conversion.
    """
    
    def active(self):
        """Get active currencies."""
        return self.filter(is_active=True)
    
    def inactive(self):
        """Get inactive currencies."""
        return self.filter(is_active=False)
    
    def by_type(self, currency_type):
        """Filter by currency type (fiat/crypto)."""
        return self.filter(currency_type=currency_type)
    
    def crypto(self):
        """Get cryptocurrency currencies."""
        return self.filter(currency_type='crypto')
    
    def fiat(self):
        """Get fiat currencies."""
        return self.filter(currency_type='fiat')
    
    def by_code(self, code):
        """Filter by currency code."""
        return self.filter(code=code.upper())
    
    def supported_by_provider(self, provider):
        """
        Get currencies supported by specific provider.
        
        Args:
            provider: Provider name (e.g., 'nowpayments')
        """
        return self.filter(
            provider_configs__provider=provider,
            provider_configs__is_enabled=True,
            is_active=True
        ).distinct()
    
    def with_networks(self):
        """Get currencies that have associated networks (crypto only)."""
        return self.crypto().filter(provider_configs__network__isnull=False).distinct()
    
    def without_networks(self):
        """Get currencies without networks (typically fiat)."""
        return self.filter(provider_configs__network__isnull=True).distinct()
    
    def popular(self):
        """
        Get popular currencies based on usage.
        
        This would typically be based on payment volume or frequency.
        For now, returns major currencies.
        """
        popular_codes = ['USD', 'EUR', 'BTC', 'ETH', 'USDT', 'USDC']
        return self.filter(code__in=popular_codes, is_active=True)
    
    def search(self, query):
        """
        Search currencies by code or name.
        
        Args:
            query: Search query string
        """
        return self.filter(
            models.Q(code__icontains=query) |
            models.Q(name__icontains=query)
        )


class CurrencyManager(models.Manager):
    """
    Manager for currency operations with django_currency integration.
    
    Provides high-level methods for currency management and conversion.
    """
    
    def get_queryset(self):
        """Return custom queryset."""
        return CurrencyQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active currencies."""
        return self.get_queryset().active()
    
    def crypto(self):
        """Get active cryptocurrencies."""
        return self.get_queryset().crypto().active()
    
    def fiat(self):
        """Get active fiat currencies."""
        return self.get_queryset().fiat().active()
    
    def by_code(self, code):
        """Get currency by code."""
        try:
            return self.get_queryset().by_code(code).get()
        except self.model.DoesNotExist:
            return None
    
    def supported_by_provider(self, provider):
        """Get currencies supported by provider."""
        return self.get_queryset().supported_by_provider(provider)
    
    def popular(self):
        """Get popular currencies."""
        return self.get_queryset().popular()
    
    def get_or_create_currency(self, code, name=None, currency_type=None, **kwargs):
        """
        Get existing currency or create new one.
        
        Args:
            code: Currency code (e.g., 'BTC')
            name: Currency name (e.g., 'Bitcoin')
            currency_type: 'crypto' or 'fiat'
            **kwargs: Additional currency fields
        
        Returns:
            tuple: (Currency, created)
        """
        code = code.upper()
        
        # Try to get existing currency
        try:
            currency = self.get(code=code)
            return currency, False
        except self.model.DoesNotExist:
            pass
        
        # Auto-detect currency type if not provided
        if not currency_type:
            # Simple heuristic: common fiat currencies
            fiat_codes = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'RUB']
            currency_type = 'fiat' if code in fiat_codes else 'crypto'
        
        # Auto-generate name if not provided
        if not name:
            name = self._generate_currency_name(code, currency_type)
        
        # Set defaults based on currency type
        defaults = {
            'name': name,
            'currency_type': currency_type,
            'decimal_places': 2 if currency_type == 'fiat' else 8,
            'is_active': True,
            **kwargs
        }
        
        currency = self.create(code=code, **defaults)
        
        logger.info(f"Created new currency", extra={
            'code': code,
            'name': name,
            'currency_type': currency_type
        })
        
        return currency, True
    
    def _generate_currency_name(self, code, currency_type):
        """Generate currency name from code."""
        # Common currency names
        names = {
            # Fiat
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar',
            'CHF': 'Swiss Franc',
            'CNY': 'Chinese Yuan',
            'RUB': 'Russian Ruble',
            
            # Crypto
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'LTC': 'Litecoin',
            'XMR': 'Monero',
            'USDT': 'Tether',
            'USDC': 'USD Coin',
            'ADA': 'Cardano',
            'DOT': 'Polkadot',
            'MATIC': 'Polygon',
            'BNB': 'Binance Coin',
        }
        
        return names.get(code, f"{code} {'Cryptocurrency' if currency_type == 'crypto' else 'Currency'}")
    
    def sync_with_django_currency(self):
        """
        Sync currencies with django_currency module.
        
        This method would integrate with the django_currency module
        to ensure our currency list is up-to-date.
        """
        try:
            from django_cfg.modules.django_currency import get_supported_currencies
            
            # Get supported currencies from django_currency
            supported = get_supported_currencies()
            
            created_count = 0
            updated_count = 0
            
            for currency_info in supported:
                currency, created = self.get_or_create_currency(
                    code=currency_info['code'],
                    name=currency_info.get('name'),
                    currency_type=currency_info.get('type', 'crypto')
                )
                
                if created:
                    created_count += 1
                else:
                    # Update exchange rate source if available
                    if currency_info.get('source') and not currency.exchange_rate_source:
                        currency.exchange_rate_source = currency_info['source']
                        currency.save(update_fields=['exchange_rate_source'])
                        updated_count += 1
            
            logger.info(f"Synced currencies with django_currency", extra={
                'created': created_count,
                'updated': updated_count,
                'total': len(supported)
            })
            
            return {
                'created': created_count,
                'updated': updated_count,
                'total': len(supported)
            }
            
        except ImportError:
            logger.warning("django_currency module not available for sync")
            return {'error': 'django_currency module not available'}
        except Exception as e:
            logger.error(f"Failed to sync with django_currency: {e}")
            return {'error': str(e)}
    
    def get_conversion_rate(self, from_code, to_code):
        """
        Get conversion rate between currencies using django_currency.
        
        Args:
            from_code: Source currency code
            to_code: Target currency code
        
        Returns:
            float: Conversion rate or None if unavailable
        """
        try:
            from django_cfg.modules.django_currency import get_exchange_rate
            
            rate = get_exchange_rate(from_code.upper(), to_code.upper())
            
            logger.debug(f"Retrieved conversion rate", extra={
                'from_currency': from_code,
                'to_currency': to_code,
                'rate': rate
            })
            
            return rate
            
        except Exception as e:
            logger.error(f"Failed to get conversion rate: {e}", extra={
                'from_currency': from_code,
                'to_currency': to_code
            })
            return None
    
    def convert_amount(self, amount, from_code, to_code):
        """
        Convert amount between currencies using django_currency.
        
        Args:
            amount: Amount to convert
            from_code: Source currency code
            to_code: Target currency code
        
        Returns:
            float: Converted amount or None if conversion failed
        """
        try:
            from django_cfg.modules.django_currency import convert_currency
            
            converted = convert_currency(amount, from_code.upper(), to_code.upper())
            
            logger.debug(f"Converted currency amount", extra={
                'amount': amount,
                'from_currency': from_code,
                'to_currency': to_code,
                'converted_amount': converted
            })
            
            return converted
            
        except Exception as e:
            logger.error(f"Failed to convert currency: {e}", extra={
                'amount': amount,
                'from_currency': from_code,
                'to_currency': to_code
            })
            return None
    
    def get_supported_currencies_for_provider(self, provider):
        """
        Get list of currencies supported by a specific provider.
        
        Args:
            provider: Provider name
        
        Returns:
            list: List of currency dictionaries
        """
        currencies = self.supported_by_provider(provider).select_related().prefetch_related(
            'provider_configs'
        )
        
        result = []
        for currency in currencies:
            provider_config = currency.provider_configs.filter(
                provider=provider,
                is_enabled=True
            ).first()
            
            if provider_config:
                result.append({
                    'code': currency.code,
                    'name': currency.name,
                    'type': currency.currency_type,
                    'symbol': currency.symbol,
                    'decimal_places': currency.decimal_places,
                    'min_amount': float(provider_config.min_amount) if provider_config.min_amount else None,
                    'max_amount': float(provider_config.max_amount) if provider_config.max_amount else None,
                    'network': provider_config.network.code if provider_config.network else None,
                    'fee_percentage': float(provider_config.fee_percentage),
                    'fixed_fee': float(provider_config.fixed_fee),
                })
        
        return result
    
    def get_currency_stats(self):
        """
        Get currency statistics.
        
        Returns:
            dict: Currency statistics
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_currencies': queryset.count(),
            'active_currencies': queryset.active().count(),
            'crypto_currencies': queryset.crypto().count(),
            'fiat_currencies': queryset.fiat().count(),
            'with_provider_support': queryset.filter(provider_configs__isnull=False).distinct().count(),
            'popular_currencies': queryset.popular().count(),
        }
        
        # Add provider breakdown
        stats['by_provider'] = {}
        providers = queryset.values_list('provider_configs__provider', flat=True).distinct()
        for provider in providers:
            if provider:  # Skip None values
                stats['by_provider'][provider] = queryset.supported_by_provider(provider).count()
        
        return stats
