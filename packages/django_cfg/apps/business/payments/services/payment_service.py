"""
Payment service for Payments v2.0.

Business logic layer using Pydantic for validation.
Handles payment creation, status checking, and confirmation.
"""

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models import Payment, Transaction, UserBalance, Currency
from .providers import NowPaymentsProvider, PaymentRequest as ProviderPaymentRequest

User = get_user_model()
logger = logging.getLogger(__name__)


# Pydantic models for Service Layer

class CreatePaymentRequest(BaseModel):
    """Request для создания платежа (View → Service)."""

    user_id: int
    amount_usd: Decimal = Field(ge=Decimal('1.0'), le=Decimal('50000.0'))
    currency_code: str = Field(min_length=3, max_length=20)
    description: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(frozen=True)

    @field_validator('currency_code')
    @classmethod
    def validate_currency_code(cls, v):
        """Ensure currency code is uppercase."""
        return v.upper()


class PaymentResult(BaseModel):
    """Result создания платежа (Service → View)."""

    success: bool
    payment_id: Optional[UUID] = None
    internal_payment_id: Optional[str] = None
    pay_address: Optional[str] = None
    pay_amount: Optional[Decimal] = None
    currency_code: Optional[str] = None
    qr_code_url: Optional[str] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None


class CheckStatusRequest(BaseModel):
    """Request для проверки статуса (View → Service)."""

    payment_id: UUID
    user_id: int
    force_refresh: bool = Field(default=False, description="Force refresh from provider")

    model_config = ConfigDict(frozen=True)


class PaymentStatusResult(BaseModel):
    """Result проверки статуса (Service → View)."""

    success: bool
    status: str
    payment_id: UUID
    amount_usd: Decimal
    pay_amount: Optional[Decimal] = None
    currency_code: str
    transaction_hash: Optional[str] = None
    is_completed: bool = False
    message: Optional[str] = None
    error: Optional[str] = None


class ConfirmPaymentRequest(BaseModel):
    """Request для подтверждения платежа (View → Service)."""

    payment_id: UUID
    user_id: int

    model_config = ConfigDict(frozen=True)


class ConfirmPaymentResult(BaseModel):
    """Result подтверждения платежа (Service → View)."""

    success: bool
    payment_status: str
    transaction_id: Optional[UUID] = None
    balance_after: Optional[Decimal] = None
    message: str


# Service class

