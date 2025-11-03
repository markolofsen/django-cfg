"""
NowPayments provider implementation for Payments v2.0.

Simplified provider focused on polling-based flow (no webhooks).
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import httpx
from django.utils import timezone

from ..models import PaymentRequest, ProviderResponse, CurrencyInfo
from .config import NowPaymentsConfig
from .parser import NowPaymentsCurrencyParser

logger = logging.getLogger(__name__)


class NowPaymentsProvider:
    """
    NowPayments cryptocurrency payment provider.

    Simplified v2.0 implementation:
    - No webhooks (polling instead)
    - Httpx for requests
    - Pydantic for validation
    """

    # Map NowPayments status to our internal status
    STATUS_MAPPING = {
        'waiting': 'pending',
        'confirming': 'confirming',
        'confirmed': 'confirmed',
        'sending': 'confirming',
        'partially_paid': 'partially_paid',
        'finished': 'completed',
        'failed': 'failed',
        'refunded': 'refunded',
        'expired': 'expired'
    }

    # Default constants
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_MIN_AMOUNT_USD = 1.0
    DEFAULT_PAYMENT_EXPIRATION_MINUTES = 30

    def __init__(self, config: NowPaymentsConfig):
        """Initialize NowPayments provider."""
        self.config = config
        self.parser = NowPaymentsCurrencyParser()
        self.client = httpx.Client(
            base_url=str(self.config.api_url),
            timeout=getattr(config, 'timeout', self.DEFAULT_TIMEOUT),
            headers={
                'x-api-key': self.config.api_key_str,
                'Content-Type': 'application/json'
            }
        )

        logger.info(
            f"NowPayments provider initialized: "
            f"sandbox={self.config.sandbox}, "
            f"api_url={self.config.api_url}"
        )

    def __del__(self):
        """Close httpx client on cleanup."""
        if hasattr(self, 'client'):
            self.client.close()

    def create_payment(self, request: PaymentRequest) -> ProviderResponse:
        """
        Create payment with NowPayments.

        Args:
            request: Payment request (validated Pydantic model)

        Returns:
            ProviderResponse with payment details or error
        """
        try:
            logger.info(
                f"Creating NowPayments payment: "
                f"amount=${request.amount_usd}, currency={request.currency_code}"
            )

            # Prepare request payload
            payload = {
                'price_amount': float(request.amount_usd),
                'price_currency': 'USD',
                'pay_currency': request.currency_code,
                'order_id': request.order_id,
                'order_description': request.description or f'Payment {request.order_id}',
            }

            # Make API request
            response = self.client.post('payment', json=payload)
            response.raise_for_status()
            data = response.json()

            # Parse response
            if 'payment_id' in data:
                logger.info(f"Payment created: {data['payment_id']}")

                return ProviderResponse(
                    success=True,
                    provider_payment_id=data['payment_id'],
                    status=self.STATUS_MAPPING.get(data.get('payment_status', 'waiting'), 'pending'),
                    wallet_address=data.get('pay_address'),
                    amount=Decimal(str(data.get('pay_amount', 0))),
                    currency=request.currency_code,
                    payment_url=data.get('invoice_url') or data.get('pay_url'),
                    expires_at=self._parse_expiry(data.get('expiration_estimate_date')),
                    raw_response=data
                )
            else:
                error_msg = data.get('message', 'Unknown error')
                return ProviderResponse(
                    success=False,
                    error_message=error_msg,
                    raw_response=data
                )

        except httpx.HTTPStatusError as e:
            error_msg = self._extract_error_message(e)
            logger.error(f"NowPayments HTTP error: {error_msg}")

            return ProviderResponse(
                success=False,
                error_message=error_msg,
                error_code=f'http_{e.response.status_code}',
                raw_response={'error': str(e)}
            )

        except httpx.RequestError as e:
            logger.error(f"NowPayments request error: {e}")

            return ProviderResponse(
                success=False,
                error_message=f"Network error: {str(e)}",
                error_code='network_error',
                raw_response={'error': str(e)}
            )

        except Exception as e:
            logger.exception(f"NowPayments unexpected error: {e}")

            return ProviderResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                error_code='unexpected_error',
                raw_response={'error': str(e), 'type': type(e).__name__}
            )

    def get_payment_status(self, provider_payment_id: str) -> ProviderResponse:
        """
        Get payment status from NowPayments (for polling).

        Args:
            provider_payment_id: NowPayments payment ID

        Returns:
            ProviderResponse with current status
        """
        try:
            logger.debug(f"Checking payment status: {provider_payment_id}")

            # Make API request
            response = self.client.get(f'payment/{provider_payment_id}')
            response.raise_for_status()
            data = response.json()

            # Parse response
            if 'payment_status' in data:
                provider_status = data['payment_status']
                internal_status = self.STATUS_MAPPING.get(provider_status, 'pending')

                return ProviderResponse(
                    success=True,
                    provider_payment_id=provider_payment_id,
                    status=internal_status,
                    wallet_address=data.get('pay_address'),
                    amount=Decimal(str(data.get('pay_amount', 0))),
                    actual_amount=Decimal(str(data.get('actually_paid', 0))) if data.get('actually_paid') else None,
                    currency=data.get('pay_currency'),
                    transaction_hash=data.get('outcome_hash'),
                    raw_response=data
                )
            else:
                return ProviderResponse(
                    success=False,
                    error_message='Payment not found',
                    error_code='payment_not_found',
                    raw_response=data
                )

        except httpx.HTTPStatusError as e:
            error_msg = self._extract_error_message(e)
            logger.error(f"NowPayments status check error: {error_msg}")

            return ProviderResponse(
                success=False,
                error_message=error_msg,
                error_code=f'http_{e.response.status_code}',
                raw_response={'error': str(e)}
            )

        except Exception as e:
            logger.exception(f"NowPayments status check failed: {e}")

            return ProviderResponse(
                success=False,
                error_message=f"Status check failed: {str(e)}",
                error_code='status_check_error',
                raw_response={'error': str(e)}
            )

    def get_currencies(self) -> List[CurrencyInfo]:
        """
        Get supported currencies from NowPayments.

        Returns:
            List of CurrencyInfo objects
        """
        try:
            logger.info("Fetching currencies from NowPayments")

            # Use full-currencies endpoint for detailed info
            response = self.client.get('full-currencies')
            response.raise_for_status()
            data = response.json()

            currencies = []

            for currency_data in data.get('currencies', []):
                # Skip disabled currencies
                if not currency_data.get('enable', True):
                    continue

                provider_code = currency_data.get('code', '').upper()
                if not provider_code:
                    continue

                # Parse currency code
                token, network = self.parser.parse_currency_code(
                    provider_code=provider_code,
                    currency_name=currency_data.get('name', ''),
                    network_from_api=currency_data.get('network'),
                    ticker=currency_data.get('ticker', '')
                )

                # Skip if parsing failed
                if not token:
                    continue

                # Generate proper name
                name = self.parser.generate_currency_name(
                    token=token,
                    network=network,
                    original_name=currency_data.get('name', '')
                )

                # Create CurrencyInfo
                currency_info = CurrencyInfo(
                    code=provider_code,
                    name=name,
                    token=token,
                    network=network,
                    is_enabled=currency_data.get('enable', True),
                    is_popular=currency_data.get('is_popular', False),
                    is_stable=currency_data.get('is_stable', False),
                    logo_url=currency_data.get('logo_url'),
                    min_amount_usd=getattr(self.config, 'min_amount_usd', self.DEFAULT_MIN_AMOUNT_USD),
                    priority=currency_data.get('priority', 0)
                )

                currencies.append(currency_info)

            logger.info(f"Fetched {len(currencies)} currencies from NowPayments")
            return currencies

        except Exception as e:
            logger.exception(f"Failed to fetch currencies: {e}")
            return []

    def get_available_currencies(self) -> List[Dict[str, Any]]:
        """
        Get available currencies as simple dict for management commands.

        Returns:
            List of currency dicts with code, name, token, network, etc.
        """
        currencies = self.get_currencies()

        return [
            {
                'code': currency.code,
                'name': currency.name,
                'token': currency.token,
                'network': currency.network,
                'symbol': '',  # NowPayments doesn't provide symbol
                'min_amount': float(currency.min_amount_usd),
            }
            for currency in currencies
        ]

    def _parse_expiry(self, expiry_str: Optional[str]) -> Optional[datetime]:
        """Parse expiry time from NowPayments."""
        expiration_minutes = getattr(self.config, 'payment_expiration_minutes', self.DEFAULT_PAYMENT_EXPIRATION_MINUTES)

        if not expiry_str:
            # Default to 30 minutes from now
            return timezone.now() + timedelta(minutes=expiration_minutes)

        try:
            # Parse ISO format
            return datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        except Exception:
            logger.warning(f"Failed to parse expiry time: {expiry_str}")
            return timezone.now() + timedelta(minutes=expiration_minutes)

    def _extract_error_message(self, error: httpx.HTTPStatusError) -> str:
        """Extract user-friendly error message from HTTP error."""
        try:
            data = error.response.json()
            return data.get('message', str(error))
        except Exception:
            return str(error)

    def health_check(self) -> bool:
        """
        Check if NowPayments API is accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self.client.get('status')
            response.raise_for_status()
            data = response.json()
            return data.get('message', '').upper() == 'OK'
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
