"""
NowPayments provider implementation.

Enhanced crypto payment provider with minimal typing.
"""

import logging
import requests
import hashlib
import hmac
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from .base import PaymentProvider
from ..internal_types import ProviderResponse, WebhookData

logger = logging.getLogger(__name__)


class NowPaymentsConfig(BaseModel):
    """NowPayments provider configuration."""
    api_key: str = Field(..., description="NowPayments API key")
    sandbox: bool = Field(default=False, description="Use sandbox mode")
    ipn_secret: Optional[str] = Field(default=None, description="IPN secret for webhook validation")
    callback_url: Optional[str] = Field(default=None, description="Webhook callback URL")
    success_url: Optional[str] = Field(default=None, description="Payment success redirect URL")
    cancel_url: Optional[str] = Field(default=None, description="Payment cancel redirect URL")
    enabled: bool = Field(default=True, description="Provider enabled")


class NowPaymentsProvider(PaymentProvider):
    """NowPayments cryptocurrency payment provider."""
    
    def __init__(self, config: NowPaymentsConfig):
        """Initialize NowPayments provider."""
        super().__init__(config.dict())
        self.config = config
        self.api_key = config.api_key
        self.sandbox = config.sandbox
        self.ipn_secret = config.ipn_secret or ''
        self.base_url = self._get_base_url()
        
        # Configurable URLs 
        self.callback_url = config.callback_url
        self.success_url = config.success_url
        self.cancel_url = config.cancel_url
        
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _get_base_url(self) -> str:
        """Get base URL based on sandbox mode."""
        if self.sandbox:
            return 'https://api-sandbox.nowpayments.io/v1'
        return 'https://api.nowpayments.io/v1'
    
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> Optional[dict]:
        """Make HTTP request to NowPayments API with error handling."""
        try:
            url = f"{self.base_url}/{endpoint}"
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NowPayments API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in NowPayments request: {e}")
            return None
    
    def create_payment(self, payment_data: dict) -> ProviderResponse:
        """Create payment via NowPayments API."""
        try:
            amount = Decimal(str(payment_data['amount']))
            currency = payment_data['currency']
            order_id = payment_data.get('order_id', f'payment_{int(amount * 100)}_{currency}')
            
            payment_request = {
                'price_amount': float(amount),
                'price_currency': 'usd',  # Base currency
                'pay_currency': currency,
                'order_id': order_id,
                'order_description': payment_data.get('description', f'Payment {order_id}'),
            }
            
            # Add optional URLs
            if self.success_url:
                payment_request['success_url'] = self.success_url
            if self.cancel_url:
                payment_request['cancel_url'] = self.cancel_url
            if self.callback_url:
                payment_request['ipn_callback_url'] = self.callback_url
            
            response = self._make_request('POST', 'payment', payment_request)
            
            if response:
                return ProviderResponse(
                    success=True,
                    provider_payment_id=response.get('payment_id'),
                    payment_url=response.get('invoice_url'),
                    pay_address=response.get('pay_address'),
                    amount=Decimal(str(response.get('pay_amount', 0))),
                    currency=response.get('pay_currency'),
                    status='pending'
                )
            else:
                return ProviderResponse(
                    success=False,
                    error_message='Failed to create payment'
                )
                
        except Exception as e:
            logger.error(f"NowPayments create_payment error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e)
            )
    
    def check_payment_status(self, payment_id: str) -> ProviderResponse:
        """Check payment status via NowPayments API."""
        try:
            response = self._make_request('GET', f'payment/{payment_id}')
            
            if response:
                # Map NowPayments status to universal status
                status_mapping = {
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
                
                provider_status = response.get('payment_status', 'unknown')
                universal_status = status_mapping.get(provider_status, 'unknown')
                
                return ProviderResponse(
                    success=True,
                    provider_payment_id=response.get('payment_id'),
                    status=universal_status,
                    pay_address=response.get('pay_address'),
                    amount=Decimal(str(response.get('pay_amount', 0))),
                    currency=response.get('pay_currency')
                )
            else:
                return ProviderResponse(
                    success=False,
                    error_message='Payment not found'
                )
                
        except Exception as e:
            logger.error(f"NowPayments check_payment_status error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e)
            )
    
    def process_webhook(self, payload: dict) -> WebhookData:
        """Process NowPayments webhook."""
        try:
            # Map status
            status_mapping = {
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
            
            provider_status = payload.get('payment_status', 'unknown')
            universal_status = status_mapping.get(provider_status, 'unknown')
            
            return WebhookData(
                provider_payment_id=str(payload.get('payment_id', '')),
                status=universal_status,
                pay_amount=Decimal(str(payload.get('pay_amount', 0))),
                actually_paid=Decimal(str(payload.get('actually_paid', 0))),
                order_id=payload.get('order_id'),
                signature=payload.get('signature')
            )
            
        except Exception as e:
            logger.error(f"NowPayments webhook processing error: {e}")
            raise
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies."""
        try:
            response = self._make_request('GET', 'currencies')
            
            if response and 'currencies' in response:
                return response['currencies']
            else:
                # Fallback currencies
                return ['BTC', 'ETH', 'LTC', 'BCH', 'XMR', 'TRX', 'BNB']
                
        except Exception as e:
            logger.error(f"Error getting supported currencies: {e}")
            return ['BTC', 'ETH', 'LTC']  # Minimal fallback
    
    def get_minimum_payment_amount(self, currency_from: str, currency_to: str = 'usd') -> Optional[Decimal]:
        """Get minimum payment amount for currency pair."""
        try:
            response = self._make_request('GET', 'min-amount', {
                'currency_from': currency_from,
                'currency_to': currency_to
            })
            
            if response and 'min_amount' in response:
                return Decimal(str(response['min_amount']))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting minimum amount: {e}")
            return None
    
    def estimate_payment_amount(self, amount: Decimal, currency_code: str) -> Optional[dict]:
        """Estimate payment amount in target currency."""
        try:
            response = self._make_request('GET', 'estimate', {
                'amount': float(amount),
                'currency_from': 'usd',
                'currency_to': currency_code
            })
            
            if response and 'estimated_amount' in response:
                return {
                    'estimated_amount': Decimal(str(response['estimated_amount'])),
                    'currency_from': response.get('currency_from'),
                    'currency_to': response.get('currency_to'),
                    'fee_amount': Decimal(str(response.get('fee_amount', 0)))
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error estimating payment amount: {e}")
            return None
    
    def validate_webhook(self, payload: dict, headers: Optional[dict] = None) -> bool:
        """Validate NowPayments webhook signature."""
        try:
            if not self.ipn_secret:
                logger.warning("IPN secret not configured, skipping webhook validation")
                return True
            
            if not headers:
                logger.warning("No headers provided for webhook validation")
                return False
            
            # Get signature from headers
            signature = headers.get('x-nowpayments-sig')
            if not signature:
                logger.warning("No signature found in webhook headers")
                return False
            
            # TODO: Implement proper HMAC signature validation
            # This requires the raw payload body for proper validation
            logger.info("Webhook signature validation placeholder")
            return True
            
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            return False
    
    def check_api_status(self) -> bool:
        """Check if NowPayments API is available."""
        try:
            response = self._make_request('GET', 'status')
            return response is not None and response.get('message') == 'OK'
        except:
            return False
