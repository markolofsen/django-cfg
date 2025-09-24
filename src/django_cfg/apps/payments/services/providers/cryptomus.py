"""
Cryptomus payment provider implementation.
"""

import logging
import hashlib
import json
import base64
from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass

import requests
from pydantic import BaseModel, Field, validator

from .base import PaymentProvider, ProviderResponse, ProviderConfig

logger = logging.getLogger(__name__)


class CryptomusConfig(ProviderConfig):
    """Configuration for Cryptomus provider."""
    
    merchant_id: str = Field(..., description="Cryptomus merchant ID")
    api_key: str = Field(..., description="Cryptomus API key")
    test_mode: bool = Field(default=False, description="Enable test mode")
    callback_url: Optional[str] = Field(None, description="Default callback URL")
    
    @validator('merchant_id')
    def validate_merchant_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Merchant ID is required")
        return v.strip()
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError("API key must be at least 10 characters")
        return v


class CryptomusProvider(PaymentProvider):
    """Cryptomus payment provider with universal field mapping."""
    
    def __init__(self, config: CryptomusConfig):
        super().__init__(config)
        self.merchant_id = config.merchant_id
        self.api_key = config.api_key
        self.test_mode = config.test_mode
        self.base_url = "https://api.cryptomus.com/v1" if not config.test_mode else "https://api.cryptomus.com/v1"
        
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
                "url_success": payment_data.get('success_url'),
                "is_payment_multiple": False,
                "lifetime": 3600,  # 1 hour
                "to_currency": payment_data.get('crypto_currency', 'BTC')
            }
            
            # Generate signature
            headers = self._generate_headers(payload)
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/payment",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('state') == 0:  # Success
                    payment_info = result.get('result', {})
                    
                    return ProviderResponse(
                        success=True,
                        transaction_id=payment_info.get('uuid'),
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
                    error_msg = result.get('message', 'Unknown Cryptomus error')
                    return ProviderResponse(
                        success=False,
                        error_message=f"Cryptomus API error: {error_msg}"
                    )
            else:
                return ProviderResponse(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
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
                        request_headers: Dict[str, str], raw_body: bytes) -> tuple[bool, Optional[str]]:
        """
        Validate Cryptomus webhook signature and required fields.
        """
        try:
            # Check required fields
            required_fields = ['uuid', 'order_id', 'amount', 'currency', 'status']
            for field in required_fields:
                if field not in webhook_data:
                    return False, f"Missing required field: {field}"
            
            # Validate signature if provided
            sign = request_headers.get('sign') or webhook_data.get('sign')
            if sign:
                # Generate expected signature
                expected_sign = self._generate_webhook_signature(webhook_data)
                if sign != expected_sign:
                    return False, "Invalid webhook signature"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Cryptomus webhook validation failed: {e}")
            return False, f"Validation error: {str(e)}"
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> ProviderResponse:
        """
        Process Cryptomus webhook and map to universal fields.
        """
        try:
            # Map Cryptomus webhook fields to universal fields
            universal_data = {
                'provider_payment_id': webhook_data.get('uuid'),
                'status': self._map_status(webhook_data.get('status')),
                'transaction_hash': webhook_data.get('txid'),
                'sender_address': webhook_data.get('from'),
                'receiver_address': webhook_data.get('to'), 
                'crypto_amount': float(webhook_data.get('amount', 0)),
                'confirmations_count': int(webhook_data.get('confirmations', 0)),
                
                # Additional Cryptomus data
                'cryptomus_network': webhook_data.get('network'),
                'cryptomus_currency': webhook_data.get('currency'),
                'cryptomus_commission': webhook_data.get('commission'),
                'updated_at': webhook_data.get('updated_at')
            }
            
            return ProviderResponse(
                success=True,
                data=universal_data
            )
            
        except Exception as e:
            logger.error(f"Cryptomus webhook processing failed: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Webhook processing error: {str(e)}"
            )
    
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
        """Generate required headers for Cryptomus API."""
        data_string = base64.b64encode(json.dumps(payload).encode()).decode()
        sign = hashlib.md5(f"{data_string}{self.api_key}".encode()).hexdigest()
        
        return {
            "merchant": self.merchant_id,
            "sign": sign,
            "Content-Type": "application/json"
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
            headers = self._generate_headers({})
            
            response = requests.post(
                f"{self.base_url}/exchange-rate/list",
                json={},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('state') == 0:
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
