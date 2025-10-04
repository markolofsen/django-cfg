"""
Provider communication.

Handles interactions with payment providers including status checks.
"""

from typing import TYPE_CHECKING
from django.db import transaction
from django.utils import timezone

from ...types import ServiceOperationResult
from ....models.managers.payment_managers import PaymentStatusUpdateFields
from .status_mapper import StatusMapper

if TYPE_CHECKING:
    from ....models import UniversalPayment


class ProviderClient:
    """Handle provider interactions."""

    def __init__(self, provider_registry, base_service):
        """
        Initialize provider client.

        Args:
            provider_registry: Provider registry instance
            base_service: Base service for logging and result creation
        """
        self.provider_registry = provider_registry
        self.base_service = base_service
        self.logger = base_service.logger

    def check_status(self, payment: 'UniversalPayment') -> ServiceOperationResult:
        """
        Check payment status with provider and update if changed.

        Args:
            payment: Payment object to check

        Returns:
            ServiceOperationResult: Result with status_changed flag
        """
        try:
            self.logger.debug("Checking provider status", extra={
                'payment_id': str(payment.id),
                'current_status': payment.status,
                'provider': payment.provider
            })

            # Get provider instance
            provider = self.provider_registry.get_provider(payment.provider)

            if not provider:
                return self.base_service._create_error_result(
                    f"Provider {payment.provider} not found",
                    "provider_not_found"
                )

            # Get status from provider
            provider_response = provider.get_payment_status(payment.provider_payment_id)

            if not provider_response.success:
                self.logger.warning("Provider status check failed", extra={
                    'payment_id': str(payment.id),
                    'provider': payment.provider,
                    'error': provider_response.error_message
                })
                return self.base_service._create_error_result(
                    f"Provider status check failed: {provider_response.error_message}",
                    "provider_check_failed"
                )

            # Map provider status to universal status
            from ....models import UniversalPayment
            provider_status = provider_response.data.get('status', '').lower()
            new_status = StatusMapper.map_status_to_enum(
                provider_status,
                UniversalPayment.PaymentStatus
            )

            if not new_status:
                new_status = payment.status

            status_changed = new_status != payment.status

            # Update payment if status changed
            if status_changed:
                with transaction.atomic():
                    # Prepare extra fields from provider response
                    provider_data = provider_response.data

                    extra_fields = PaymentStatusUpdateFields(
                        transaction_hash=provider_data.get('transaction_hash'),
                        confirmations_count=provider_data.get('confirmations_count')
                    )

                    # Use manager method for consistent status updates
                    success = UniversalPayment.objects.update_payment_status(
                        payment, new_status, extra_fields
                    )

                    if not success:
                        return self.base_service._create_error_result(
                            "Failed to update payment status",
                            "status_update_failed"
                        )

                self.logger.info("Payment status updated", extra={
                    'payment_id': str(payment.id),
                    'old_status': payment.status,
                    'new_status': new_status,
                    'provider_status': provider_status
                })

            return self.base_service._create_success_result(
                "Provider status checked",
                {
                    'status_changed': status_changed,
                    'old_status': payment.status if not status_changed else None,
                    'new_status': new_status,
                    'provider_status': provider_status,
                    'provider_response': provider_response.data
                }
            )

        except Exception as e:
            self.logger.error("Error checking provider status", extra={
                'payment_id': str(payment.id),
                'error': str(e)
            })
            return self.base_service._handle_exception("_check_provider_status", e)
