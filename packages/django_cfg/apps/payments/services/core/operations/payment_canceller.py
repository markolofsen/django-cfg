"""
Payment cancellation logic.

Handles payment cancellation with validation.
"""

from typing import TYPE_CHECKING
from ...types import PaymentResult
from ..utils import DataConverter

if TYPE_CHECKING:
    from ....models import UniversalPayment


class PaymentCanceller:
    """Handle payment cancellation."""

    def __init__(self, base_service):
        """
        Initialize canceller.

        Args:
            base_service: Base service for transactions, logging, and result creation
        """
        self.base_service = base_service
        self.logger = base_service.logger

    def cancel_payment(self, payment_id: str, reason: str = None) -> PaymentResult:
        """
        Cancel payment if possible.

        Args:
            payment_id: Payment ID to cancel
            reason: Cancellation reason

        Returns:
            PaymentResult: Cancellation result
        """
        try:
            from ....models import UniversalPayment

            self.logger.info("Cancelling payment", extra={
                'payment_id': payment_id,
                'reason': reason
            })

            # Get payment
            try:
                payment = UniversalPayment.objects.get(id=payment_id)
            except UniversalPayment.DoesNotExist:
                return PaymentResult(
                    success=False,
                    message=f"Payment {payment_id} not found",
                    error_code="payment_not_found"
                )

            # Check if payment can be cancelled
            if not payment.can_be_cancelled():
                return PaymentResult(
                    success=False,
                    message=f"Payment {payment_id} cannot be cancelled (status: {payment.status})",
                    error_code="cannot_cancel"
                )

            # Cancel using manager
            def cancel_payment_transaction():
                return payment.cancel(reason)

            success = self.base_service._execute_with_transaction(cancel_payment_transaction)

            if success:
                payment.refresh_from_db()
                payment_data = DataConverter.payment_to_data(payment)

                self.base_service._log_operation(
                    "cancel_payment",
                    True,
                    payment_id=payment_id,
                    reason=reason
                )

                return PaymentResult(
                    success=True,
                    message="Payment cancelled successfully",
                    payment_id=str(payment.id),
                    status=payment.status,
                    data={'payment': payment_data.model_dump()}
                )
            else:
                return PaymentResult(
                    success=False,
                    message="Failed to cancel payment",
                    error_code="cancel_failed"
                )

        except Exception as e:
            return PaymentResult(**self.base_service._handle_exception(
                "cancel_payment", e,
                payment_id=payment_id
            ).model_dump())