class PaymentService:
    """
    Service для работы с платежами.

    Использует Pydantic для валидации данных между слоями.
    """

    def __init__(self, provider: NowPaymentsProvider):
        """
        Initialize payment service.

        Args:
            provider: NowPayments provider instance
        """
        self.provider = provider

    @transaction.atomic
    def create_payment(self, request: CreatePaymentRequest) -> PaymentResult:
        """
        Создать платеж.

        Args:
            request: Validated Pydantic request

        Returns:
            PaymentResult with payment data or error
        """
        try:
            logger.info(
                f"Creating payment: user_id={request.user_id}, "
                f"amount=${request.amount_usd}, currency={request.currency_code}"
            )

            # Validate user exists
            try:
                user = User.objects.get(id=request.user_id)
            except User.DoesNotExist:
                return PaymentResult(success=False, error="User not found")

            # Validate currency exists and is active
            try:
                currency = Currency.objects.get(code=request.currency_code, is_active=True)
            except Currency.DoesNotExist:
                return PaymentResult(
                    success=False,
                    error=f"Currency {request.currency_code} is not available"
                )

            # Check amount limits
            if request.amount_usd < currency.min_amount_usd:
                return PaymentResult(
                    success=False,
                    error=f"Minimum amount is ${currency.min_amount_usd}"
                )

            # Create payment in database
            payment = Payment.objects.create(
                user=user,
                amount_usd=request.amount_usd,
                currency=currency,
                description=request.description or '',
                status='pending'
            )

            logger.info(f"Payment created in DB: {payment.id}")

            # Prepare provider request
            provider_request = ProviderPaymentRequest(
                amount_usd=request.amount_usd,
                currency_code=request.currency_code,
                order_id=payment.internal_payment_id,
                description=request.description
            )

            # Call provider
            provider_response = self.provider.create_payment(provider_request)

            if not provider_response.success:
                # Provider failed - mark payment as failed
                payment.status = 'failed'
                payment.provider_data = provider_response.raw_response
                payment.save(update_fields=['status', 'provider_data', 'updated_at'])

                logger.error(f"Provider failed: {provider_response.error_message}")

                return PaymentResult(
                    success=False,
                    payment_id=payment.id,
                    error=provider_response.error_message or "Payment creation failed"
                )

            # Success - update payment with provider data
            payment.provider_payment_id = provider_response.provider_payment_id
            payment.pay_address = provider_response.wallet_address
            payment.pay_amount = provider_response.amount
            payment.payment_url = provider_response.payment_url
            payment.expires_at = provider_response.expires_at
            payment.provider_data = provider_response.raw_response
            payment.status_changed_at = timezone.now()
            payment.save(update_fields=[
                'provider_payment_id', 'pay_address', 'pay_amount',
                'payment_url', 'expires_at', 'provider_data',
                'status_changed_at', 'updated_at'
            ])

            logger.info(
                f"Payment updated with provider data: "
                f"provider_id={payment.provider_payment_id}, "
                f"address={payment.pay_address}"
            )

            return PaymentResult(
                success=True,
                payment_id=payment.id,
                internal_payment_id=payment.internal_payment_id,
                pay_address=payment.pay_address,
                pay_amount=payment.pay_amount,
                currency_code=currency.code,
                qr_code_url=payment.get_qr_code_url(),
                expires_at=payment.expires_at.isoformat() if payment.expires_at else None
            )

        except Exception as e:
            logger.exception(f"Payment creation failed: {e}")
            return PaymentResult(
                success=False,
                error=f"Payment creation error: {str(e)}"
            )

    def check_payment_status(self, request: CheckStatusRequest) -> PaymentStatusResult:
        """
        Проверить статус платежа.

        Args:
            request: Validated Pydantic request

        Returns:
            PaymentStatusResult with current status
        """
        try:
            # Get payment from database
            try:
                payment = Payment.objects.select_related('currency', 'user').get(
                    id=request.payment_id,
                    user_id=request.user_id
                )
            except Payment.DoesNotExist:
                return PaymentStatusResult(
                    success=False,
                    status='',
                    payment_id=request.payment_id,
                    amount_usd=Decimal('0'),
                    currency_code='',
                    error="Payment not found"
                )

            # If payment is already completed/failed, return cached status
            if payment.is_completed or payment.is_failed:
                return PaymentStatusResult(
                    success=True,
                    status=payment.status,
                    payment_id=payment.id,
                    amount_usd=payment.amount_usd,
                    pay_amount=payment.pay_amount,
                    currency_code=payment.currency.code,
                    transaction_hash=payment.transaction_hash,
                    is_completed=payment.is_completed,
                    message="Payment already finalized"
                )

            # Check if we need to refresh from provider
            should_refresh = request.force_refresh or self._should_refresh_status(payment)

            if should_refresh and payment.provider_payment_id:
                # Fetch fresh status from provider
                provider_response = self.provider.get_payment_status(payment.provider_payment_id)

                if provider_response.success:
                    # Update payment with fresh data
                    self._update_payment_from_provider(payment, provider_response)

            return PaymentStatusResult(
                success=True,
                status=payment.status,
                payment_id=payment.id,
                amount_usd=payment.amount_usd,
                pay_amount=payment.pay_amount,
                currency_code=payment.currency.code,
                transaction_hash=payment.transaction_hash,
                is_completed=payment.is_completed,
                message="Status updated" if should_refresh else "Status from cache"
            )

        except Exception as e:
            logger.exception(f"Status check failed: {e}")
            return PaymentStatusResult(
                success=False,
                status='',
                payment_id=request.payment_id,
                amount_usd=Decimal('0'),
                currency_code='',
                error=f"Status check error: {str(e)}"
            )

    @transaction.atomic
    def confirm_payment(self, request: ConfirmPaymentRequest) -> ConfirmPaymentResult:
        """
        Подтвердить платеж (пользователь нажал "Я оплатил").

        Проверяет статус у провайдера и создает транзакцию если оплачено.

        Args:
            request: Validated Pydantic request

        Returns:
            ConfirmPaymentResult with result
        """
        try:
            # Get payment
            try:
                payment = Payment.objects.select_for_update().select_related('currency', 'user').get(
                    id=request.payment_id,
                    user_id=request.user_id
                )
            except Payment.DoesNotExist:
                return ConfirmPaymentResult(
                    success=False,
                    payment_status='',
                    message="Payment not found"
                )

            # Check if already completed
            if payment.is_completed:
                user_balance = UserBalance.get_or_create_for_user(payment.user)
                return ConfirmPaymentResult(
                    success=True,
                    payment_status=payment.status,
                    balance_after=user_balance.balance_usd,
                    message="Payment already completed"
                )

            # Check if failed/expired
            if payment.is_failed:
                return ConfirmPaymentResult(
                    success=False,
                    payment_status=payment.status,
                    message=f"Payment is {payment.status}"
                )

            # Check status from provider
            if not payment.provider_payment_id:
                return ConfirmPaymentResult(
                    success=False,
                    payment_status=payment.status,
                    message="Payment not yet initialized with provider"
                )

            provider_response = self.provider.get_payment_status(payment.provider_payment_id)

            if not provider_response.success:
                return ConfirmPaymentResult(
                    success=False,
                    payment_status=payment.status,
                    message=f"Failed to check payment status: {provider_response.error_message}"
                )

            # Update payment status
            self._update_payment_from_provider(payment, provider_response)

            # Check if completed
            if payment.status == 'completed':
                # Create deposit transaction
                transaction_obj = self._create_deposit_transaction(payment)

                # Get updated balance
                user_balance = UserBalance.get_or_create_for_user(payment.user)

                logger.info(
                    f"Payment confirmed: payment_id={payment.id}, "
                    f"transaction_id={transaction_obj.id}, "
                    f"balance=${user_balance.balance_usd}"
                )

                return ConfirmPaymentResult(
                    success=True,
                    payment_status=payment.status,
                    transaction_id=transaction_obj.id,
                    balance_after=user_balance.balance_usd,
                    message="Payment confirmed! Funds added to your balance."
                )

            elif payment.status == 'partially_paid':
                return ConfirmPaymentResult(
                    success=False,
                    payment_status=payment.status,
                    message="Payment partially paid. Please contact support or send the remaining amount."
                )

            else:
                # Still pending/confirming
                return ConfirmPaymentResult(
                    success=False,
                    payment_status=payment.status,
                    message=f"Payment is {payment.status}. Please wait for blockchain confirmation."
                )

        except Exception as e:
            logger.exception(f"Payment confirmation failed: {e}")
            return ConfirmPaymentResult(
                success=False,
                payment_status='',
                message=f"Confirmation error: {str(e)}"
            )

    def _should_refresh_status(self, payment: Payment) -> bool:
        """
        Определить нужно ли обновлять статус от провайдера.

        Returns:
            True if should refresh (not refreshed in last 5 seconds)
        """
        if not payment.status_changed_at:
            return True

        # Refresh if last check was more than 5 seconds ago
        time_since_check = (timezone.now() - payment.status_changed_at).total_seconds()
        return time_since_check > 5

    def _update_payment_from_provider(self, payment: Payment, provider_response) -> None:
        """
        Обновить payment из ответа провайдера.

        Args:
            payment: Payment instance
            provider_response: ProviderResponse from provider
        """
        old_status = payment.status
        payment.status = provider_response.status
        payment.status_changed_at = timezone.now()

        if provider_response.transaction_hash:
            payment.transaction_hash = provider_response.transaction_hash

        if provider_response.actual_amount:
            payment.actual_amount = provider_response.actual_amount

        # Merge provider data
        if provider_response.raw_response:
            payment.provider_data = {
                **payment.provider_data,
                'last_check': timezone.now().isoformat(),
                'latest_response': provider_response.raw_response
            }

        # Set completed_at if just completed
        if payment.status == 'completed' and not payment.completed_at:
            payment.completed_at = timezone.now()

        payment.save(update_fields=[
            'status', 'status_changed_at', 'transaction_hash',
            'actual_amount', 'provider_data', 'completed_at', 'updated_at'
        ])

        logger.info(f"Payment status updated: {old_status} → {payment.status}")

    def _create_deposit_transaction(self, payment: Payment) -> Transaction:
        """
        Создать транзакцию пополнения для completed платежа.

        Args:
            payment: Completed payment

        Returns:
            Created Transaction instance
        """
        # Get or create user balance
        user_balance = UserBalance.get_or_create_for_user(payment.user)

        # Calculate new balance
        amount = payment.actual_amount_usd or payment.amount_usd
        new_balance = user_balance.balance_usd + amount

        # Create transaction
        transaction_obj = Transaction.objects.create(
            user=payment.user,
            transaction_type='deposit',
            amount_usd=amount,
            balance_after=new_balance,
            payment_id=payment.internal_payment_id,
            description=f"Deposit via {payment.currency.code}",
            metadata={
                'payment_id': str(payment.id),
                'currency_code': payment.currency.code,
                'transaction_hash': payment.transaction_hash or '',
            }
        )

        # Update user balance
        user_balance.balance_usd = new_balance
        user_balance.total_deposited += amount
        user_balance.last_transaction_at = timezone.now()
        user_balance.save(update_fields=[
            'balance_usd', 'total_deposited', 'last_transaction_at', 'updated_at'
        ])

        logger.info(
            f"Deposit transaction created: user={payment.user.id}, "
            f"amount=${amount}, balance=${new_balance}"
        )

        return transaction_obj
