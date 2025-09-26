"""
NowPayments provider for the Universal Payment System v2.0.

Implementation of NowPayments API integration with unified interface.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
import hmac
import hashlib
import json

from .base import BaseProvider, ProviderConfig, PaymentRequest
from ..types import ProviderResponse, ServiceOperationResult, NowPaymentsWebhook
from django_cfg.modules.django_currency import convert_currency


class NowPaymentsConfig(ProviderConfig):
    """
    NowPayments-specific configuration.
    
    Extends base config with NowPayments-specific fields.
    """
    
    ipn_secret: Optional[str] = Field(None, description="IPN callback secret")
    
    def __init__(self, **data):
        """Initialize with NowPayments defaults."""
        # Set NowPayments-specific defaults
        if 'provider_name' not in data:
            data['provider_name'] = 'nowpayments'
        
        if 'api_url' not in data:
            sandbox = data.get('sandbox', False)
            data['api_url'] = (
                'https://api-sandbox.nowpayments.io/v1' if sandbox 
                else 'https://api.nowpayments.io/v1'
            )
        
        if 'supported_currencies' not in data:
            data['supported_currencies'] = [
                'BTC', 'ETH', 'LTC', 'XMR', 'USDT', 'USDC', 'ADA', 'DOT'
            ]
        
        super().__init__(**data)


class NowPaymentsProvider(BaseProvider):
    """
    NowPayments provider implementation.
    
    Handles payment creation, status checking, and webhook validation for NowPayments.
    """
    
    def __init__(self, config: NowPaymentsConfig):
        """Initialize NowPayments provider."""
        super().__init__(config)
        self.config: NowPaymentsConfig = config
    
    def create_payment(self, request: PaymentRequest) -> ProviderResponse:
        """
        Create payment with NowPayments.
        
        Args:
            request: Payment creation request
            
        Returns:
            ProviderResponse: NowPayments response
        """
        try:
            self.logger.info("Creating NowPayments payment", extra={
                'amount_usd': request.amount_usd,
                'currency': request.currency_code,
                'order_id': request.order_id
            })
            
            # Convert USD to crypto amount
            try:
                crypto_amount = convert_currency(
                    request.amount_usd, 
                    'USD', 
                    request.currency_code
                )
            except Exception as e:
                return self._create_provider_response(
                    success=False,
                    raw_response={'error': f'Currency conversion failed: {e}'},
                    error_message=f'Currency conversion failed: {e}'
                )
            
            # Prepare NowPayments request
            payment_data = {
                'price_amount': request.amount_usd,
                'price_currency': 'USD',
                'pay_currency': request.currency_code,
                'order_id': request.order_id,
                'order_description': request.description or f'Payment {request.order_id}',
            }
            
            # Add optional fields
            if request.callback_url:
                payment_data['success_url'] = request.callback_url
            
            if request.cancel_url:
                payment_data['cancel_url'] = request.cancel_url
            
            if request.customer_email:
                payment_data['customer_email'] = request.customer_email
            
            # Add IPN callback URL (would be configured via webhook service)
            if hasattr(self, '_ipn_callback_url'):
                payment_data['ipn_callback_url'] = self._ipn_callback_url
            
            # Make API request
            headers = {
                'x-api-key': self.config.api_key
            }
            
            response_data = self._make_request(
                method='POST',
                endpoint='payment',
                data=payment_data,
                headers=headers
            )
            
            # Parse NowPayments response
            if 'payment_id' in response_data:
                # Successful payment creation
                payment_url = response_data.get('invoice_url') or response_data.get('pay_url')
                
                return self._create_provider_response(
                    success=True,
                    raw_response=response_data,
                    provider_payment_id=response_data['payment_id'],
                    status='waiting',  # NowPayments initial status
                    amount=Decimal(str(crypto_amount)),
                    currency=request.currency_code,
                    payment_url=payment_url,
                    wallet_address=response_data.get('pay_address'),
                    qr_code_url=response_data.get('qr_code_url'),
                    expires_at=self._parse_expiry_time(response_data.get('expiration_estimate_date'))
                )
            else:
                # Error response
                error_message = response_data.get('message', 'Unknown error')
                return self._create_provider_response(
                    success=False,
                    raw_response=response_data,
                    error_message=error_message
                )
                
        except Exception as e:
            self.logger.error(f"NowPayments payment creation failed: {e}", extra={
                'order_id': request.order_id
            })
            
            return self._create_provider_response(
                success=False,
                raw_response={'error': str(e)},
                error_message=f'Payment creation failed: {e}'
            )
    
    def get_payment_status(self, provider_payment_id: str) -> ProviderResponse:
        """
        Get payment status from NowPayments.
        
        Args:
            provider_payment_id: NowPayments payment ID
            
        Returns:
            ProviderResponse: Current payment status
        """
        try:
            self.logger.debug("Getting NowPayments payment status", extra={
                'payment_id': provider_payment_id
            })
            
            headers = {
                'x-api-key': self.config.api_key
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint=f'payment/{provider_payment_id}',
                headers=headers
            )
            
            if 'payment_status' in response_data:
                return self._create_provider_response(
                    success=True,
                    raw_response=response_data,
                    provider_payment_id=provider_payment_id,
                    status=response_data['payment_status'],
                    amount=Decimal(str(response_data.get('pay_amount', 0))),
                    currency=response_data.get('pay_currency'),
                    wallet_address=response_data.get('pay_address')
                )
            else:
                error_message = response_data.get('message', 'Payment not found')
                return self._create_provider_response(
                    success=False,
                    raw_response=response_data,
                    error_message=error_message
                )
                
        except Exception as e:
            self.logger.error(f"NowPayments status check failed: {e}", extra={
                'payment_id': provider_payment_id
            })
            
            return self._create_provider_response(
                success=False,
                raw_response={'error': str(e)},
                error_message=f'Status check failed: {e}'
            )
    
    def get_supported_currencies(self) -> ServiceOperationResult:
        """
        Get supported currencies from NowPayments.
        
        Returns:
            ServiceOperationResult: List of supported currencies
        """
        try:
            self.logger.debug("Getting NowPayments supported currencies")
            
            headers = {
                'x-api-key': self.config.api_key
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint='currencies',
                headers=headers
            )
            
            if 'currencies' in response_data:
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
    
    def validate_webhook(self, payload: Dict[str, Any], signature: str = None) -> ServiceOperationResult:
        """
        Validate NowPayments IPN webhook.
        
        Args:
            payload: Webhook payload
            signature: HMAC signature (optional)
            
        Returns:
            ServiceOperationResult: Validation result
        """
        try:
            self.logger.debug("Validating NowPayments webhook", extra={
                'has_signature': bool(signature),
                'payment_id': payload.get('payment_id')
            })
            
            # Validate payload structure
            try:
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
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> ServiceOperationResult:
        """
        Get exchange rate from NowPayments.
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            ServiceOperationResult: Exchange rate
        """
        try:
            self.logger.debug("Getting NowPayments exchange rate", extra={
                'from': from_currency,
                'to': to_currency
            })
            
            headers = {
                'x-api-key': self.config.api_key
            }
            
            response_data = self._make_request(
                method='GET',
                endpoint=f'exchange-amount/{from_currency}-{to_currency}',
                headers=headers
            )
            
            if 'estimated_amount' in response_data:
                rate = float(response_data['estimated_amount'])
                
                return ServiceOperationResult(
                    success=True,
                    message="Exchange rate retrieved",
                    data={
                        'from_currency': from_currency,
                        'to_currency': to_currency,
                        'rate': rate,
                        'provider': self.name
                    }
                )
            else:
                return ServiceOperationResult(
                    success=False,
                    message="Exchange rate not available",
                    error_code="rate_not_available"
                )
                
        except Exception as e:
            self.logger.error(f"NowPayments exchange rate failed: {e}")
            
            return ServiceOperationResult(
                success=False,
                message=f"Exchange rate error: {e}",
                error_code="rate_fetch_error"
            )
    
    def _validate_ipn_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Validate IPN signature using HMAC-SHA512.
        
        Args:
            payload: Webhook payload
            signature: Received signature
            
        Returns:
            bool: True if signature is valid
        """
        try:
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
        """
        Parse NowPayments expiry time string.
        
        Args:
            expiry_str: Expiry time string from NowPayments
            
        Returns:
            Optional[datetime]: Parsed expiry time
        """
        if not expiry_str:
            return None
        
        try:
            # NowPayments typically returns ISO format
            return datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        except Exception:
            self.logger.warning(f"Failed to parse expiry time: {expiry_str}")
            return None
    
    def set_ipn_callback_url(self, callback_url: str):
        """
        Set IPN callback URL for payments.
        
        Args:
            callback_url: IPN callback URL
        """
        self._ipn_callback_url = callback_url
        self.logger.info(f"Set IPN callback URL: {callback_url}")
    
    def health_check(self) -> ServiceOperationResult:
        """Perform NowPayments-specific health check."""
        try:
            # Test API connectivity by getting currencies
            currencies_result = self.get_supported_currencies()
            
            if currencies_result.success:
                currency_count = len(currencies_result.data.get('currencies', []))
                
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
                        'error': currencies_result.message
                    }
                )
                
        except Exception as e:
            return ServiceOperationResult(
                success=False,
                message=f"NowPayments health check error: {e}",
                error_code="health_check_error",
                data={'provider': self.name}
            )
