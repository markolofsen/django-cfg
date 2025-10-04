"""
Currency service for the Universal Payment System v2.0.

Handles currency conversion and rate management using django_currency module.
"""

from typing import Optional, List
from django.utils import timezone
from django.db import models

from .base import BaseService
from ..types import (
    CurrencyConversionRequest, CurrencyConversionResult, CurrencyData,
    ServiceOperationResult
)
from ...models import Currency, ProviderCurrency, Network
from django_cfg.modules.django_currency import (
    convert_currency, get_exchange_rate, CurrencyError
)


class CurrencyService(BaseService):
    """
    Currency service with conversion and rate management.
    
    Integrates with django_currency module for real-time rates.
    """
    
    def convert_currency(self, request: CurrencyConversionRequest) -> CurrencyConversionResult:
        """
        Convert amount between currencies.
        
        Args:
            request: Currency conversion request
            
        Returns:
            CurrencyConversionResult: Conversion result with rate
        """
        try:
            # Validate request
            if isinstance(request, dict):
                request = CurrencyConversionRequest(**request)
            
            self.logger.debug("Converting currency", extra={
                'amount': request.amount,
                'from_currency': request.from_currency,
                'to_currency': request.to_currency
            })
            
            # Check if currencies are supported
            validation_result = self._validate_currencies(
                request.from_currency, 
                request.to_currency
            )
            if not validation_result.success:
                return CurrencyConversionResult(
                    success=False,
                    message=validation_result.message,
                    error_code=validation_result.error_code
                )
            
            # Perform conversion using django_currency
            try:
                converted_amount = convert_currency(
                    request.amount,
                    request.from_currency,
                    request.to_currency
                )
                
                exchange_rate = get_exchange_rate(
                    request.from_currency,
                    request.to_currency
                )
                
                self._log_operation(
                    "convert_currency",
                    True,
                    from_currency=request.from_currency,
                    to_currency=request.to_currency,
                    amount=request.amount,
                    converted_amount=converted_amount,
                    exchange_rate=exchange_rate
                )
                
                return CurrencyConversionResult(
                    success=True,
                    message="Currency converted successfully",
                    amount=request.amount,
                    from_currency=request.from_currency,
                    to_currency=request.to_currency,
                    converted_amount=converted_amount,
                    exchange_rate=exchange_rate,
                    rate_timestamp=timezone.now()
                )
                
            except CurrencyError as e:
                return CurrencyConversionResult(
                    success=False,
                    message=f"Currency conversion failed: {e}",
                    error_code="conversion_failed",
                    amount=request.amount,
                    from_currency=request.from_currency,
                    to_currency=request.to_currency
                )
                
        except Exception as e:
            return CurrencyConversionResult(**self._handle_exception(
                "convert_currency", e,
                from_currency=request.from_currency if hasattr(request, 'from_currency') else None,
                to_currency=request.to_currency if hasattr(request, 'to_currency') else None
            ).model_dump())
    
    def get_exchange_rate(self, base_currency: str, quote_currency: str) -> ServiceOperationResult:
        """
        Get current exchange rate between currencies.
        
        Args:
            base_currency: Base currency code
            quote_currency: Quote currency code
            
        Returns:
            ServiceOperationResult: Exchange rate information
        """
        try:
            self.logger.debug("Getting exchange rate", extra={
                'base_currency': base_currency,
                'quote_currency': quote_currency
            })
            
            # Validate currencies
            validation_result = self._validate_currencies(base_currency, quote_currency)
            if not validation_result.success:
                return validation_result
            
            # Get rate using django_currency
            try:
                rate = get_exchange_rate(base_currency, quote_currency)
                
                return self._create_success_result(
                    "Exchange rate retrieved successfully",
                    {
                        'base_currency': base_currency,
                        'quote_currency': quote_currency,
                        'exchange_rate': rate,
                        'rate_timestamp': timezone.now().isoformat(),
                        'pair': f"{base_currency}/{quote_currency}"
                    }
                )
                
            except CurrencyError as e:
                return self._create_error_result(
                    f"Failed to get exchange rate: {e}",
                    "rate_fetch_failed"
                )
                
        except Exception as e:
            return self._handle_exception(
                "get_exchange_rate", e,
                base_currency=base_currency,
                quote_currency=quote_currency
            )
    
    def get_supported_currencies(self, provider: Optional[str] = None, currency_type: str = 'all') -> ServiceOperationResult:
        """
        Get list of supported currencies.
        
        Args:
            provider: Filter by provider (optional)
            currency_type: Filter by currency type ('all', 'crypto', 'fiat')
            
        Returns:
            ServiceOperationResult: List of supported currencies
        """
        try:
            self.logger.debug("Getting supported currencies", extra={
                'provider': provider,
                'currency_type': currency_type
            })
            
            # Get currencies from database
            queryset = Currency.objects.filter(is_active=True)
            
            # Filter by currency type
            if currency_type and currency_type != 'all':
                queryset = queryset.filter(currency_type=currency_type)
            
            if provider:
                # Filter by provider support
                queryset = queryset.filter(
                    provider_configs__provider=provider,
                    provider_configs__is_enabled=True
                ).distinct()
            
            currencies = queryset.order_by('code')
            
            # Convert to data
            currency_data = []
            for currency in currencies:
                data = CurrencyData.model_validate(currency)
                currency_info = data.model_dump()
                
                # Add provider-specific info if requested
                if provider:
                    try:
                        provider_currency = ProviderCurrency.objects.filter(
                            currency=currency,
                            provider=provider,
                            is_enabled=True
                        ).first()
                        if provider_currency:
                            currency_info['provider_info'] = {
                                'min_amount': provider_currency.provider_min_amount_usd,
                                'max_amount': provider_currency.provider_max_amount_usd,
                                'fee_percentage': provider_currency.provider_fee_percentage,
                                'fixed_fee_usd': provider_currency.provider_fixed_fee_usd,
                                'confirmation_blocks': provider_currency.provider_confirmation_blocks
                            }
                    except Exception:
                        pass
                
                currency_data.append(currency_info)
            
            return self._create_success_result(
                f"Retrieved {len(currency_data)} supported currencies",
                {
                    'currencies': currency_data,
                    'count': len(currency_data),
                    'provider': provider
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "get_supported_currencies", e,
                provider=provider
            )
    
    def get_currency_networks(self, currency_code: str) -> ServiceOperationResult:
        """
        Get available networks for a currency.
        
        Args:
            currency_code: Currency code
            
        Returns:
            ServiceOperationResult: Available networks
        """
        try:
            self.logger.debug("Getting currency networks", extra={
                'currency_code': currency_code
            })
            
            # Get currency
            try:
                currency = Currency.objects.get(code=currency_code, is_active=True)
            except Currency.DoesNotExist:
                return self._create_error_result(
                    f"Currency {currency_code} not found or disabled",
                    "currency_not_found"
                )
            
            # Get networks
            networks = Network.objects.filter(
                currency_code=currency_code,
                is_active=True
            ).order_by('name')
            
            network_data = []
            for network in networks:
                network_info = {
                    'code': network.code,
                    'name': network.name,
                    'currency_code': network.currency_code,
                    'is_testnet': network.is_testnet,
                    'confirmation_blocks': network.confirmation_blocks,
                    'block_time_seconds': network.block_time_seconds,
                    'estimated_confirmation_time': network.estimated_confirmation_time()
                }
                network_data.append(network_info)
            
            return self._create_success_result(
                f"Retrieved {len(network_data)} networks for {currency_code}",
                {
                    'currency_code': currency_code,
                    'networks': network_data,
                    'count': len(network_data)
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "get_currency_networks", e,
                currency_code=currency_code
            )
    
    def update_currency_rates(self, currency_codes: Optional[List[str]] = None) -> ServiceOperationResult:
        """
        Update currency rates from external sources.
        
        Args:
            currency_codes: Specific currencies to update (optional)
            
        Returns:
            ServiceOperationResult: Update result
        """
        try:
            self.logger.info("Updating currency rates", extra={
                'currency_codes': currency_codes
            })
            
            # Get currencies to update
            if currency_codes:
                currencies = Currency.objects.filter(
                    code__in=currency_codes,
                    is_active=True
                )
            else:
                currencies = Currency.objects.filter(is_active=True)
            
            updated_count = 0
            failed_count = 0
            errors = []
            
            # Update rates for each currency against USD
            for currency in currencies:
                try:
                    if currency.code != 'USD':
                        # Test rate fetch
                        rate = get_exchange_rate('USD', currency.code)
                        updated_count += 1
                        
                        self.logger.debug(f"Updated rate for {currency.code}", extra={
                            'currency_code': currency.code,
                            'usd_rate': rate
                        })
                except CurrencyError as e:
                    failed_count += 1
                    error_msg = f"{currency.code}: {str(e)}"
                    errors.append(error_msg)
                    
                    self.logger.warning(f"Failed to update rate for {currency.code}", extra={
                        'currency_code': currency.code,
                        'error': str(e)
                    })
            
            self._log_operation(
                "update_currency_rates",
                failed_count == 0,
                updated_count=updated_count,
                failed_count=failed_count
            )
            
            return self._create_success_result(
                f"Updated rates for {updated_count} currencies, {failed_count} failed",
                {
                    'updated_count': updated_count,
                    'failed_count': failed_count,
                    'errors': errors,
                    'total_currencies': currencies.count()
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "update_currency_rates", e,
                currency_codes=currency_codes
            )
    
    def get_currency_stats(self) -> ServiceOperationResult:
        """
        Get currency statistics.
        
        Returns:
            ServiceOperationResult: Currency statistics
        """
        try:
            # Currency counts
            total_currencies = Currency.objects.count()
            enabled_currencies = Currency.objects.filter(is_active=True).count()
            crypto_currencies = Currency.objects.filter(
                currency_type=Currency.CurrencyType.CRYPTO,
                is_active=True
            ).count()
            fiat_currencies = Currency.objects.filter(
                currency_type=Currency.CurrencyType.FIAT,
                is_active=True
            ).count()
            
            # Provider support
            provider_stats = ProviderCurrency.objects.filter(
                is_enabled=True
            ).values('provider').annotate(
                currency_count=models.Count('currency', distinct=True)
            ).order_by('-currency_count')
            
            # Network stats
            network_stats = Network.objects.filter(
                is_active=True
            ).values('currency_code').annotate(
                network_count=models.Count('id')
            ).order_by('-network_count')
            
            stats = {
                'total_currencies': total_currencies,
                'enabled_currencies': enabled_currencies,
                'crypto_currencies': crypto_currencies,
                'fiat_currencies': fiat_currencies,
                'provider_support': list(provider_stats),
                'network_support': list(network_stats),
                'generated_at': timezone.now().isoformat()
            }
            
            return self._create_success_result(
                "Currency statistics retrieved",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("get_currency_stats", e)
    
    def _validate_currencies(self, from_currency: str, to_currency: str) -> ServiceOperationResult:
        """Validate that currencies are supported."""
        try:
            # Check from_currency
            if not Currency.objects.filter(code=from_currency, is_active=True).exists():
                return self._create_error_result(
                    f"Currency {from_currency} not supported",
                    "from_currency_not_supported"
                )
            
            # Check to_currency
            if not Currency.objects.filter(code=to_currency, is_active=True).exists():
                return self._create_error_result(
                    f"Currency {to_currency} not supported",
                    "to_currency_not_supported"
                )
            
            return self._create_success_result("Currencies are valid")
            
        except Exception as e:
            return self._create_error_result(
                f"Currency validation error: {e}",
                "validation_error"
            )
    
    def health_check(self) -> ServiceOperationResult:
        """Perform currency service health check."""
        try:
            # Check database connectivity
            currency_count = Currency.objects.filter(is_active=True).count()
            
            # Test currency conversion
            try:
                test_rate = get_exchange_rate('USD', 'BTC')
                conversion_healthy = True
            except CurrencyError:
                conversion_healthy = False
            
            # Check provider currencies
            provider_currency_count = ProviderCurrency.objects.filter(
                is_enabled=True
            ).count()
            
            stats = {
                'service_name': 'CurrencyService',
                'enabled_currencies': currency_count,
                'provider_currencies': provider_currency_count,
                'conversion_service_healthy': conversion_healthy,
                'django_currency_module': 'available'
            }
            
            if conversion_healthy and currency_count > 0:
                return self._create_success_result(
                    "CurrencyService is healthy",
                    stats
                )
            else:
                return self._create_error_result(
                    "CurrencyService has issues",
                    "service_unhealthy",
                    stats
                )
                
        except Exception as e:
            return self._handle_exception("health_check", e)
