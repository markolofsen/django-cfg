"""
Payment status checking.

Handles payment status retrieval with optional provider verification.
"""

from typing import TYPE_CHECKING
from ...types import PaymentStatusRequest, PaymentResult
from ..utils import DataConverter

if TYPE_CHECKING:
    from ..providers import ProviderClient


class StatusChecker:
    """Check payment status."""

    def __init__(self, provider_client: 'ProviderClient', base_service):
        """
        Initialize status checker.

        Args:
            provider_client: Provider client for status checks
            base_service: Base service for logging and result creation
        """
        self.provider_client = provider_client
        self.base_service = base_service
        self.logger = base_service.logger

    def get_payment_status(self, request: PaymentStatusRequest) -> PaymentResult:
        """
        Get payment status with optional provider check.

        Args:
            request: Payment status request

        Returns:
            PaymentResult: Current payment status
        """
        try:
            from ....models import UniversalPayment

            # Validate request
            if isinstance(request, dict):
                request = PaymentStatusRequest(**request)

            self.logger.debug("Getting payment status", extra={
                'payment_id': request.payment_id,
                'force_provider_check': request.force_provider_check
            })

            # Get payment
            try:
                payment = UniversalPayment.objects.get(id=request.payment_id)
            except UniversalPayment.DoesNotExist:
                return PaymentResult(
                    success=False,
                    message=f"Payment {request.payment_id} not found",
                    error_code="payment_not_found"
                )

            # Check user authorization if provided
            if request.user_id and payment.user_id != request.user_id:
                return PaymentResult(
                    success=False,
                    message="Access denied to payment",
                    error_code="access_denied"
                )

            # Force provider check if requested
            if request.force_provider_check:
                provider_result = self.provider_client.check_status(payment)
                if provider_result.success and provider_result.data.get('status_changed'):
                    # Reload payment if status was updated
                    payment.refresh_from_db()

            # Convert to PaymentData
            payment_data = DataConverter.payment_to_data(payment)

            return PaymentResult(
                success=True,
                message="Payment status retrieved",
                payment_id=str(payment.id),
                status=payment.status,
                amount_usd=payment.amount_usd,
                crypto_amount=payment.pay_amount,
                currency_code=payment.currency.code,
                provider_payment_id=payment.provider_payment_id,
                payment_url=payment.payment_url,
                qr_code_url=getattr(payment, 'qr_code_url', None),
                wallet_address=payment.pay_address,
                expires_at=payment.expires_at,
                data={'payment': payment_data.model_dump()}
            )

        except Exception as e:
            return PaymentResult(**self.base_service._handle_exception(
                "get_payment_status", e,
                payment_id=request.payment_id if hasattr(request, 'payment_id') else None
            ).model_dump())
