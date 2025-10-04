"""
Currency validation.

Validates that currencies are active and supported by providers.
"""

from ....models import Currency, ProviderCurrency
from ...types import ServiceOperationResult


class CurrencyValidator:
    """Validate currencies for payment operations."""

    def __init__(self, base_service):
        """
        Initialize validator.

        Args:
            base_service: Base service instance for error/success result creation
        """
        self.base_service = base_service

    def validate_currency(self, currency_code: str) -> ServiceOperationResult:
        """
        Validate currency is supported.

        Checks that:
        1. Currency exists and is active
        2. Currency is supported by at least one provider

        Args:
            currency_code: Currency code to validate (e.g., 'BTC', 'ETH')

        Returns:
            ServiceOperationResult with currency data or error
        """
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)

            # Check if currency is supported by any provider
            provider_currency = ProviderCurrency.objects.filter(
                currency=currency,
                is_enabled=True
            ).first()

            if not provider_currency:
                return self.base_service._create_error_result(
                    f"Currency {currency_code} not supported by any provider",
                    "currency_not_supported"
                )

            return self.base_service._create_success_result(
                "Currency is valid",
                {'currency': currency}  # Wrap in dict for Pydantic
            )

        except Currency.DoesNotExist:
            return self.base_service._create_error_result(
                f"Currency {currency_code} not found",
                "currency_not_found"
            )
