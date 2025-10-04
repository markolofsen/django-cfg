"""
Payment creation logic.

Handles payment creation with full validation and provider integration.
"""

from typing import TYPE_CHECKING
from django.contrib.auth import get_user_model
from django.utils import timezone

from ...types import PaymentCreateRequest, PaymentResult
from ..utils import DataConverter

if TYPE_CHECKING:
    from ..currency import CurrencyValidator
    from ...providers import ProviderRegistry

User = get_user_model()


class PaymentCreator:
    """Handle payment creation."""

    def __init__(
        self,
        provider_registry: 'ProviderRegistry',
        currency_validator: 'CurrencyValidator',
        base_service
    ):
        """
        Initialize payment creator.

        Args:
            provider_registry: Provider registry for payment providers
            currency_validator: Currency validator
            base_service: Base service for transactions, logging, and result creation
        """
        self.provider_registry = provider_registry
        self.currency_validator = currency_validator
        self.base_service = base_service
        self.logger = base_service.logger

    def create_payment(
        self,
        request: PaymentCreateRequest,
        user
    ) -> PaymentResult:
        """
        Create new payment with full validation.

        Steps:
        1. Validate currency
        2. Create payment in database
        3. Create payment with provider
        4. Update payment with provider response

        Args:
            request: Payment creation request with validation
            user: User creating the payment

        Returns:
            PaymentResult: Result with payment data or error
        """
        try:
            from ....models import UniversalPayment

            # Validate currency
            currency_result = self.currency_validator.validate_currency(request.currency_code)
            if not currency_result.success:
                return PaymentResult(
                    success=False,
                    message=currency_result.message,
                    error_code=currency_result.error_code
                )

            # Get provider for payment creation
            provider = self.provider_registry.get_provider(request.provider)
            if not provider:
                return PaymentResult(
                    success=False,
                    message=f"Provider {request.provider} not available",
                    error_code="provider_not_available"
                )

            # Create payment in database first
            def create_payment_transaction():
                currency = currency_result.data['currency']
                payment = UniversalPayment.objects.create(
                    user=user,
                    amount_usd=request.amount_usd,
                    currency=currency,
                    network=currency.native_networks.first(),  # Use first native network
                    provider=request.provider,
                    status=UniversalPayment.PaymentStatus.PENDING,
                    status_changed_at=timezone.now(),  # Track initial status setting
                    callback_url=request.callback_url,
                    cancel_url=request.cancel_url,
                    description=request.description,
                    expires_at=timezone.now() + timezone.timedelta(hours=1)  # 1 hour expiry
                )
                return payment

            payment = self.base_service._execute_with_transaction(create_payment_transaction)

            # Create payment with provider
            from ...providers.models import PaymentRequest as ProviderPaymentRequest

            # Use provider_currency_code from metadata if available, otherwise use original currency_code
            provider_currency_code = request.metadata.get('provider_currency_code', request.currency_code)

            provider_request = ProviderPaymentRequest(
                amount_usd=request.amount_usd,
                currency_code=provider_currency_code,  # Use provider-specific currency code
                order_id=str(payment.id),
                callback_url=request.callback_url,
                cancel_url=request.cancel_url,
                description=request.description,
                metadata=request.metadata
            )

            provider_response = provider.create_payment(provider_request)

            # Update payment with provider response
            if provider_response.success:
                def update_payment_transaction():
                    payment.provider_payment_id = provider_response.provider_payment_id
                    payment.pay_amount = provider_response.amount  # Fix: use pay_amount instead of crypto_amount
                    payment.payment_url = provider_response.payment_url
                    payment.qr_code_url = provider_response.qr_code_url
                    payment.pay_address = provider_response.wallet_address  # Fix: use pay_address instead of wallet_address
                    if provider_response.expires_at:
                        payment.expires_at = provider_response.expires_at
                    payment.save()
                    return payment

                payment = self.base_service._execute_with_transaction(update_payment_transaction)

                # Convert to PaymentData
                payment_data = DataConverter.payment_to_data(payment)

                self.base_service._log_operation(
                    "create_payment",
                    True,
                    payment_id=str(payment.id),
                    user_id=request.user_id,
                    amount_usd=request.amount_usd
                )

                return PaymentResult(
                    success=True,
                    message="Payment created successfully",
                    payment_id=str(payment.id),
                    status=payment.status,
                    amount_usd=payment.amount_usd,
                    crypto_amount=payment.pay_amount,
                    currency_code=payment.currency.code,
                    payment_url=payment.payment_url,
                    expires_at=payment.expires_at,
                    data={'payment': payment_data.model_dump()}
                )

            else:
                # Mark payment as failed if provider creation failed
                self.logger.error("❌ PAYMENT SERVICE: Provider creation failed", extra={
                    'payment_id': str(payment.id),
                    'provider_error': getattr(provider_response, 'error_message', 'Unknown error')
                })
                payment.mark_failed(
                    reason=provider_response.error_message,
                    error_code="provider_creation_failed"
                )

                # Return error result when provider fails
                self.base_service._log_operation(
                    "create_payment",
                    False,
                    payment_id=str(payment.id),
                    user_id=request.user_id,
                    amount_usd=request.amount_usd,
                    error=provider_response.error_message
                )

                return PaymentResult(
                    success=False,
                    message=provider_response.error_message or "Payment creation failed",
                    error_code="provider_creation_failed",
                    payment_id=str(payment.id),
                    status=payment.status,
                    data={'error_details': getattr(provider_response, 'raw_response', {})}
                )

        except Exception as e:
            return PaymentResult(**self.base_service._handle_exception(
                "create_payment", e,
                user_id=request.user_id if hasattr(request, 'user_id') else None
            ).model_dump())
