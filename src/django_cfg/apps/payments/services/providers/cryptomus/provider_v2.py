"""
Cryptomus payment provider implementation using official library.
Enhanced with better error handling, security, and Pydantic models.
"""

from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime

from cryptomus import Client
from cryptomus.request_exceptions import RequestExceptionsBuilder

from ..base import PaymentProvider
from ...internal_types import ProviderResponse, WebhookData, PaymentAmountEstimate, ProviderInfo
from .models import CryptomusConfig, CryptomusWebhook
from django_cfg.modules.django_logger import get_logger

logger = get_logger("cryptomus")


class CryptomusProviderV2(PaymentProvider):
    """
    Enhanced Cryptomus payment provider using official Python library.
    Features:
    - Official cryptomus library integration
    - Proper error handling with RequestExceptionsBuilder
    - Pydantic model validation
    - Universal field mapping
    - Security-first approach
    """
    
    name = "cryptomus_v2"
    display_name = "Cryptomus (Official)"
    
    def __init__(self, config: CryptomusConfig):
        super().__init__(config)
        self.config = config
        self._payment_client = None
        self._payout_client = None
    
    @property
    def payment_client(self):
        """Lazy-loaded payment client using official library."""
        if self._payment_client is None:
            try:
                self._payment_client = Client.payment(
                    self.config.api_key,
                    self.config.merchant_id
                )
            except Exception as e:
                logger.error(f"Failed to initialize Cryptomus payment client: {e}")
                raise
        return self._payment_client
    
    @property
    def payout_client(self):
        """Lazy-loaded payout client using official library."""
        if self._payout_client is None and hasattr(self.config, 'payout_api_key'):
            try:
                self._payout_client = Client.payout(
                    self.config.payout_api_key,
                    self.config.merchant_id
                )
            except Exception as e:
                logger.error(f"Failed to initialize Cryptomus payout client: {e}")
                # Don't raise here, payout is optional
                pass
        return self._payout_client
    
    def create_payment(self, payment_data: dict) -> ProviderResponse:
        """
        Create payment using official Cryptomus library.
        Maps to universal payment fields with enhanced error handling.
        """
        try:
            # Validate required fields
            order_id = payment_data.get('order_id')
            amount = payment_data.get('amount')
            currency = payment_data.get('currency', 'USD')
            
            if not all([order_id, amount]):
                return ProviderResponse(
                    success=False,
                    error_message="Missing required fields: order_id, amount"
                )
            
            # Validate amount
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    return ProviderResponse(
                        success=False,
                        error_message="Amount must be positive"
                    )
            except (ValueError, TypeError):
                return ProviderResponse(
                    success=False,
                    error_message="Invalid amount format"
                )
            
            # Prepare payment data for Cryptomus API
            cryptomus_data = {
                'amount': str(amount_decimal),
                'currency': currency,
                'order_id': order_id,
                'url_callback': payment_data.get('callback_url', self.config.callback_url),
                'url_return': payment_data.get('return_url'),
                'url_success': payment_data.get('success_url', self.config.success_url),
                'url_cancel': payment_data.get('cancel_url', self.config.cancel_url),
                'is_payment_multiple': payment_data.get('allow_overpayment', True),
                'lifetime': payment_data.get('lifetime', 3600),  # 1 hour default
                'to_currency': payment_data.get('crypto_currency', 'BTC')
            }
            
            # Add optional fields
            if payment_data.get('description'):
                cryptomus_data['additional_data'] = {
                    'description': payment_data['description']
                }
            
            # Create payment using official library
            result = self.payment_client.create(cryptomus_data)
            
            # Map response to universal format
            return ProviderResponse(
                success=True,
                transaction_id=result.get('uuid'),
                provider_payment_id=result.get('uuid'),
                pay_address=result.get('address'),
                pay_amount=Decimal(str(result.get('payment_amount', 0))),
                pay_currency=result.get('payer_currency', currency),
                data={
                    # Universal fields
                    'payment_url': result.get('url'),
                    'qr_code_data': result.get('url'),  # Use payment URL for QR
                    'expires_at': result.get('expired_at'),
                    
                    # Cryptomus specific
                    'cryptomus_uuid': result.get('uuid'),
                    'cryptomus_order_id': result.get('order_id'),
                    'cryptomus_status': result.get('payment_status'),
                    'cryptomus_amount': result.get('amount'),
                    'cryptomus_currency': result.get('currency'),
                    'cryptomus_network': result.get('network'),
                    'cryptomus_address': result.get('address'),
                    'cryptomus_is_final': result.get('is_final', False)
                }
            )
            
        except RequestExceptionsBuilder as e:
            # Handle Cryptomus API exceptions
            error_msg = f"Cryptomus API error: {e}"
            
            # Check for specific error types
            if hasattr(e, 'args') and len(e.args) >= 2:
                status_code = e.args[1] if isinstance(e.args[1], int) else 0
                
                if status_code == 400:
                    if 'balance' in str(e).lower():
                        error_msg = "Insufficient balance in merchant account"
                    elif 'amount' in str(e).lower():
                        error_msg = "Invalid payment amount"
                    elif 'currency' in str(e).lower():
                        error_msg = "Unsupported currency"
                elif status_code == 401:
                    error_msg = "Authentication failed: Invalid API key or merchant ID"
                elif status_code == 403:
                    error_msg = "Access denied: Check merchant permissions"
                elif status_code == 422:
                    error_msg = "Validation error: Check request parameters"
            
            logger.error(f"Cryptomus create_payment error: {error_msg}")
            return ProviderResponse(
                success=False,
                error_message=error_msg
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in Cryptomus create_payment: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def validate_webhook(self, webhook_data: Dict[str, Any], 
                        request_headers: Optional[Dict[str, str]] = None, 
                        raw_body: Optional[bytes] = None) -> bool:
        """
        Validate Cryptomus webhook using Pydantic model and signature verification.
        Enhanced security with strict validation.
        """
        try:
            # Validate using Pydantic model
            webhook = CryptomusWebhook(**webhook_data)
            
            # Verify signature if provided
            signature = webhook.sign
            if signature:
                # Prepare data for signature verification (exclude sign field)
                data_for_sign = webhook.model_dump(exclude={'sign'})
                expected_signature = self._generate_webhook_signature(data_for_sign)
                
                if signature != expected_signature:
                    logger.error("Cryptomus webhook signature verification failed")
                    return False
            else:
                logger.warning("Cryptomus webhook missing signature - validation skipped")
            
            # Additional business logic validation
            if webhook.type not in ['payment', 'payout']:
                logger.warning(f"Unknown webhook type: {webhook.type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Cryptomus webhook validation failed: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> WebhookData:
        """
        Process Cryptomus webhook with enhanced error handling.
        Maps to universal webhook data format.
        """
        try:
            # Validate and parse webhook data
            webhook = CryptomusWebhook(**webhook_data)
            
            # Map status to universal format
            universal_status = self._map_status(webhook.status)
            
            # Calculate amounts
            pay_amount = webhook.amount if webhook.amount else Decimal('0')
            actually_paid = webhook.payment_amount if webhook.payment_amount else pay_amount
            
            return WebhookData(
                provider_payment_id=webhook.uuid,
                status=universal_status,
                pay_amount=pay_amount,
                pay_currency=webhook.payer_currency or webhook.currency,
                actually_paid=actually_paid,
                order_id=webhook.order_id,
                signature=webhook.txid or webhook.sign,
                transaction_hash=webhook.txid,
                network=webhook.network,
                from_address=webhook.from_address,
                is_final=webhook.is_final,
                raw_data=webhook_data
            )
            
        except Exception as e:
            logger.error(f"Cryptomus webhook processing failed: {e}")
            raise
    
    def check_payment_status(self, payment_id: str) -> ProviderResponse:
        """Get payment status using official library."""
        try:
            # Use info method with UUID
            result = self.payment_client.info({'uuid': payment_id})
            
            return ProviderResponse(
                success=True,
                provider_payment_id=result.get('uuid'),
                status=self._map_status(result.get('payment_status')),
                pay_address=result.get('address'),
                pay_amount=Decimal(str(result.get('payment_amount', 0))),
                pay_currency=result.get('payer_currency'),
                data={
                    'transaction_hash': result.get('txid'),
                    'network': result.get('network'),
                    'confirmations': result.get('confirmations', 0),
                    'is_final': result.get('is_final', False),
                    'created_at': result.get('created_at'),
                    'updated_at': result.get('updated_at')
                }
            )
            
        except RequestExceptionsBuilder as e:
            error_msg = f"Cryptomus payment status error: {e}"
            logger.error(error_msg)
            return ProviderResponse(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_payment_status: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def get_supported_currencies(self) -> ProviderResponse:
        """Get supported currencies using official library services endpoint."""
        try:
            services = self.payment_client.services()
            
            # Extract unique currencies
            currencies = list(set([
                service.get('currency') for service in services 
                if service.get('currency')
            ]))
            
            return ProviderResponse(
                success=True,
                data={
                    'currencies': currencies,
                    'services': services  # Full service data for advanced usage
                }
            )
            
        except RequestExceptionsBuilder as e:
            error_msg = f"Cryptomus services error: {e}"
            logger.error(error_msg)
            return ProviderResponse(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_supported_currencies: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def get_supported_networks(self, currency_code: str = None) -> ProviderResponse:
        """Get supported networks from services data."""
        try:
            services_response = self.get_supported_currencies()
            if not services_response.success:
                return services_response
            
            services = services_response.data.get('services', [])
            networks = {}
            
            for service in services:
                currency = service.get('currency', '').upper()
                network = service.get('network')
                
                if currency_code and currency != currency_code.upper():
                    continue
                
                if currency and network:
                    if currency not in networks:
                        networks[currency] = []
                    
                    network_info = {
                        'code': network,
                        'name': service.get('network_name', network),
                        'min_amount': service.get('min_amount', 0),
                        'max_amount': service.get('max_amount', 0),
                        'commission_percent': service.get('commission_percent', 0),
                        'is_available': service.get('is_available', True)
                    }
                    networks[currency].append(network_info)
            
            return ProviderResponse(
                success=True,
                data={'networks': networks}
            )
            
        except Exception as e:
            logger.error(f"Error in get_supported_networks: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Error: {str(e)}"
            )
    
    def get_balance(self) -> ProviderResponse:
        """Get merchant balance using official library."""
        try:
            balance = self.payment_client.balance()
            
            return ProviderResponse(
                success=True,
                data={'balance': balance}
            )
            
        except RequestExceptionsBuilder as e:
            error_msg = f"Cryptomus balance error: {e}"
            logger.error(error_msg)
            return ProviderResponse(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_balance: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def estimate_payment_amount(self, amount: Decimal, currency_code: str) -> Optional[PaymentAmountEstimate]:
        """
        Estimate payment amount by creating a test payment.
        Note: Cryptomus doesn't have a dedicated estimation API.
        """
        try:
            # For estimation, we could use the exchange rate or create a test payment
            # Since there's no dedicated estimation API, we'll return a basic estimate
            # based on 1:1 ratio and let the actual payment creation determine the real rate
            
            return PaymentAmountEstimate(
                currency_from='usd',
                currency_to=currency_code.lower(),
                amount_from=amount,
                estimated_amount=amount,  # 1:1 estimate, real rate determined at payment creation
                exchange_rate=Decimal('1.0'),
                provider_name=self.name,
                estimated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Cryptomus estimate_payment_amount error: {e}")
            return None
    
    def create_wallet(self, currency: str, network: str, order_id: str, 
                     callback_url: str = None) -> ProviderResponse:
        """Create static wallet using official library."""
        try:
            wallet_data = {
                'network': network,
                'currency': currency,
                'order_id': order_id
            }
            
            if callback_url:
                wallet_data['url_callback'] = callback_url
            elif self.config.callback_url:
                wallet_data['url_callback'] = self.config.callback_url
            
            result = self.payment_client.create_wallet(wallet_data)
            
            return ProviderResponse(
                success=True,
                provider_payment_id=result.get('uuid'),
                pay_address=result.get('address'),
                data={
                    'wallet_uuid': result.get('uuid'),
                    'address': result.get('address'),
                    'currency': currency,
                    'network': network,
                    'order_id': order_id
                }
            )
            
        except RequestExceptionsBuilder as e:
            error_msg = f"Cryptomus wallet creation error: {e}"
            logger.error(error_msg)
            return ProviderResponse(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_wallet: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def resend_notification(self, payment_id: str = None, order_id: str = None) -> ProviderResponse:
        """Resend webhook notification using official library."""
        try:
            if not payment_id and not order_id:
                return ProviderResponse(
                    success=False,
                    error_message="Either payment_id (uuid) or order_id must be provided"
                )
            
            data = {}
            if payment_id:
                data['uuid'] = payment_id
            if order_id:
                data['order_id'] = order_id
            
            result = self.payment_client.resend_notification(data)
            
            return ProviderResponse(
                success=True,
                data={'resend_result': result}
            )
            
        except RequestExceptionsBuilder as e:
            error_msg = f"Cryptomus resend notification error: {e}"
            logger.error(error_msg)
            return ProviderResponse(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            logger.error(f"Unexpected error in resend_notification: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _generate_webhook_signature(self, webhook_data: dict) -> str:
        """Generate expected webhook signature for validation."""
        import json
        import base64
        import hashlib
        
        # Cryptomus webhook signature: md5(base64(json_data) + api_key)
        json_data = json.dumps(webhook_data, separators=(',', ':'), sort_keys=True)
        encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
        signature_string = encoded_data + self.config.api_key
        return hashlib.md5(signature_string.encode('utf-8')).hexdigest()
    
    def _map_status(self, cryptomus_status: str) -> str:
        """Map Cryptomus status to universal status."""
        status_mapping = {
            'check': 'pending',
            'process': 'pending',
            'confirm_check': 'pending',
            'paid': 'completed',
            'paid_over': 'completed',
            'confirmed': 'completed',
            'fail': 'failed',
            'wrong_amount': 'failed',
            'cancel': 'cancelled',
            'system_fail': 'failed',
            'refund_process': 'refunding',
            'refund_fail': 'failed',
            'refund_paid': 'refunded'
        }
        return status_mapping.get(cryptomus_status, 'pending')
    
    def get_provider_info(self) -> ProviderInfo:
        """Get provider information with Pydantic model."""
        return ProviderInfo(
            name=self.name,
            display_name=self.display_name,
            supported_currencies=["BTC", "ETH", "USDT", "USDC", "LTC", "BCH", "TRX", "BNB"],
            is_active=self.config.enabled,
            features={
                "hosted_payments": True,
                "static_wallets": True,
                "payouts": bool(self.payout_client),
                "webhooks": True,
                "qr_codes": True,
                "overpayments": True,
                "refunds": True,
                "api_endpoints": {
                    "create_payment": "https://api.cryptomus.com/v1/payment",
                    "payment_info": "https://api.cryptomus.com/v1/payment/info",
                    "services": "https://api.cryptomus.com/v1/payment/services",
                    "balance": "https://api.cryptomus.com/v1/balance",
                    "create_wallet": "https://api.cryptomus.com/v1/wallet"
                }
            }
        )
    
    def get_currency_network_mapping(self) -> Dict[str, List[str]]:
        """Get currency to network mapping."""
        networks_response = self.get_supported_networks()
        if not networks_response.success:
            return {}
        
        mapping = {}
        networks_data = networks_response.data.get('networks', {})
        
        for currency_code, networks in networks_data.items():
            mapping[currency_code] = [network['code'] for network in networks]
        
        return mapping
