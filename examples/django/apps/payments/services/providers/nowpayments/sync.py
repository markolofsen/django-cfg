"""
NowPayments currency synchronization service.

Handles syncing currencies from NowPayments API to database.
"""

from typing import Optional, Tuple, List
from django.db import transaction
from django.utils import timezone

from django_cfg.modules.django_logging import get_logger
from django_cfg.apps.payments.models import Currency, Network, ProviderCurrency
from ..models import UniversalCurrency, CurrencySyncResult
from .config import NowPaymentsConfig as Config

logger = get_logger("nowpayments_sync")


class NowPaymentsCurrencySync:
    """Service for synchronizing NowPayments currencies to database."""
    
    def __init__(self, provider_name: str = 'nowpayments'):
        """Initialize currency sync service."""
        self.provider_name = provider_name
        
    def sync_currencies_to_db(self, currencies: List[UniversalCurrency]) -> CurrencySyncResult:
        """
        Sync universal currencies to database.
        
        Args:
            currencies: List of universal currencies from provider
            
        Returns:
            CurrencySyncResult: Sync operation results
        """
        result = CurrencySyncResult(total_processed=len(currencies))
        
        try:
            with transaction.atomic():
                for currency in currencies:
                    try:
                        self._sync_single_currency(currency, result)
                    except Exception as e:
                        error_msg = f"Failed to sync {currency.provider_currency_code}: {e}"
                        logger.error(error_msg)
                        result.errors.append(error_msg)
                        
            logger.info(
                f"Currency sync completed: {result.currencies_created} created, "
                f"{result.currencies_updated} updated, "
                f"{result.provider_currencies_created} provider currencies created, "
                f"{len(result.errors)} errors"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Currency sync transaction failed: {e}")
            result.errors.append(f"Transaction failed: {e}")
            return result
    
    def _sync_single_currency(self, currency: UniversalCurrency, result: CurrencySyncResult):
        """Sync a single currency to database."""
        
        # 1. Ensure base currency exists
        base_currency, currency_created = self._get_or_create_currency(currency)
        if currency_created:
            result.currencies_created += 1
        else:
            # Update existing currency if needed
            updated = self._update_currency_if_needed(base_currency, currency)
            if updated:
                result.currencies_updated += 1
        
        # 2. Ensure network exists (if applicable)
        network = None
        if currency.network_code:
            network, network_created = self._get_or_create_network(currency, base_currency)
            if network_created:
                result.networks_created += 1
        
        # 3. Create or update provider currency
        provider_currency, pc_created = self._get_or_create_provider_currency(
            currency, base_currency, network
        )
        
        if pc_created:
            result.provider_currencies_created += 1
        else:
            # Update existing provider currency
            updated = self._update_provider_currency_if_needed(provider_currency, currency)
            if updated:
                result.provider_currencies_updated += 1
    
    def _get_or_create_currency(self, currency: UniversalCurrency) -> Tuple[Currency, bool]:
        """Get or create base currency."""
        
        defaults = {
            'name': currency.name,
            'currency_type': currency.currency_type,
            'is_active': currency.is_enabled,
            'usd_rate': 1.0,  # Will be updated by rate sync
            'usd_rate_updated_at': None,
            'decimal_places': self._get_decimal_places(currency),
        }
        
        return Currency.objects.get_or_create(
            code=currency.base_currency_code,
            defaults=defaults
        )
    
    def _update_currency_if_needed(self, base_currency: Currency, currency: UniversalCurrency) -> bool:
        """Update currency if needed."""
        updated = False
        
        # Always update name to use the proper generated name
        if base_currency.name != currency.name:
            base_currency.name = currency.name
            updated = True
        
        # Update activity status
        if base_currency.is_active != currency.is_enabled:
            base_currency.is_active = currency.is_enabled
            updated = True
        
        if updated:
            base_currency.save()
            
        return updated
    
    def _get_or_create_network(self, currency: UniversalCurrency, base_currency: Currency) -> Tuple[Network, bool]:
        """Get or create network for currency."""
        
        network_name = Config.get_network_name(currency.network_code)
        
        defaults = {
            'name': network_name,
            'native_currency': base_currency,
            'is_active': True,
            'confirmation_blocks': Config.get_confirmation_blocks(currency.network_code),
        }
        
        return Network.objects.get_or_create(
            code=currency.network_code,
            defaults=defaults
        )
    
    def _get_or_create_provider_currency(
        self, 
        currency: UniversalCurrency, 
        base_currency: Currency, 
        network: Optional[Network]
    ) -> Tuple[ProviderCurrency, bool]:
        """Get or create provider currency."""
        
        defaults = {
            'currency': base_currency,
            'network': network,
            'is_enabled': currency.is_enabled,
        }
        
        return ProviderCurrency.objects.get_or_create(
            provider=self.provider_name,
            provider_currency_code=currency.provider_currency_code,
            defaults=defaults
        )
    
    def _update_provider_currency_if_needed(
        self, 
        provider_currency: ProviderCurrency, 
        currency: UniversalCurrency
    ) -> bool:
        """Update provider currency if needed."""
        updated = False
        
        # Update enabled status
        if provider_currency.is_enabled != currency.is_enabled:
            provider_currency.is_enabled = currency.is_enabled
            updated = True
        
        # Update timestamps
        if updated:
            provider_currency.updated_at = timezone.now()
            provider_currency.save()
            
        return updated
    
    def _get_decimal_places(self, currency: UniversalCurrency) -> int:
        """Get appropriate decimal places for currency."""
        if currency.currency_type == 'fiat':
            return 2
        elif currency.is_stable:
            return 6  # Stablecoins
        else:
            return 8  # Regular crypto
    