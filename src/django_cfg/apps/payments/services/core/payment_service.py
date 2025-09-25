"""
Payment Service - Core payment processing logic.

This service handles universal payment operations, provider orchestration,
and payment lifecycle management.
"""

from typing import Optional, List
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from pydantic import BaseModel, Field, ValidationError

from .balance_service import BalanceService
from .fallback_service import get_fallback_service
from ...models import UniversalPayment, UserBalance, Transaction
from ...utils.config_utils import get_payments_config
from ..providers.registry import ProviderRegistry
from django_cfg.modules.django_logger import get_logger
from ..monitoring.provider_health import get_health_monitor
from ..internal_types import (
    ProviderResponse, WebhookData, ServiceOperationResult,
    BalanceUpdateRequest, AccessCheckRequest, AccessCheckResult,
    PaymentCreationResult, WebhookProcessingResult, PaymentStatusResult,
    PaymentHistoryItem, ProviderInfo
)

# Import django_currency module for currency conversion
from django_cfg.modules.django_currency import convert_currency, CurrencyError
from ...models.events import PaymentEvent

User = get_user_model()
logger = get_logger("payment_service")


class PaymentRequest(BaseModel):
    """Type-safe payment request validation"""
    user_id: int = Field(gt=0, description="User ID")
    amount: Decimal = Field(gt=0, description="Payment amount")
    currency: str = Field(min_length=3, max_length=10, description="Currency code")
    provider: str = Field(min_length=1, description="Payment provider name")
    callback_url: Optional[str] = Field(None, description="Success callback URL")
    cancel_url: Optional[str] = Field(None, description="Cancellation URL")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class PaymentResult(BaseModel):
    """Type-safe payment operation result"""
    success: bool
    payment_id: Optional[str] = None
    provider_payment_id: Optional[str] = None
    payment_url: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class WebhookProcessingResult(BaseModel):
    """Type-safe webhook processing result"""
    success: bool
    payment_id: Optional[str] = None
    status_updated: bool = False
    balance_updated: bool = False
    error_message: Optional[str] = None


