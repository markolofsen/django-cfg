"""
Cryptomus payment provider implementation.
"""

from django_cfg.modules.django_logger import get_logger
import hashlib
import json
import base64
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import requests
from ..base import PaymentProvider
from ...internal_types import ProviderResponse, PaymentAmountEstimate, WebhookData
from .models import CryptomusConfig

logger = get_logger("cryptomus_old")


class CryptomusProvider(PaymentProvider):
    """Cryptomus payment provider with universal field mapping."""
    
    def __init__(self, config: CryptomusConfig):
        super().__init__(config)
        self.config = config
        self.merchant_id = config.merchant_id
        self.api_key = config.api_key
        self.test_mode = config.test_mode
        self.base_url = self._get_base_url()
    
    def _get_base_url(self) -> str:
        """Get base URL for API requests."""
        if self.config.test_mode:
            return "https://api.cryptomus.com/v1/test"  # Test mode URL for identification
        return "https://api.cryptomus.com/v1"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> Optional[dict]:
        """Make HTTP request to Cryptomus API with error handling."""
        try:
            url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
            
            # Generate headers with signature for POST requests
            headers = self._generate_headers(data or {})
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Cryptomus API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Cryptomus request: {e}")
            return None
        
    def check_payment_status(self, payment_id: str) -> ProviderResponse:
        """Check payment status via Cryptomus API."""
        try:
            endpoint = f"payment/{payment_id}"
            response = self._make_request('POST', endpoint, {})
            
            if response and 'state' in response and response['state'] == 0:
                result = response.get('result', {})
                return ProviderResponse(
                    success=True,
                    provider_payment_id=result.get('uuid', payment_id),
                    status=result.get('status', 'pending'),
                    pay_address=result.get('address'),
                    amount=Decimal(str(result.get('amount', 0))),
                    currency=result.get('currency', 'unknown'),
                    data=result
                )
            else:
                return ProviderResponse(
                    success=False,
                    error_message=response.get('message', 'Failed to check payment status')
                )
                
        except Exception as e:
            logger.error(f"Cryptomus check_payment_status error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e)
            )

    def create_payment(self, payment_data: dict) -> ProviderResponse:
        """
        Create payment using Cryptomus API.
        Maps to universal payment fields.
        """
        try:
            # Extract required data
            order_id = payment_data.get('order_id')
            amount = payment_data.get('amount')
            currency = payment_data.get('currency', 'USD')
            callback_url = payment_data.get('callback_url', self.config.callback_url)
            
            if not all([order_id, amount]):
                return ProviderResponse(
                    success=False,
                    error_message="Missing required fields: order_id, amount"
                )
            
            # Prepare Cryptomus API request
            payload = {
                "amount": str(amount),
                "currency": currency,
                "order_id": order_id,
                "url_callback": callback_url,
                "url_return": payment_data.get('return_url'),
                "url_success": payment_data.get('success_url', self.config.success_url),
                "url_cancel": payment_data.get('cancel_url', self.config.cancel_url),
                "is_payment_multiple": False,
                "lifetime": 3600,  # 1 hour
                "to_currency": payment_data.get('crypto_currency', 'BTC')
            }
            
            # Make API request using centralized method
            result = self._make_request('POST', 'payment', payload)
            
            if result and result.get('state') == 0:  # Success
                payment_info = result.get('result', {})
                
                return ProviderResponse(
                    success=True,
                    provider_payment_id=payment_info.get('uuid'),
                    data={
                        # Universal field mapping
                        'provider_payment_id': payment_info.get('uuid'),
                        'receiver_address': payment_info.get('address'),
                        'crypto_amount': float(payment_info.get('amount', 0)),
                        'provider_callback_url': callback_url,
                        'payment_url': payment_info.get('url'),
                        'qr_code': payment_info.get('static_qr'),
                        
                        # Cryptomus specific fields
                        'cryptomus_order_id': payment_info.get('order_id'),
                        'cryptomus_currency': payment_info.get('currency'),
                        'cryptomus_network': payment_info.get('network'),
                        'cryptomus_status': payment_info.get('status'),
                        'expires_at': payment_info.get('expired_at')
                    }
                )
            else:
                error_msg = result.get('message', 'Unknown Cryptomus error') if result else 'No response from API'
                return ProviderResponse(
                    success=False,
                    error_message=f"Cryptomus API error: {error_msg}"
                )
                
        except requests.RequestException as e:
            logger.error(f"Cryptomus API request failed: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Cryptomus payment creation failed: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def validate_webhook(self, webhook_data: Dict[str, Any], 
                        request_headers: Optional[Dict[str, str]] = None, 
                        raw_body: Optional[bytes] = None) -> bool:
        """
        Validate Cryptomus webhook with strict requirements.
        """
        try:
            # Strict required field validation
            required_fields = ['uuid', 'order_id', 'amount', 'currency', 'status']
            for field in required_fields:
                if field not in webhook_data or not webhook_data[field]:
                    logger.warning(f"Missing or empty required field: {field}")
                    return False
            
            # Validate signature (required for security)
            sign = None
            if request_headers:
                sign = request_headers.get('sign')
            if not sign:
                sign = webhook_data.get('sign')
            
            if not sign:
                logger.error("No signature found in Cryptomus webhook")
                return False  # Require signature for security
                
            # Verify signature
            data_for_sign = {k: v for k, v in webhook_data.items() if k != 'sign'}
            expected_sign = self._generate_webhook_signature(data_for_sign)
            if sign != expected_sign:
                logger.error("Cryptomus webhook signature validation failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Cryptomus webhook validation failed: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> WebhookData:
        """
        Process Cryptomus webhook and map to universal fields.
        """
        try:
            # Map Cryptomus status to universal status
            status = self._map_status(webhook_data.get('status', 'unknown'))
            
            # Extract payment amount
            amount = webhook_data.get('amount')
            pay_amount = Decimal(str(amount)) if amount else Decimal('0')
            
            # Ensure provider_payment_id is not None
            provider_payment_id = webhook_data.get('uuid') or webhook_data.get('order_id') or 'unknown'
            
            return WebhookData(
                provider_payment_id=provider_payment_id,
                status=status,
                pay_amount=pay_amount,
                pay_currency=webhook_data.get('currency', 'unknown'),
                actually_paid=pay_amount,  # For Cryptomus, same as pay_amount
                order_id=webhook_data.get('order_id'),
                signature=webhook_data.get('txid') or webhook_data.get('sign')  # Use transaction ID or signature
            )
            
        except Exception as e:
            logger.error(f"Cryptomus webhook processing failed: {e}")
            raise
    
    def estimate_payment_amount(self, amount: Decimal, currency_code: str) -> Optional['PaymentAmountEstimate']:
        """Estimate payment amount using Cryptomus exchange rates."""
        try:
            # Cryptomus exchange rate endpoint
            response = self._make_request('POST', 'exchange-rate/list', {
                'currency_from': 'USD',
                'currency_to': currency_code.upper(),
                'amount': float(amount)
            })
            
            if response and response.get('state') == 0:
                result = response.get('result', {})
                if result:
                    return PaymentAmountEstimate(
                        currency_from='usd',
                        currency_to=currency_code.lower(),
                        amount_from=amount,
                        estimated_amount=Decimal(str(result.get('amount', 0))),
                        exchange_rate=Decimal(str(result.get('course', 1))),
                        provider_name=self.name,
                        estimated_at=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Cryptomus estimate_payment_amount error: {e}")
            return None
    
    def get_payment_status(self, payment_id: str) -> ProviderResponse:
        """Get payment status from Cryptomus."""
        try:
            payload = {"uuid": payment_id}
            headers = self._generate_headers(payload)
            
            response = requests.post(
                f"{self.base_url}/payment/info",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('state') == 0:
                    payment_info = result.get('result', {})
                    
                    return ProviderResponse(
                        success=True,
                        data={
                            'status': self._map_status(payment_info.get('status')),
                            'provider_payment_id': payment_info.get('uuid'),
                            'transaction_hash': payment_info.get('txid'),
                            'crypto_amount': float(payment_info.get('amount', 0)),
                            'confirmations_count': int(payment_info.get('confirmations', 0))
                        }
                    )
            
            return ProviderResponse(
                success=False,
                error_message="Failed to get payment status"
            )
            
        except Exception as e:
            logger.error(f"Cryptomus status check failed: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Status check error: {str(e)}"
            )
    
    def _generate_headers(self, payload: dict) -> dict:
        """Generate authentication headers for Cryptomus API."""
        # Convert data to JSON string with sorted keys for consistency
        data_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        # Create signature: md5(base64(data) + api_key)
        data_b64 = base64.b64encode(data_json.encode('utf-8')).decode('utf-8')
        signature_string = data_b64 + self.config.api_key
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        
        return {
            'Content-Type': 'application/json',
            'merchant': self.config.merchant_id,  # CRITICAL: merchant header
            'sign': signature
        }
    
    def _generate_webhook_signature(self, webhook_data: dict) -> str:
        """Generate expected webhook signature for validation."""
        # Cryptomus webhook signature generation
        data_string = base64.b64encode(json.dumps(webhook_data, sort_keys=True).encode()).decode()
        return hashlib.md5(f"{data_string}{self.api_key}".encode()).hexdigest()
    
    def _map_status(self, cryptomus_status: str) -> str:
        """Map Cryptomus status to universal status."""
        status_mapping = {
            'check': 'pending',
            'process': 'pending', 
            'confirm_check': 'pending',
            'paid': 'completed',  # Add missing 'paid' status
            'confirmed': 'completed',
            'fail': 'failed',
            'cancel': 'cancelled',
            'system_fail': 'failed',
            'refund_process': 'refunding',
            'refund_fail': 'failed',
            'refund_paid': 'refunded'
        }
        return status_mapping.get(cryptomus_status, 'pending')
    
    def get_supported_currencies(self) -> ProviderResponse:
        """Get supported currencies from Cryptomus."""
        try:
            result = self._make_request('POST', 'exchange-rate/list', {})
            
            if result and result.get('state') == 0:
                currencies = result.get('result', [])
                return ProviderResponse(
                    success=True,
                    data={'currencies': currencies}
                )
            
            return ProviderResponse(
                success=False,
                error_message="Failed to get supported currencies"
            )
            
        except Exception as e:
            logger.error(f"Cryptomus currencies request failed: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Currencies request error: {str(e)}"
            )
    
    def get_supported_networks(self, currency_code: str = None) -> ProviderResponse:
        """Get supported networks from Cryptomus."""
        try:
            headers = self._generate_headers({})
            
            # Cryptomus might have a specific API endpoint for networks
            # For now, we'll extract from currencies data
            currencies_response = self.get_supported_currencies()
            if not currencies_response.success:
                return currencies_response
            
            networks = {}
            currencies = currencies_response.data.get('currencies', [])
            
            for currency in currencies:
                currency_symbol = currency.get('currency_code', '').upper()
                if currency_code and currency_symbol != currency_code.upper():
                    continue
                    
                # Extract network info from currency data
                network_info = {
                    'code': currency.get('network', 'mainnet'),
                    'name': currency.get('network_name', 'Mainnet'),
                    'min_amount': currency.get('min_amount', 0),
                    'max_amount': currency.get('max_amount', 0),
                    'commission_percent': currency.get('commission_percent', 0)
                }
                
                if currency_symbol not in networks:
                    networks[currency_symbol] = []
                networks[currency_symbol].append(network_info)
            
            return ProviderResponse(
                success=True,
                data={'networks': networks}
            )
            
        except Exception as e:
            logger.error(f"Cryptomus networks request failed: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Networks request error: {str(e)}"
            )
    
    def get_currency_network_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of currencies to their supported networks."""
        networks_response = self.get_supported_networks()
        if not networks_response.success:
            return {}
        
        mapping = {}
        networks_data = networks_response.data.get('networks', {})
        
        for currency_code, networks in networks_data.items():
            mapping[currency_code] = [network['code'] for network in networks]
        
        return mapping
