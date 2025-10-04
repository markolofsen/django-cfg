"""
Data conversion utilities.

Converts between Django models and Pydantic data models.
"""

from typing import TYPE_CHECKING
from ...types import PaymentData

if TYPE_CHECKING:
    from ....models import UniversalPayment


class DataConverter:
    """Convert between data formats."""

    @staticmethod
    def payment_to_data(payment: 'UniversalPayment') -> PaymentData:
        """
        Convert Django UniversalPayment to PaymentData.

        Args:
            payment: UniversalPayment model instance

        Returns:
            PaymentData: Pydantic model with payment data
        """
        return PaymentData(
            id=str(payment.id),
            user_id=payment.user_id,
            amount_usd=float(payment.amount_usd),
            crypto_amount=payment.pay_amount,
            currency_code=payment.currency.code,
            provider=payment.provider,
            status=payment.status,
            provider_payment_id=payment.provider_payment_id,
            payment_url=payment.payment_url,
            qr_code_url=getattr(payment, 'qr_code_url', None),
            wallet_address=payment.pay_address,
            callback_url=payment.callback_url,
            cancel_url=payment.cancel_url,
            description=payment.description,
            metadata={},
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            expires_at=payment.expires_at,
            completed_at=getattr(payment, 'completed_at', None)
        )