class PaymentService:
    """
    Universal payment processing service.
    
    Handles payment creation, webhook processing, and provider management.
    Integrates with balance management and caching.
    """
    
    def __init__(self):
        """Initialize payment service with dependencies"""
        self.provider_registry = ProviderRegistry()
        self.config = get_payments_config()
    
    def create_payment(self, payment_data: dict) -> 'PaymentCreationResult':
        """
        Create a new payment with the specified provider.
        
        Args:
            payment_data: Dictionary with payment details
            
        Returns:
            PaymentCreationResult with payment details or error information
        """
        try:
            # Validate payment request
            request = PaymentRequest(
                user_id=payment_data['user_id'],
                amount=payment_data['amount'],
                currency=payment_data.get('currency', 'USD'),
                provider=payment_data['provider'],
                metadata=payment_data.get('metadata', {})
            )
            
            # Get provider instance
            provider_instance = self.provider_registry.get_provider(request.provider)
            if not provider_instance:
                return PaymentCreationResult(
                    success=False,
                    error=f"Payment provider '{request.provider}' is not available"
                )
            
            # Get user
            user = User.objects.get(id=request.user_id)
            
            # Convert currency if needed
            amount_usd = self._convert_to_usd(request.amount, request.currency) if request.currency != 'USD' else request.amount
            
            # Create payment record
            with transaction.atomic():
                payment = UniversalPayment.objects.create(
                    user=user,
                    provider=request.provider,
                    amount_usd=amount_usd,
                    currency_code=request.currency,
                    status=UniversalPayment.PaymentStatus.PENDING,
                    metadata=request.metadata
                )
                
                # Prepare provider data
                provider_data = {
                    'amount': float(request.amount),
                    'currency': request.currency,
                    'user_id': user.id,
                    'payment_id': str(payment.id),
                    'callback_url': request.callback_url,
                    'cancel_url': request.cancel_url,
                    **request.metadata
                }
                
                # Process with provider
                provider_result = provider_instance.create_payment(provider_data)
                
                if provider_result.success:
                    # Update payment with provider data
                    payment.provider_payment_id = provider_result.provider_payment_id
                    payment.save()
                    
                    
                    return PaymentCreationResult(
                        success=True,
                        payment_id=str(payment.id),
                        provider_payment_id=provider_result.provider_payment_id,
                        payment_url=provider_result.payment_url
                    )
                else:
                    # Mark payment as failed
                    payment.status = UniversalPayment.PaymentStatus.FAILED
                    payment.error_message = provider_result.error_message or 'Unknown provider error'
                    payment.save()
                    
                    return PaymentCreationResult(
                        success=False,
                        payment_id=str(payment.id),
                        error=provider_result.error_message or 'Payment creation failed'
                    )
                    
        except ValidationError as e:
            logger.error(f"Payment validation error: {e}")
            return PaymentCreationResult(
                success=False,
                error=f"Invalid payment data: {e}"
            )
        except Exception as e:
            logger.error(f"Payment creation failed: {e}", exc_info=True)
            return PaymentCreationResult(
                success=False,
                error=f"Internal error: {str(e)}"
            )
    
    def process_webhook(
        self,
        provider: str,
        webhook_data: dict,
        request_headers: Optional[dict] = None
    ) -> 'WebhookProcessingResult':
        """
        Process payment webhook from provider.
        
        Args:
            provider: Payment provider name
            webhook_data: Webhook payload data
            request_headers: HTTP headers for validation
            
        Returns:
            WebhookProcessingResult with processing status
        """
        try:
            # Get provider instance
            provider_instance = self.provider_registry.get_provider(provider)
            if not provider_instance:
                return WebhookProcessingResult(
                    success=False,
                    error=f"Provider '{provider}' not found"
                )
            
            # Process webhook with provider
            webhook_result = provider_instance.process_webhook(webhook_data)
            if not webhook_result.success:
                return WebhookProcessingResult(
                    success=False,
                    error=webhook_result.error_message or "Webhook processing failed"
                )
            
            # Find payment by provider payment ID
            try:
                payment = UniversalPayment.objects.get(
                    provider_payment_id=webhook_result.provider_payment_id
                )
            except UniversalPayment.DoesNotExist:
                return WebhookProcessingResult(
                    success=False,
                    error=f"Payment not found: {webhook_result.provider_payment_id}"
                )
            
            # Process payment status update
            old_status = payment.status
            new_status = webhook_result.status
            
            with transaction.atomic():
                # Update payment
                payment.status = new_status
                payment.save()
                
                # Process completion if status changed to completed
                balance_updated = False
                if (new_status == UniversalPayment.PaymentStatus.COMPLETED and 
                    old_status != UniversalPayment.PaymentStatus.COMPLETED):
                    balance_updated = self._process_payment_completion(payment)
                
                
                return WebhookProcessingResult(
                    success=True,
                    payment_id=str(payment.id),
                    status_updated=(old_status != new_status),
                    balance_updated=balance_updated
                )
                
        except Exception as e:
            logger.error(f"Webhook processing failed for {provider}: {e}", exc_info=True)
            return WebhookProcessingResult(
                success=False,
                error=f"Webhook processing error: {str(e)}"
            )
    
    def get_payment_status(self, payment_id: str) -> Optional['PaymentStatusResult']:
        """
        Get payment status by ID.
        
        Args:
            payment_id: Payment UUID
            
        Returns:
            Payment status information or None if not found
        """
        try:
            
            # Get from database
            payment = UniversalPayment.objects.get(id=payment_id)
            
            return PaymentStatusResult(
                payment_id=str(payment.id),
                status=payment.status,
                amount_usd=payment.amount_usd,
                currency_code=payment.currency_code,
                provider=payment.provider,
                provider_payment_id=payment.provider_payment_id,
                created_at=payment.created_at,
                updated_at=payment.updated_at
            )
            
        except UniversalPayment.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting payment status {payment_id}: {e}")
            return None
    
    def get_user_payments(
        self,
        user: User,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PaymentHistoryItem]:
        """
        Get user's payment history.
        
        Args:
            user: User object
            status: Filter by payment status
            limit: Number of payments to return
            offset: Pagination offset
            
        Returns:
            List of PaymentHistoryItem objects
        """
        try:
            queryset = UniversalPayment.objects.filter(user=user)
            
            if status:
                queryset = queryset.filter(status=status)
            
            payments = queryset.order_by('-created_at')[offset:offset+limit]
            
            return [
                PaymentHistoryItem(
                    id=str(payment.id),
                    user_id=payment.user.id,
                    amount=payment.pay_amount if payment.pay_amount else payment.amount_usd,
                    currency=payment.currency_code,
                    status=payment.status,
                    provider=payment.provider.name if payment.provider else 'unknown',
                    provider_payment_id=payment.provider_payment_id,
                    created_at=payment.created_at,
                    updated_at=payment.updated_at,
                    metadata=payment.metadata or {}
                )
                for payment in payments
            ]
            
        except Exception as e:
            logger.error(f"Error getting user payments for {user.id}: {e}")
            return []
    
    def _process_payment_completion(self, payment: UniversalPayment) -> bool:
        """
        Process completed payment by adding funds to user balance.
        
        Args:
            payment: Completed payment object
            
        Returns:
            True if balance was updated, False otherwise
        """
        try:
            
            balance_service = BalanceService()
            result = balance_service.add_funds(
                user=payment.user,
                amount=payment.amount_usd,
                currency_code='USD',
                source='payment',
                reference_id=str(payment.id),
                metadata={
                    'provider': payment.provider.name if payment.provider else 'unknown',
                    'provider_payment_id': payment.provider_payment_id,
                    'pay_amount': str(payment.pay_amount) if payment.pay_amount else str(payment.amount_usd),
                    'currency_code': payment.currency_code
                }
            )
            
            
            return result.success
            
        except Exception as e:
            logger.error(f"Error processing payment completion {payment.id}: {e}")
            return False
    
    def _convert_to_usd(self, amount: Decimal, currency: str) -> Decimal:
        """
        Convert amount to USD using django_currency module.
        
        Args:
            amount: Amount to convert
            currency: Source currency
            
        Returns:
            Amount in USD
        """
        if currency == 'USD':
            return amount
        
        try:
            # Use django_currency module for conversion
            converted_amount = convert_currency(
                amount=float(amount),
                from_currency=currency,
                to_currency='USD'
            )
            
            logger.info(f"Currency conversion: {amount} {currency} = {converted_amount} USD")
            return Decimal(str(converted_amount))
            
        except CurrencyError as e:
            logger.error(f"Currency conversion failed for {amount} {currency} to USD: {e}")
            # Fallback to 1:1 rate if conversion fails
            logger.warning(f"Using 1:1 fallback rate for {currency} to USD")
            return amount
            
        except Exception as e:
            logger.error(f"Unexpected error in currency conversion: {e}")
            # Fallback to 1:1 rate for any other errors
            logger.warning(f"Using 1:1 fallback rate for {currency} to USD due to error")
            return amount
    
    def process_webhook(self, provider: str, webhook_data: dict, headers: dict = None) -> 'WebhookProcessingResult':
        """
        Process webhook from payment provider.
        
        Args:
            provider: Provider name
            webhook_data: Webhook payload
            headers: Request headers for validation
            
        Returns:
            WebhookProcessingResult with processing status
        """
        try:
            # Get provider instance for validation
            provider_instance = self.provider_registry.get_provider(provider)
            if not provider_instance:
                return WebhookProcessingResult(
                    success=False,
                    error_message=f"Unknown provider: {provider}"
                )
            
            # Validate webhook
            if hasattr(provider_instance, 'validate_webhook'):
                is_valid = provider_instance.validate_webhook(webhook_data, headers)
                if not is_valid:
                    logger.warning(f"Invalid webhook from {provider}: {webhook_data}")
                    return WebhookProcessingResult(
                        success=False,
                        error_message="Webhook validation failed"
                    )
            
            # Process webhook data
            processed_data = provider_instance.process_webhook(webhook_data)
            
            # Find payment record
            payment_id = processed_data.payment_id
            if not payment_id:
                return WebhookProcessingResult(
                    success=False,
                    error_message="No payment ID found in webhook"
                )
            
            # Update payment
            with transaction.atomic():
                try:
                    payment = UniversalPayment.objects.get(
                        provider_payment_id=payment_id,
                        provider=provider
                    )
                    
                    # Update payment status and data
                    old_status = payment.status
                    payment.update_from_webhook(webhook_data)
                    
                    # Create event for audit trail
                    self._create_payment_event(
                        payment=payment,
                        event_type='webhook_processed',
                        data={
                            'provider': provider,
                            'old_status': old_status,
                            'new_status': payment.status,
                            'webhook_data': webhook_data
                        }
                    )
                    
                    # Process completion if needed
                    if payment.is_completed and old_status != payment.status:
                        success = self._process_payment_completion(payment)
                        if success:
                            payment.processed_at = timezone.now()
                            payment.save()
                    
                    return WebhookProcessingResult(
                        success=True,
                        payment_id=str(payment.id),
                        new_status=payment.status
                    )
                    
                except UniversalPayment.DoesNotExist:
                    logger.error(f"Payment not found for webhook: provider={provider}, payment_id={payment_id}")
                    return WebhookProcessingResult(
                        success=False,
                        error_message="Payment not found"
                    )
        
        except Exception as e:
            logger.error(f"Error processing webhook from {provider}: {e}")
            return WebhookProcessingResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_payment_event(self, payment: UniversalPayment, event_type: str, data: dict):
        """
        Create payment event for audit trail.
        
        Args:
            payment: Payment object
            event_type: Type of event
            data: Event data
        """
        try:
            # Get next sequence number
            last_event = PaymentEvent.objects.filter(
                payment_id=str(payment.id)
            ).order_by('-sequence_number').first()
            
            sequence_number = (last_event.sequence_number + 1) if last_event else 1
            
            PaymentEvent.objects.create(
                payment_id=str(payment.id),
                event_type=event_type,
                sequence_number=sequence_number,
                event_data=data,
                processed_by=f"payment_service_{timezone.now().timestamp()}",
                correlation_id=data.get('correlation_id'),
                idempotency_key=f"{payment.id}_{event_type}_{sequence_number}"
            )
            
        except Exception as e:
            logger.error(f"Failed to create payment event: {e}")
    
    def get_payment_events(self, payment_id: str) -> List[dict]:
        """
        Get all events for a payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            List of payment events
        """
        try:
            events = PaymentEvent.objects.filter(
                payment_id=payment_id
            ).order_by('sequence_number')
            
            return [
                {
                    'id': str(event.id),
                    'event_type': event.event_type,
                    'sequence_number': event.sequence_number,
                    'event_data': event.event_data,
                    'created_at': event.created_at,
                    'processed_by': event.processed_by
                }
                for event in events
            ]
            
        except Exception as e:
            logger.error(f"Error getting payment events for {payment_id}: {e}")
            return []
    
    
    def list_available_providers(self) -> List[ProviderInfo]:
        """
        List all available payment providers.
        
        Returns:
            List of ProviderInfo objects
        """
        return [
            ProviderInfo(
                name=name,
                display_name=provider.get_display_name(),
                supported_currencies=provider.get_supported_currencies(),
                is_active=provider.is_active(),
                features={'provider_type': provider.get_provider_type()}
            )
            for name, provider in self.provider_registry.get_all_providers().items()
        ]