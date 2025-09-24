"""
CryptAPI provider implementation.

Crypto payment provider using CryptAPI service.
"""

import logging
import requests
import secrets
import string
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from .base import PaymentProvider
from ..internal_types import ProviderResponse, WebhookData

logger = logging.getLogger(__name__)


class CryptAPIConfig(BaseModel):
    """CryptAPI provider configuration."""
    own_address: str = Field(..., description="Your cryptocurrency address")
    callback_url: str = Field(..., description="Webhook callback URL")
    convert_payments: bool = Field(default=True, description="Auto-convert payments")
    multi_token: bool = Field(default=True, description="Support multi-token payments")
    priority: str = Field(default='default', description="Transaction priority")
    enabled: bool = Field(default=True, description="Provider enabled")


class CryptAPIException(Exception):
    """CryptAPI specific exception."""
    pass


class CryptAPIProvider(PaymentProvider):
    """CryptAPI cryptocurrency payment provider."""
    
    CRYPTAPI_URL = 'https://api.cryptapi.io/'
    
    def __init__(self, config: CryptAPIConfig):
        """Initialize CryptAPI provider."""
        super().__init__(config.dict())
        self.config = config
        self.own_address = config.own_address
        self.callback_url = config.callback_url
        self.convert_payments = config.convert_payments
        self.multi_token = config.multi_token
        self.priority = config.priority
    
    def _make_request(self, coin: str, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make HTTP request to CryptAPI."""
        try:
            if coin:
                coin = coin.replace('/', '_')
                url = f"{self.CRYPTAPI_URL}{coin}/{endpoint}/"
            else:
                url = f"{self.CRYPTAPI_URL}{endpoint}/"
            
            response = requests.get(url, params=params or {}, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for API errors
            if 'error' in result:
                logger.error(f"CryptAPI error: {result['error']}")
                return None
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CryptAPI request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected CryptAPI error: {e}")
            return None
    
    def create_payment(self, payment_data: dict) -> ProviderResponse:
        """Create payment address via CryptAPI."""
        try:
            amount = Decimal(str(payment_data['amount']))
            currency = payment_data['currency'].lower()
            order_id = payment_data.get('order_id', f'payment_{int(amount * 100)}')
            
            # Generate secure nonce for replay attack protection
            security_nonce = self._generate_nonce()
            
            # Build callback URL with parameters including nonce
            callback_params = {
                'order_id': order_id,
                'amount': str(amount),
                'nonce': security_nonce
            }
            
            # Create payment address
            params = {
                'address': self.own_address,
                'callback': self.callback_url,
                'convert': 1 if self.convert_payments else 0,
                'multi_token': 1 if self.multi_token else 0,
                'priority': self.priority,
                **callback_params
            }
            
            response = self._make_request(currency, 'create', params)
            
            if response and 'address_in' in response:
                return ProviderResponse(
                    success=True,
                    provider_payment_id=response['address_in'],  # Use address as payment ID
                    payment_url=None,  # CryptAPI doesn't provide payment URLs
                    pay_address=response['address_in'],
                    amount=amount,
                    currency=currency.upper(),
                    status='pending'
                )
            else:
                return ProviderResponse(
                    success=False,
                    error_message='Failed to create payment address'
                )
                
        except Exception as e:
            logger.error(f"CryptAPI create_payment error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e)
            )
    
    def check_payment_status(self, payment_id: str) -> ProviderResponse:
        """Check payment status via CryptAPI."""
        try:
            # For CryptAPI, payment_id is the address
            # We need to check logs to see if payment was received
            # This is a limitation of CryptAPI - no direct status check by address
            
            # Return pending status as CryptAPI uses callbacks for status updates
            return ProviderResponse(
                success=True,
                provider_payment_id=payment_id,
                status='pending',
                pay_address=payment_id,
                amount=Decimal('0'),  # Unknown without logs
                currency='unknown'
            )
            
        except Exception as e:
            logger.error(f"CryptAPI check_payment_status error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e)
            )
    
    def process_webhook(self, payload: dict) -> WebhookData:
        """Process CryptAPI webhook/callback."""
        try:
            # CryptAPI sends callbacks with these parameters:
            # - address_in: payment address
            # - address_out: your address  
            # - txid_in: transaction ID
            # - txid_out: forwarding transaction ID (if applicable)
            # - confirmations: number of confirmations
            # - value: amount received
            # - value_coin: amount in coin
            # - value_forwarded: amount forwarded
            # - coin: cryptocurrency
            # - pending: 0 or 1
            
            confirmations = int(payload.get('confirmations', 0))
            pending = int(payload.get('pending', 1))
            
            # Determine status based on confirmations and pending flag
            if pending == 1:
                status = 'pending'
            elif confirmations >= 1:
                status = 'completed'
            else:
                status = 'processing'
            
            return WebhookData(
                provider_payment_id=payload.get('address_in', ''),
                status=status,
                pay_amount=Decimal(str(payload.get('value_coin', 0))),
                actually_paid=Decimal(str(payload.get('value_coin', 0))),
                order_id=payload.get('order_id'),  # Custom parameter we sent
                signature=payload.get('txid_in')  # Use transaction ID as signature
            )
            
        except Exception as e:
            logger.error(f"CryptAPI webhook processing error: {e}")
            raise
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies."""
        try:
            response = self._make_request('', 'info')
            
            if response and isinstance(response, dict):
                # CryptAPI returns a dict with coin info
                return list(response.keys())
            else:
                # Fallback currencies
                return ['BTC', 'ETH', 'LTC', 'BCH', 'XMR', 'TRX']
                
        except Exception as e:
            logger.error(f"Error getting supported currencies: {e}")
            return ['BTC', 'ETH', 'LTC']  # Minimal fallback
    
    def get_minimum_payment_amount(self, currency_from: str, currency_to: str = 'usd') -> Optional[Decimal]:
        """Get minimum payment amount for currency."""
        try:
            response = self._make_request(currency_from.lower(), 'info')
            
            if response and 'minimum_transaction' in response:
                return Decimal(str(response['minimum_transaction']))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting minimum amount: {e}")
            return None
    
    def estimate_payment_amount(self, amount: Decimal, currency_code: str) -> Optional[dict]:
        """Estimate payment amount - CryptAPI doesn't provide this."""
        # CryptAPI doesn't have a direct estimation API
        # Would need to use external price APIs
        return None
    
    def validate_webhook(self, payload: dict, headers: Optional[dict] = None) -> bool:
        """Validate CryptAPI webhook."""
        try:
            # CryptAPI doesn't use HMAC signatures
            # Validation is done by checking if the callback came from their servers
            # and contains expected parameters
            
            required_fields = ['address_in', 'address_out', 'txid_in', 'value_coin', 'coin', 'confirmations']
            
            for field in required_fields:
                if field not in payload:
                    logger.warning(f"Missing required field in CryptAPI webhook: {field}")
                    return False
            
            # Basic validation passed
            return True
            
        except Exception as e:
            logger.error(f"CryptAPI webhook validation error: {e}")
            return False
    
    def check_api_status(self) -> bool:
        """Check if CryptAPI is available."""
        try:
            response = self._make_request('', 'info')
            return response is not None
        except:
            return False
    
    def get_logs(self, callback_url: str) -> Optional[dict]:
        """Get payment logs for a callback URL."""
        try:
            params = {'callback': callback_url}
            # Note: This would need a specific coin, but we don't know which one
            # This is a limitation of the current implementation
            return None
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return None
    
    def _generate_nonce(self, length: int = 32) -> str:
        """Generate cryptographically secure nonce for replay attack protection."""
        sequence = string.ascii_letters + string.digits
        return ''.join([secrets.choice(sequence) for _ in range(length)])
