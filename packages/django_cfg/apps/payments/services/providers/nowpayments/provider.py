"""
NowPayments provider implementation for Universal Payment System v2.0.

Enhanced crypto payment provider with currency synchronization.
"""

import requests
import hashlib
import hmac
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from django_cfg.modules.django_logging import get_logger
from ..base import BaseProvider
from ..models import PaymentRequest
from ...types import ProviderResponse, ServiceOperationResult
from .models import (
    NowPaymentsProviderConfig, 
    NowPaymentsCurrency, 
    NowPaymentsFullCurrenciesResponse
)
from ..models import (
    UniversalCurrency,
    UniversalCurrenciesResponse,
    CurrencySyncResult
)
from .sync import NowPaymentsCurrencySync
from .parsers import NowPaymentsCurrencyParser
from .config import NowPaymentsConfig as Config

logger = get_logger("nowpayments")


class NowPaymentsProvider(BaseProvider):
    """NowPayments cryptocurrency payment provider."""
    
    # Map NowPayments status to universal status
    STATUS_MAPPING = {
        'waiting': 'pending',
        'confirming': 'processing', 
        'confirmed': 'completed',
        'sending': 'processing',
        'partially_paid': 'pending',
        'finished': 'completed',
        'failed': 'failed',
        'refunded': 'refunded',
        'expired': 'expired'
    }
    
    def __init__(self, config: NowPaymentsProviderConfig):
        """Initialize NowPayments provider."""
        super().__init__(config)
        self.config: NowPaymentsProviderConfig = config
        self.sync_service = NowPaymentsCurrencySync(self.name)
        self.parser = NowPaymentsCurrencyParser()
        
        # Log initialization
        api_key_str = str(self.config.api_key)
        if hasattr(self.config.api_key, 'get_secret_value'):
            api_key_str = self.config.api_key.get_secret_value()
        
        logger.info(
            f"🔑 NowPayments initialized: api_key={api_key_str[:10]}..., "
            f"sandbox={self.is_sandbox}, base_url={self.config.api_url}"
        )
    
    # Override BaseProvider configuration methods
    def get_fee_percentage(self, currency_code: str = None, currency_type: str = None) -> Decimal:
        """Get NowPayments fee percentage."""
        return Config.FEE_PERCENTAGE
    
    def get_fixed_fee_usd(self, currency_code: str = None, currency_type: str = None) -> Decimal:
        """Get NowPayments fixed fee."""
        return Config.FIXED_FEE_USD
    
    def get_min_amount_usd(self, currency_code: str = None, currency_type: str = None, is_stable: bool = False) -> Decimal:
        """Get NowPayments minimum amount."""
        return Config.get_min_amount()
    
    def get_max_amount_usd(self, currency_code: str = None, currency_type: str = None) -> Decimal:
        """Get NowPayments maximum amount."""
        return Config.MAX_AMOUNT_USD
    
    def get_confirmation_blocks(self, network_code: str) -> int:
        """Get confirmation blocks for network."""
        return Config.get_confirmation_blocks(network_code)
    
    def get_network_name(self, network_code: str) -> str:
        """Get human-readable network name."""
        return Config.get_network_name(network_code)
    
    def create_payment(self, request: PaymentRequest) -> ProviderResponse:
        """Create payment with NowPayments."""
        try:
            self.logger.info("Creating NowPayments payment", extra={
                'amount_usd': request.amount_usd,
                'currency': request.currency_code,
                'order_id': request.order_id
            })
            
            # Use provider_currency_code from metadata if available, otherwise use original currency_code
            provider_currency_code = request.metadata.get('provider_currency_code', request.currency_code)
            
            # Prepare NowPayments request
            payment_data = {
                'price_amount': request.amount_usd,
                'price_currency': 'USD',
                'pay_currency': provider_currency_code,  # Use provider-specific currency code
                'order_id': request.order_id,
                'order_description': request.description or f'Payment {request.order_id}',
            }
            
            # Log the request data for debugging
            self.logger.info("NowPayments request data", extra={
                'payment_data': payment_data,
                'original_currency_code': request.currency_code,
                'provider_currency_code': provider_currency_code,
                'request_amount_usd': request.amount_usd,
                'request_order_id': request.order_id
            })
            
            # Add optional fields
            if request.callback_url:
                payment_data['success_url'] = request.callback_url
            
            if request.cancel_url:
                payment_data['cancel_url'] = request.cancel_url
            
            if request.customer_email:
                payment_data['customer_email'] = request.customer_email
            
            # Add IPN callback URL if configured
            if self.config.callback_url:
                payment_data['ipn_callback_url'] = self.config.callback_url
            
            # Make API request
            headers = {
                'x-api-key': self._get_api_key()
            }
            
            response_data = self._make_request(
                method='POST',
                endpoint='payment',
                data=payment_data,
                headers=headers
            )
            
            # Parse NowPayments response
            if response_data and 'payment_id' in response_data:
                # Log the full response for debugging
                self.logger.info("NowPayments response received", extra={
                    'payment_id': response_data.get('payment_id'),
                    'pay_address': response_data.get('pay_address'),
                    'pay_amount': response_data.get('pay_amount'),
                    'full_response': response_data
                })
                
                # Successful payment creation
                payment_url = response_data.get('invoice_url') or response_data.get('pay_url')
                
                return self._create_provider_response(
                    success=True,
                    raw_response=response_data,
                    provider_payment_id=response_data['payment_id'],
                    status='waiting',  # NowPayments initial status
                    amount=Decimal(str(response_data.get('pay_amount', 0))),
                    currency=request.currency_code,
                    payment_url=payment_url,
                    wallet_address=response_data.get('pay_address'),
                    expires_at=self._parse_expiry_time(response_data.get('expiration_estimate_date'))
                )
            else:
                # Error response
                error_message = response_data.get('message', 'Unknown error') if response_data else 'No response'
                return self._create_provider_response(
                    success=False,
                    raw_response=response_data or {},
                    error_message=error_message
                )
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"NowPayments payment creation failed: {error_msg}", extra={
                'order_id': request.order_id,
                'error_type': type(e).__name__
            })
            
            # Provide user-friendly error messages
            if "IP address blocked" in error_msg:
                user_message = "NowPayments has blocked this IP address. Please contact support or try from a different location."
            elif "Authentication failed" in error_msg:
                user_message = "Invalid NowPayments API key. Please check your configuration."
            elif "Bad request" in error_msg:
                user_message = f"Invalid payment request: {error_msg}"
            elif "Rate limit exceeded" in error_msg:
                user_message = "Too many requests to NowPayments. Please try again in a few minutes."
            elif "server error" in error_msg.lower():
                user_message = "NowPayments service is temporarily unavailable. Please try again later."
            else:
                user_message = f"Payment creation failed: {error_msg}"
            
            return self._create_provider_response(
                success=False,
                raw_response={'error': error_msg, 'error_type': type(e).__name__},
                error_message=user_message
            )
    
    def get_payment_status(self, provider_payment_id: str) -> ProviderResponse:
        """Get payment status from NowPayments."""
        try:
            self.logger.debug("Getting NowPayments payment status", extra={
                'payment_id': provider_payment_id
            })
            
            headers = {
                'x-api-key': self._get_api_key()
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint=f'payment/{provider_payment_id}',
                headers=headers
            )
            
            if response_data and 'payment_status' in response_data:
                provider_status = response_data['payment_status']
                universal_status = self.STATUS_MAPPING.get(provider_status, 'unknown')
                
                return self._create_provider_response(
                    success=True,
                    raw_response=response_data,
                    provider_payment_id=provider_payment_id,
                    status=universal_status,
                    amount=Decimal(str(response_data.get('pay_amount', 0))),
                    currency=response_data.get('pay_currency'),
                    wallet_address=response_data.get('pay_address')
                )
            else:
                error_message = response_data.get('message', 'Payment not found') if response_data else 'No response'
                return self._create_provider_response(
                    success=False,
                    raw_response=response_data or {},
                    error_message=error_message
                )
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"NowPayments status check failed: {error_msg}", extra={
                'payment_id': provider_payment_id,
                'error_type': type(e).__name__
            })
            
            # Provide user-friendly error messages
            if "IP address blocked" in error_msg:
                user_message = "NowPayments has blocked this IP address. Cannot check payment status."
            elif "Authentication failed" in error_msg:
                user_message = "Invalid NowPayments API key. Cannot check payment status."
            elif "server error" in error_msg.lower():
                user_message = "NowPayments service is temporarily unavailable. Please try again later."
            else:
                user_message = f"Status check failed: {error_msg}"
            
            return self._create_provider_response(
                success=False,
                raw_response={'error': error_msg, 'error_type': type(e).__name__},
                error_message=user_message
            )
    
    def get_supported_currencies(self) -> ServiceOperationResult:
        """Get supported currencies from NowPayments."""
        try:
            self.logger.debug("Getting NowPayments supported currencies")
            
            headers = {
                'x-api-key': self._get_api_key()
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint='full-currencies',
                headers=headers
            )
            
            if response_data and 'currencies' in response_data:
                currencies = response_data['currencies']
                
                return ServiceOperationResult(
                    success=True,
                    message=f"Retrieved {len(currencies)} supported currencies",
                    data={
                        'currencies': currencies,
                        'count': len(currencies),
                        'provider': self.name
                    }
                )
            else:
                return ServiceOperationResult(
                    success=False,
                    message="Failed to get currencies from NowPayments",
                    error_code="currencies_fetch_failed"
                )
                
        except Exception as e:
            self.logger.error(f"NowPayments currencies fetch failed: {e}")
            
            return ServiceOperationResult(
                success=False,
                message=f"Currencies fetch error: {e}",
                error_code="currencies_fetch_error"
            )
    
    def get_parsed_currencies(self) -> UniversalCurrenciesResponse:
        """Get parsed and normalized currencies from NowPayments."""
        try:
            # Use full-currencies endpoint to get detailed currency info
            headers = {
                'x-api-key': self._get_api_key()
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint='full-currencies',
                headers=headers
            )
            
            if not response_data or 'currencies' not in response_data:
                return UniversalCurrenciesResponse(currencies=[])
            
            universal_currencies = []
            
            for currency_data in response_data['currencies']:
                if not currency_data.get('enable', True):
                    continue  # Skip disabled currencies
                
                provider_code = currency_data.get('code', '').upper()
                if not provider_code:
                    continue
                
                # Parse provider code into base currency + network using API data
                currency_name = currency_data.get('name', '')
                api_network = currency_data.get('network')
                ticker = currency_data.get('ticker', '')
                
                # Use parser to extract base currency and network
                parse_result = self.parser.parse_currency_code(
                    provider_code, currency_name, api_network, ticker
                )
                
                # Skip currencies that should be filtered out (empty network duplicates)
                if parse_result[0] is None:
                    continue
                
                base_currency_code, network_code = parse_result
                
                # Determine currency type
                currency_type = 'fiat' if network_code is None else 'crypto'
                
                # Generate proper currency name
                proper_name = self.parser.generate_currency_name(
                    base_currency_code, network_code, currency_name
                )
                
                universal_currency = UniversalCurrency(
                    provider_currency_code=provider_code,
                    base_currency_code=base_currency_code,
                    network_code=network_code,
                    name=proper_name,  # Use generated name instead of API name
                    currency_type=currency_type,
                    is_enabled=currency_data.get('enable', True),
                    is_popular=currency_data.get('is_popular', False),
                    is_stable=currency_data.get('is_stable', False),
                    priority=currency_data.get('priority', 0),
                    logo_url=currency_data.get('logo_url', ''),
                    available_for_payment=currency_data.get('available_for_payment', True),
                    available_for_payout=currency_data.get('available_for_payout', True),
                    raw_data=currency_data
                )
                
                universal_currencies.append(universal_currency)
            
            return UniversalCurrenciesResponse(currencies=universal_currencies)
            
        except Exception as e:
            logger.error(f"Error parsing currencies: {e}")
            return UniversalCurrenciesResponse(currencies=[])
    
    def sync_currencies_to_db(self) -> CurrencySyncResult:
        """Sync currencies from NowPayments API to database."""
        try:
            self.logger.info("Starting NowPayments currency synchronization")
            
            # Get parsed currencies from API
            currencies_response = self.get_parsed_currencies()
            
            if not currencies_response.currencies:
                return CurrencySyncResult(
                    errors=["No currencies received from NowPayments API"]
                )
            
            # Sync to database
            result = self.sync_service.sync_currencies_to_db(currencies_response.currencies)
            
            self.logger.info(
                f"NowPayments currency sync completed: "
                f"{result.currencies_created} currencies created, "
                f"{result.provider_currencies_created} provider currencies created, "
                f"{len(result.errors)} errors"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Currency sync failed: {e}"
            self.logger.error(error_msg)
            return CurrencySyncResult(errors=[error_msg])
    
    def validate_webhook(self, payload: Dict[str, Any], signature: str = None) -> ServiceOperationResult:
        """Validate NowPayments IPN webhook."""
        try:
            self.logger.debug("Validating NowPayments webhook", extra={
                'has_signature': bool(signature),
                'payment_id': payload.get('payment_id')
            })
            
            # Validate payload structure
            try:
                from .models import NowPaymentsWebhook
                webhook_data = NowPaymentsWebhook(**payload)
            except Exception as e:
                return ServiceOperationResult(
                    success=False,
                    message=f"Invalid webhook payload: {e}",
                    error_code="invalid_payload"
                )
            
            # Validate signature if provided and secret is configured
            if signature and self.config.ipn_secret:
                is_valid_signature = self._validate_ipn_signature(payload, signature)
                if not is_valid_signature:
                    return ServiceOperationResult(
                        success=False,
                        message="Invalid webhook signature",
                        error_code="invalid_signature"
                    )
            
            return ServiceOperationResult(
                success=True,
                message="Webhook validated successfully",
                data={
                    'provider': self.name,
                    'payment_id': webhook_data.payment_id,
                    'status': webhook_data.payment_status,
                    'signature_validated': bool(signature and self.config.ipn_secret),
                    'webhook_data': webhook_data.model_dump()
                }
            )
            
        except Exception as e:
            self.logger.error(f"NowPayments webhook validation failed: {e}")
            
            return ServiceOperationResult(
                success=False,
                message=f"Webhook validation error: {e}",
                error_code="validation_error"
            )
    
    def health_check(self) -> ServiceOperationResult:
        """Perform NowPayments-specific health check."""
        try:
            # Test API connectivity by getting status
            headers = {
                'x-api-key': self._get_api_key()
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint='status',
                headers=headers
            )
            
            if response_data and response_data.get('message') == 'OK':
                # Also check currencies endpoint
                currencies_result = self.get_supported_currencies()
                currency_count = len(currencies_result.data.get('currencies', [])) if currencies_result.success else 0
                
                return ServiceOperationResult(
                    success=True,
                    message="NowPayments provider is healthy",
                    data={
                        'provider': self.name,
                        'sandbox': self.is_sandbox,
                        'api_url': self.config.api_url,
                        'supported_currencies': currency_count,
                        'has_ipn_secret': bool(self.config.ipn_secret),
                        'api_key_configured': bool(self.config.api_key)
                    }
                )
            else:
                return ServiceOperationResult(
                    success=False,
                    message="NowPayments API connectivity failed",
                    error_code="api_connectivity_failed",
                    data={
                        'provider': self.name,
                        'response': response_data
                    }
                )
                
        except Exception as e:
            return ServiceOperationResult(
                success=False,
                message=f"NowPayments health check error: {e}",
                error_code="health_check_error",
                data={'provider': self.name}
            )
    
    
    def _validate_ipn_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Validate IPN signature using HMAC-SHA512."""
        try:
            import json
            
            # Sort payload and create canonical string
            sorted_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.config.ipn_secret.encode('utf-8'),
                sorted_payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            self.logger.error(f"Signature validation error: {e}")
            return False
    
    def _parse_expiry_time(self, expiry_str: Optional[str]) -> Optional[datetime]:
        """Parse NowPayments expiry time string."""
        if not expiry_str:
            return None
        
        try:
            # NowPayments typically returns ISO format
            return datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        except Exception:
            self.logger.warning(f"Failed to parse expiry time: {expiry_str}")
            return None
    
    def _get_api_key(self) -> str:
        """Get API key as string."""
        if hasattr(self.config.api_key, 'get_secret_value'):
            return self.config.api_key.get_secret_value()
        return str(self.config.api_key)
