"""
NowPayments provider implementation.

Enhanced crypto payment provider with minimal typing.
"""

import requests
import hashlib
import hmac
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from ..base import PaymentProvider
from ...internal_types import ProviderResponse, WebhookData, PaymentAmountEstimate, UniversalCurrency, UniversalCurrenciesResponse
from .models import NowPaymentsConfig
from django_cfg.modules.django_logger import get_logger

logger = get_logger("nowpayments")


class NowPaymentsProvider(PaymentProvider):
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
    
    def __init__(self, config: NowPaymentsConfig):
        """Initialize NowPayments provider."""
        super().__init__(config)
        self.config = config
        self.api_key = config.api_key
        # TEMP: Disable sandbox since sandbox registration site is down
        # self.sandbox = config.sandbox
        self.sandbox = False  # Force production URL
        self.ipn_secret = config.ipn_secret or ''
        self.base_url = self._get_base_url()
        
        # Configurable URLs 
        self.callback_url = config.callback_url
        self.success_url = config.success_url
        self.cancel_url = config.cancel_url
        
        self.headers = {
            'x-api-key': self.api_key.get_secret_value() if hasattr(self.api_key, 'get_secret_value') else str(self.api_key),
            'Content-Type': 'application/json'
        }
    
    def _get_dynamic_callback_url(self) -> Optional[str]:
        """Get dynamic callback URL with ngrok support."""
        try:
            from api.config import config
            
            # Try ngrok first (development)
            ngrok_url = getattr(config, 'get_ngrok_url', lambda x: None)('/cfg/admin/django_cfg_payments/webhooks/nowpayments/')
            if ngrok_url:
                logger.info(f"Using ngrok webhook URL: {ngrok_url}")
                return ngrok_url
            
            # Fallback to configured callback URL
            if self.callback_url:
                logger.info(f"Using configured webhook URL: {self.callback_url}")
                return self.callback_url
            
            # Fallback to site URL
            site_webhook = f"{config.site_url}/cfg/admin/django_cfg_payments/webhooks/nowpayments/"
            logger.info(f"Using site webhook URL: {site_webhook}")
            return site_webhook
            
        except Exception as e:
            logger.warning(f"Failed to get dynamic callback URL: {e}")
            return self.callback_url
    
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
            
            # Get dynamic callback URL with ngrok support
            dynamic_callback_url = self._get_dynamic_callback_url()
            if dynamic_callback_url:
                payment_request['ipn_callback_url'] = dynamic_callback_url
            
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
                provider_status = response.get('payment_status', 'unknown')
                universal_status = self.STATUS_MAPPING.get(provider_status, 'unknown')
                
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
            provider_status = payload.get('payment_status', 'unknown')
            universal_status = self.STATUS_MAPPING.get(provider_status, 'unknown')
            
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
    
    
    def get_parsed_currencies(self) -> UniversalCurrenciesResponse:
        """Get parsed and normalized currencies from NowPayments."""
        try:
            # Use full-currencies endpoint to get detailed currency info
            response = self._make_request('GET', 'full-currencies')
            
            if not response or 'currencies' not in response:
                return UniversalCurrenciesResponse(currencies=[])
            
            universal_currencies = []
            
            for currency_data in response['currencies']:
                if not currency_data.get('enable', True):
                    continue  # Skip disabled currencies
                
                provider_code = currency_data.get('code', '').upper()
                if not provider_code:
                    continue
                
                # Parse provider code into base currency + network using API data
                currency_name = currency_data.get('name', '')
                api_network = currency_data.get('network')
                ticker = currency_data.get('ticker', '')
                base_currency_code, network_code = self._parse_currency_code(provider_code, currency_name, api_network, ticker)
                
                # Determine currency type
                currency_type = 'fiat' if network_code is None else 'crypto'
                
                universal_currency = UniversalCurrency(
                    provider_currency_code=provider_code,
                    base_currency_code=base_currency_code,
                    network_code=network_code,
                    name=currency_data.get('name', base_currency_code),
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
    
    def _parse_currency_code(self, provider_code: str, currency_name: str, network_code: Optional[str] = None, ticker: str = '') -> tuple[str, Optional[str]]:
        """
        Smart parsing using API data, prioritizing ticker field.
        
        Uses ticker as primary source for base currency, then falls back to name parsing.
        
        Examples:
        - "1INCHBSC", "1Inch Network (BSC)", "bsc", "1inch" → ("1INCH", "bsc") 
        - "USDTERC20", "Tether USD (ERC-20)", "eth", "usdt" → ("USDT", "eth") 
        - "BTC", "Bitcoin", "btc", "btc" → ("BTC", "btc")
        """
        # Priority 1: Use ticker if available and meaningful
        if ticker and len(ticker.strip()) > 0:
            base_currency = ticker.upper().strip()
            return base_currency, network_code
        
        # Priority 2: Extract from name using patterns
        base_currency = self._extract_base_currency_from_name(currency_name, provider_code)
        return base_currency, network_code
    
    def _extract_base_currency_from_name(self, currency_name: str, fallback_code: str) -> str:
        """Extract base currency from human-readable name using real API patterns."""
        if not currency_name:
            return fallback_code
        
        name_lower = currency_name.lower()
        
        # Precise patterns from real NowPayments API data
        precise_patterns = {
            # Stablecoins - most common
            'tether usd': 'USDT',
            'tether (': 'USDT',          # "Tether (Arbitrum One)"
            'usd coin': 'USDC',          # "USD Coin (Ethereum)"
            'usd coin bridged': 'USDC',  # "USD Coin Bridged (Polygon)"
            'trueusd': 'TUSD',           # "TrueUSD (Tron)"
            
            # Major cryptocurrencies  
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'cardano': 'ADA',
            'dogecoin': 'DOGE',
            'litecoin': 'LTC',
            
            # Exchange tokens
            'binance coin': 'BNB',
            'bnb': 'BNB',
            
            # Layer 1/2 tokens
            'polygon': 'MATIC',
            'avalanche': 'AVAX',
            'solana': 'SOL',
            'chainlink': 'LINK',
            
            # Other stablecoins
            'dai stablecoin': 'DAI',
            'frax': 'FRAX'
        }
        
        # Check precise patterns first (most reliable)
        for pattern, base in precise_patterns.items():
            if pattern in name_lower:
                return base
        
        # Fallback patterns for edge cases
        fallback_patterns = {
            'usdt': 'USDT',
            'usdc': 'USDC', 
            'tusd': 'TUSD',
            'btc': 'BTC',
            'eth ': 'ETH',
            'ada': 'ADA',
            'doge': 'DOGE',
            'matic': 'MATIC'
        }
        
        for pattern, base in fallback_patterns.items():
            if pattern in name_lower:
                return base
        
        # Last resort: use the provider code as-is
        return fallback_code
    
    
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
