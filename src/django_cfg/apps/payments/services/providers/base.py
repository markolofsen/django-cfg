"""
Base payment provider interface.

Abstract base class for all payment providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from django.db.models import QuerySet
from decimal import Decimal

from django.db import models, transaction
from cachetools import TTLCache

from ..internal_types import ProviderResponse, WebhookData, PaymentAmountEstimate, ProviderInfo, UniversalCurrency, UniversalCurrenciesResponse, ProviderSyncResult
from ...models import Currency, Network, ProviderCurrency
from django_cfg.modules.django_logger import get_logger


logger = get_logger('base_provider')

class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    # Class-level cache for all providers (5 min TTL)
    _api_cache = TTLCache(maxsize=100, ttl=300)
    
    def __init__(self, config):
        """Initialize provider with config."""
        self.config = config
        self.name = self.__class__.__name__.lower().replace('provider', '')
        self.logger = get_logger(f"payment.{self.name}")
        
        # Handle both dict and Pydantic model configs
        if hasattr(config, 'enabled'):
            self.enabled = config.enabled
        elif hasattr(config, 'get'):
            self.enabled = config.get('enabled', True)
        else:
            self.enabled = getattr(config, 'enabled', True)
    
    @abstractmethod
    def create_payment(self, payment_data: dict) -> ProviderResponse:
        """
        Create a payment request.
        
        Args:
            amount: Payment amount
            currency: Payment currency
            **kwargs: Additional parameters (order_id, description, etc.)
            
        Returns:
            Dict with payment creation result
        """
        pass
    
    @abstractmethod
    def check_payment_status(self, payment_id: str) -> ProviderResponse:
        """
        Check payment status.
        
        Args:
            payment_id: Payment ID from provider
            
        Returns:
            Dict with payment status
        """
        pass
    
    @abstractmethod
    def process_webhook(self, payload: dict) -> WebhookData:
        """
        Process webhook payload.
        
        Args:
            payload: Webhook data from provider
            
        Returns:
            Dict with processed webhook data
        """
        pass
    
    @abstractmethod 
    def get_parsed_currencies(self) -> UniversalCurrenciesResponse:
        """
        Get parsed and normalized currencies ready for database sync.
        
        This method should:
        1. Fetch data from provider API
        2. Parse provider codes into base_currency + network
        3. Return universal format
        
        Returns:
            UniversalCurrenciesResponse with parsed data
        """
        pass
    
    
    
    def validate_webhook(self, payload: dict, headers: Optional[dict] = None) -> bool:
        """
        Validate webhook signature and data.
        
        Args:
            payload: Webhook data
            signature: Webhook signature (if applicable)
            
        Returns:
            True if webhook is valid
        """
        # Default implementation - providers can override
        return True
    
    
    def check_api_status(self) -> bool:
        """
        Check if provider API is available.
        
        Returns:
            True if API is available
        """
        # Optional method - providers can override
        return True
    
    def is_enabled(self) -> bool:
        """Check if provider is enabled."""
        return self.enabled
    
    def sync_currencies_to_db(self) -> ProviderSyncResult:
        """
        Synchronize provider currencies with clean architecture.
        Uses get_parsed_currencies() to get normalized data.
        """
        result = ProviderSyncResult()
        
        # Get parsed data from provider
        try:
            parsed_response = self.get_parsed_currencies()
        except Exception as e:
            result.errors.append(f"Failed to get parsed currencies: {str(e)}")
            return result
        
        logger.info(f"Processing {len(parsed_response.currencies)} currencies from {self.name}")
        
        with transaction.atomic():
            for universal_currency in parsed_response.currencies:
                try:
                    # 1. Create/update base Currency using normalized manager
                    currency, created = Currency.objects.get_or_create_normalized(
                        code=universal_currency.base_currency_code,
                        defaults={
                            'name': universal_currency.name,
                            'currency_type': universal_currency.currency_type
                        }
                    )
                    
                    if created:
                        result.currencies_created += 1
                        logger.debug(f"Created currency: {universal_currency.base_currency_code}")
                    else:
                        result.currencies_updated += 1
                    
                    # 2. Create/update Network (if needed) using normalized manager
                    network = None
                    if universal_currency.network_code:
                        network, created = Network.objects.get_or_create_normalized(
                            code=universal_currency.network_code,
                            defaults={
                                'name': universal_currency.network_code.title()
                            }
                        )
                        
                        if created:
                            result.networks_created += 1
                            logger.debug(f"Created network: {universal_currency.network_code}")
                        else:
                            result.networks_updated += 1
                    
                    # 3. Create/update ProviderCurrency mapping
                    provider_currency, created = ProviderCurrency.objects.get_or_create(
                        provider_name=self.name,
                        provider_currency_code=universal_currency.provider_currency_code,
                        defaults={
                            'base_currency': currency,
                            'network': network,
                            'is_enabled': universal_currency.is_enabled,
                            'is_popular': universal_currency.is_popular,
                            'is_stable': universal_currency.is_stable,
                            'priority': universal_currency.priority,
                            'logo_url': universal_currency.logo_url,
                            'available_for_payment': universal_currency.available_for_payment,
                            'available_for_payout': universal_currency.available_for_payout,
                            'min_amount': universal_currency.min_amount,
                            'max_amount': universal_currency.max_amount,
                            'metadata': universal_currency.raw_data
                        }
                    )
                    
                    if created:
                        result.provider_currencies_created += 1
                        logger.debug(f"Created provider currency: {universal_currency.provider_currency_code}")
                    else:
                        # Update existing record
                        provider_currency.is_enabled = universal_currency.is_enabled
                        provider_currency.is_popular = universal_currency.is_popular
                        provider_currency.is_stable = universal_currency.is_stable
                        provider_currency.priority = universal_currency.priority
                        provider_currency.logo_url = universal_currency.logo_url
                        provider_currency.save()
                        result.provider_currencies_updated += 1
                
                except Exception as e:
                    error_msg = f"Error processing {universal_currency.provider_currency_code}: {str(e)}"
                    result.errors.append(error_msg)
                    logger.error(error_msg)
        
        logger.info(f"Sync completed: {result}")
        return result
    
    def get_provider_info(self) -> ProviderInfo:
        """Get provider information using parsed currencies."""
        try:
            parsed_response = self.get_parsed_currencies()
            supported_currencies = [c.base_currency_code for c in parsed_response.currencies]
        except Exception:
            supported_currencies = []
        
        return ProviderInfo(
            name=self.name,
            display_name=self.name.title(),
            supported_currencies=supported_currencies,
            is_active=self.enabled and self.check_api_status(),
            features={
                'supports_networks': True,
                'supports_webhooks': True,
                'supports_refunds': True
            }
        )
