"""
Currency conversion.

Converts between USD and cryptocurrencies using exchange rates.
"""

from decimal import Decimal
from django_cfg.modules.django_currency import convert_currency, get_exchange_rate
from ...types import ServiceOperationResult


class CurrencyConverter:
    """Convert between currencies."""

    def __init__(self, base_service):
        """
        Initialize converter.

        Args:
            base_service: Base service instance for error/success result creation
        """
        self.base_service = base_service

    def convert_usd_to_crypto(
        self,
        amount_usd: float,
        currency_code: str
    ) -> ServiceOperationResult:
        """
        Convert USD amount to cryptocurrency.

        Args:
            amount_usd: Amount in USD
            currency_code: Target cryptocurrency code

        Returns:
            ServiceOperationResult with conversion data or error
        """
        try:
            # Use django_currency module for conversion
            crypto_amount = convert_currency(amount_usd, 'USD', currency_code)

            return self.base_service._create_success_result(
                "Currency converted successfully",
                {
                    'amount_usd': amount_usd,
                    'crypto_amount': Decimal(str(crypto_amount)),
                    'currency_code': currency_code,
                    'exchange_rate': get_exchange_rate('USD', currency_code)
                }
            )

        except Exception as e:
            return self.base_service._create_error_result(
                f"Currency conversion failed: {e}",
                "conversion_failed"
            )
