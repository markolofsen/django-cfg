"""
Payment service for the Universal Payment System v2.0.

Handles payment creation, status checking, and lifecycle management.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from django_cfg.modules.django_currency import convert_currency, get_exchange_rate
from .base import BaseService
from ..types import (
    PaymentCreateRequest, PaymentStatusRequest, PaymentResult,
    PaymentData, ServiceOperationResult
)
from ...models import UniversalPayment, Currency, ProviderCurrency
from ..providers import ProviderRegistry, get_provider_registry

User = get_user_model()

class PaymentService(BaseService):
    """
    Payment service with business logic and validation.
    
    Handles payment operations using Pydantic validation and Django ORM managers.
    """
    
    def __init__(self):
        """Initialize payment service with configuration."""
        super().__init__()
        # Direct Constance access instead of ConfigService
        self.provider_registry = get_provider_registry()
    
    def create_payment(self, request: PaymentCreateRequest) -> PaymentResult:
        """
        Create new payment with full validation.
        
        Args:
            request: Payment creation request with validation
            
        Returns:
            PaymentResult: Result with payment data or error
        """
        try:
            # Validate request
            if isinstance(request, dict):
                request = PaymentCreateRequest(**request)
            
            self.logger.info("Creating payment", extra={
                'user_id': request.user_id,
                'amount_usd': request.amount_usd,
                'currency_code': request.currency_code,
                'provider': request.provider
            })
            
            # Get user
            try:
                user = User.objects.get(id=request.user_id)
            except User.DoesNotExist:
                return PaymentResult(
                    success=False,
                    message=f"User {request.user_id} not found",
                    error_code="user_not_found"
                )
            
            # Validate currency
            currency_result = self._validate_currency(request.currency_code)
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
                    callback_url=request.callback_url,
                    cancel_url=request.cancel_url,
                    description=request.description,
                    expires_at=timezone.now() + timezone.timedelta(hours=1)  # 1 hour expiry
                )
                return payment
            
            payment = self._execute_with_transaction(create_payment_transaction)
            
            # Create payment with provider
            from ..providers.base import PaymentRequest as ProviderPaymentRequest
            
            provider_request = ProviderPaymentRequest(
                amount_usd=request.amount_usd,
                currency_code=request.currency_code,
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
                    payment.crypto_amount = provider_response.amount
                    payment.payment_url = provider_response.payment_url
                    payment.qr_code_url = provider_response.qr_code_url
                    payment.wallet_address = provider_response.wallet_address
                    if provider_response.expires_at:
                        payment.expires_at = provider_response.expires_at
                    payment.save()
                    return payment
                
                payment = self._execute_with_transaction(update_payment_transaction)
            else:
                # Mark payment as failed if provider creation failed
                payment.mark_failed(
                    reason=provider_response.error_message,
                    error_code="provider_creation_failed"
                )
            
            # Convert to PaymentData using our helper method
            payment_data = self._convert_payment_to_data(payment)
            
            self._log_operation(
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
            
        except Exception as e:
            return PaymentResult(**self._handle_exception(
                "create_payment", e,
                user_id=request.user_id if hasattr(request, 'user_id') else None
            ).model_dump())
    
    def get_payment_status(self, request: PaymentStatusRequest) -> PaymentResult:
        """
        Get payment status with optional provider check.
        
        Args:
            request: Payment status request
            
        Returns:
            PaymentResult: Current payment status
        """
        try:
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
                provider_result = self._check_provider_status(payment)
                if provider_result.success and provider_result.data.get('status_changed'):
                    # Reload payment if status was updated
                    payment.refresh_from_db()
            
            # Convert to PaymentData using from_attributes
            payment_data = self._convert_payment_to_data(payment)
            
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
            return PaymentResult(**self._handle_exception(
                "get_payment_status", e,
                payment_id=request.payment_id if hasattr(request, 'payment_id') else None
            ).model_dump())
    
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
            
            success = self._execute_with_transaction(cancel_payment_transaction)
            
            if success:
                payment.refresh_from_db()
                payment_data = self._convert_payment_to_data(payment)
                
                self._log_operation(
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
            return PaymentResult(**self._handle_exception(
                "cancel_payment", e,
                payment_id=payment_id
            ).model_dump())
    
    def _validate_currency(self, currency_code: str) -> ServiceOperationResult:
        """Validate currency is supported."""
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)
            
            # Check if currency is supported by any provider
            provider_currency = ProviderCurrency.objects.filter(
                currency=currency,
                is_enabled=True
            ).first()
            
            if not provider_currency:
                return self._create_error_result(
                    f"Currency {currency_code} not supported by any provider",
                    "currency_not_supported"
                )
            
            return self._create_success_result(
                "Currency is valid",
                {'currency': currency}  # Wrap in dict for Pydantic
            )
            
        except Currency.DoesNotExist:
            return self._create_error_result(
                f"Currency {currency_code} not found",
                "currency_not_found"
            )
    
    def _convert_usd_to_crypto(self, amount_usd: float, currency_code: str) -> ServiceOperationResult:
        """Convert USD amount to cryptocurrency."""
        try:
            # Use django_currency module for conversion
            crypto_amount = convert_currency(amount_usd, 'USD', currency_code)
            
            return self._create_success_result(
                "Currency converted successfully",
                {
                    'amount_usd': amount_usd,
                    'crypto_amount': Decimal(str(crypto_amount)),
                    'currency_code': currency_code,
                    'exchange_rate': get_exchange_rate('USD', currency_code)
                }
            )
            
        except Exception as e:
            return self._create_error_result(
                f"Currency conversion failed: {e}",
                "conversion_failed"
            )
    
    def _check_provider_status(self, payment: UniversalPayment) -> ServiceOperationResult:
        """Check payment status with provider."""
        try:
            # This would integrate with provider services
            # For now, return success without changes
            return self._create_success_result(
                "Provider status checked",
                {'status_changed': False}
            )
            
        except Exception as e:
            return self._create_error_result(
                f"Provider check failed: {e}",
                "provider_check_failed"
            )
    
    def get_user_payments(
        self, 
        user_id: int, 
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> ServiceOperationResult:
        """Get user payments with pagination."""
        try:
            queryset = UniversalPayment.objects.filter(user_id=user_id)
            
            if status:
                queryset = queryset.filter(status=status)
            
            total_count = queryset.count()
            payments = queryset.order_by('-created_at')[offset:offset + limit]
            
            payment_data = []
            for payment in payments:
                payment_obj = self._convert_payment_to_data(payment)
                payment_data.append(payment_obj.model_dump())
            
            return self._create_success_result(
                f"Retrieved {len(payment_data)} payments",
                {
                    'payments': payment_data,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            )
            
        except Exception as e:
            return self._handle_exception(
                "get_user_payments", e,
                user_id=user_id
            )
    
    def _convert_payment_to_data(self, payment: UniversalPayment) -> PaymentData:
        """Convert Django UniversalPayment to PaymentData."""
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
    
    def get_payment_stats(self, days: int = 30) -> ServiceOperationResult:
        """Get payment statistics."""
        try:
            from datetime import timedelta
            
            since = timezone.now() - timedelta(days=days)
            
            stats = UniversalPayment.objects.filter(
                created_at__gte=since
            ).aggregate(
                total_payments=models.Count('id'),
                total_amount_usd=models.Sum('amount_usd'),
                completed_payments=models.Count(
                    'id', 
                    filter=models.Q(status=UniversalPayment.PaymentStatus.COMPLETED)
                ),
                failed_payments=models.Count(
                    'id',
                    filter=models.Q(status=UniversalPayment.PaymentStatus.FAILED)
                )
            )
            
            # Calculate success rate
            total = stats['total_payments'] or 0
            completed = stats['completed_payments'] or 0
            success_rate = (completed / total * 100) if total > 0 else 0
            
            stats['success_rate'] = round(success_rate, 2)
            stats['period_days'] = days
            
            return self._create_success_result(
                f"Payment statistics for {days} days",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("get_payment_stats", e)
