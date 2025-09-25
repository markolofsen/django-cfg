"""
CryptAPI provider implementation.

Crypto payment provider using CryptAPI service.
"""

import requests
import secrets
import string
import base64
from typing import Optional, List, Dict, Any
from decimal import Decimal
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from ..base import PaymentProvider
from ...internal_types import ProviderResponse, WebhookData, PaymentAmountEstimate
from .models import CryptAPIConfig, CryptAPICallback
from django_cfg.modules.django_logger import get_logger

logger = get_logger("cryptapi")


class CryptAPIException(Exception):
    """CryptAPI specific exception."""
    pass


class CryptAPIProvider(PaymentProvider):
    """CryptAPI cryptocurrency payment provider."""
    
    CRYPTAPI_URL = 'https://api.cryptapi.io/'
    
    def __init__(self, config: CryptAPIConfig):
        """Initialize CryptAPI provider."""
        super().__init__(config)
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
        """Create payment address via CryptAPI with full parameter support according to documentation."""
        try:
            # Required parameters
            amount = Decimal(str(payment_data['amount']))
            currency = payment_data['currency'].lower()
            order_id = payment_data.get('order_id', f'payment_{int(amount * 100)}')
            
            # Build callback URL with custom parameters
            callback_url = payment_data.get('callback_url', self.config.callback_url)
            
            # Add custom parameters to callback URL for tracking
            callback_params = []
            if order_id:
                callback_params.append(f'order_id={order_id}')
            if 'user_id' in payment_data:
                callback_params.append(f'user_id={payment_data["user_id"]}')
            
            # Generate nonce for security
            security_nonce = self._generate_nonce()
            callback_params.append(f'nonce={security_nonce}')
            
            # Build full callback URL
            if callback_params:
                separator = '&' if '?' in callback_url else '?'
                callback_url = f"{callback_url}{separator}{'&'.join(callback_params)}"
            
            # Prepare API parameters according to documentation
            params = {
                'address': payment_data.get('address', self.config.own_address),
                'callback': callback_url,
            }
            
            # Optional parameters from documentation
            if payment_data.get('pending', False) or self.config.convert_payments:
                params['pending'] = 1
            
            if 'confirmations' in payment_data:
                params['confirmations'] = int(payment_data['confirmations'])
            
            if payment_data.get('post', False):
                params['post'] = 1
                
            if payment_data.get('json', True):
                params['json'] = 1
                
            if self.config.priority and self.config.priority != 'default':
                params['priority'] = self.config.priority
                
            if self.config.multi_token:
                params['multi_token'] = 1
                
            if self.config.convert_payments:
                params['convert'] = 1
            
            # Handle multi-address splitting if provided
            if 'addresses' in payment_data and isinstance(payment_data['addresses'], list):
                # Format: percentage@address|percentage@address
                address_parts = []
                for addr_info in payment_data['addresses']:
                    if isinstance(addr_info, dict) and 'address' in addr_info and 'percentage' in addr_info:
                        address_parts.append(f"{addr_info['percentage']}@{addr_info['address']}")
                if address_parts:
                    params['address'] = '|'.join(address_parts)
            
            # Make API request using ticker/create endpoint
            response = self._make_request(currency, 'create', params)
            
            if response and 'address_in' in response:
                return ProviderResponse(
                    success=True,
                    provider_payment_id=response['address_in'],
                    payment_url=None,  # CryptAPI doesn't provide hosted payment pages
                    pay_address=response['address_in'],
                    amount=amount,
                    currency=currency.upper(),
                    status='pending',
                    data={
                        'callback_url': response.get('callback_url'),
                        'minimum_transaction_coin': response.get('minimum_transaction_coin'),
                        'priority': response.get('priority'),
                        'nonce': security_nonce
                    }
                )
            else:
                # Standardized error message format
                if response and 'error' in response:
                    error_msg = f"CryptAPI error: {response['error']}"
                elif response:
                    error_msg = "CryptAPI error: Invalid response format"
                else:
                    error_msg = "CryptAPI error: No response from API"
                    
                return ProviderResponse(
                    success=False,
                    error_message=error_msg
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
        """Process CryptAPI webhook according to official documentation."""
        try:
            # Parse and validate webhook using Pydantic model
            webhook = CryptAPICallback(**payload)
            
            # Determine status based on pending flag
            pending = webhook.pending if webhook.pending is not None else 0
            if pending == 1:
                status = 'pending'
            elif pending == 0:
                # Confirmed webhook - check confirmations if available
                if webhook.confirmations is not None and webhook.confirmations >= 1:
                    status = 'completed'
                else:
                    status = 'processing'
            else:
                status = 'unknown'
            
            # Use value_coin for confirmed webhooks, or estimate for pending
            pay_amount = webhook.value_coin if webhook.value_coin is not None else Decimal('0')
            
            # Use UUID if available, otherwise fall back to address_in
            payment_id = webhook.uuid if webhook.uuid else webhook.address_in
            
            return WebhookData(
                provider_payment_id=payment_id,
                status=status,
                pay_amount=pay_amount,
                pay_currency=webhook.coin.lower(),
                actually_paid=pay_amount,
                order_id=payload.get('order_id'),  # Custom parameter from callback URL
                signature=webhook.txid_in  # Transaction hash as signature
            )
            
        except Exception as e:
            logger.error(f"CryptAPI webhook processing error: {e}")
            raise
    
    def get_logs(self, callback_url: str) -> Optional[dict]:
        """Get payment logs for a specific callback URL."""
        try:
            response = self._make_request('GET', 'logs', {
                'callback': callback_url
            })
            
            if response:
                return {
                    'success': True,
                    'logs': response,
                    'callback_url': callback_url
                }
            
            return None
            
        except Exception as e:
            logger.error(f"CryptAPI get_logs error: {e}")
            return None
    
    def generate_qr_code(self, address: str, amount: Optional[Decimal] = None, 
                        size: int = 512) -> Optional[dict]:
        """Generate QR code for payment address."""
        try:
            params = {
                'address': address,
                'size': size
            }
            
            if amount:
                params['value'] = float(amount)
            
            response = self._make_request('GET', 'qrcode', params)
            
            if response and 'qr_code' in response:
                return {
                    'success': True,
                    'qr_code_url': response['qr_code'],
                    'address': address,
                    'amount': amount,
                    'size': size
                }
            
            return None
            
        except Exception as e:
            logger.error(f"CryptAPI generate_qr_code error: {e}")
            return None

    def get_supported_currencies(self) -> ProviderResponse:
        """Get list of supported currencies."""
        try:
            response = self._make_request('', 'info')
            
            if response and isinstance(response, dict):
                # CryptAPI returns a dict with coin info
                currencies = list(response.keys())
                return ProviderResponse(
                    success=True,
                    data={'currencies': [{'currency_code': c, 'name': c.upper()} for c in currencies]}
                )
            else:
                return ProviderResponse(
                    success=False,
                    error_message="Invalid response from CryptAPI info endpoint"
                )
                
        except Exception as e:
            logger.error(f"Error getting supported currencies: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Failed to get currencies from CryptAPI: {str(e)}"
            )
    
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
    
    def validate_webhook(self, payload: dict, headers: Optional[dict] = None, raw_body: Optional[bytes] = None) -> bool:
        """Validate CryptAPI webhook with RSA SHA256 signature verification."""
        try:
            # Skip signature verification if disabled
            if not self.config.verify_signatures:
                logger.warning("CryptAPI signature verification is disabled - using basic validation only")
                return self._basic_webhook_validation(payload)
            
            # Check for signature header
            if not headers or 'x-ca-signature' not in headers:
                logger.error("Missing x-ca-signature header in CryptAPI webhook")
                return False
            
            signature_b64 = headers['x-ca-signature']
            if not signature_b64:
                logger.error("Empty x-ca-signature header")
                return False
            
            # Verify the signature
            if not self._verify_cryptapi_signature(payload, signature_b64, raw_body):
                logger.error("CryptAPI webhook signature verification failed")
                return False
            
            # Signature verified - do basic validation
            return self._basic_webhook_validation(payload)
            
        except Exception as e:
            logger.error(f"CryptAPI webhook validation error: {e}")
            return False
    
    def _basic_webhook_validation(self, payload: dict) -> bool:
        """Basic webhook payload validation."""
        # Core required fields (UUID is optional for compatibility)
        required_fields = ['address_in', 'address_out', 'txid_in', 'coin']
        
        for field in required_fields:
            if field not in payload:
                logger.warning(f"Missing required field in CryptAPI webhook: {field}")
                return False
        
        # Validate coin format if present
        if 'coin' in payload and not payload['coin']:
            logger.warning("Empty coin field in CryptAPI webhook")
            return False
        
        return True
    
    def _verify_cryptapi_signature(self, payload: dict, signature_b64: str, raw_body: Optional[bytes] = None) -> bool:
        """Verify CryptAPI RSA SHA256 signature according to documentation."""
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                self.config.public_key.encode('utf-8'),
                backend=default_backend()
            )
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Determine what data to verify
            if raw_body:
                # For POST requests - verify raw body
                data_to_verify = raw_body
            else:
                # For GET requests - construct URL from payload
                # This is a fallback if raw_body is not provided
                params = "&".join([f"{k}={v}" for k, v in payload.items()])
                data_to_verify = params.encode('utf-8')
            
            # Verify signature using RSA SHA256
            public_key.verify(
                signature,
                data_to_verify,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"CryptAPI signature verification error: {e}")
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
