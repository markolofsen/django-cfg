"""
Webhook service for the Universal Payment System v2.0.

Handles webhook validation and processing from payment providers.
"""

from typing import Optional, Dict, Any
import json
from django.utils import timezone
from django.db import models

from .base import BaseService
from ..types import (
    WebhookValidationRequest, WebhookProcessingResult, NowPaymentsWebhook,
    WebhookSignature, ServiceOperationResult
)
from ...models import UniversalPayment
from .payment_service import PaymentService
from .balance_service import BalanceService
# ConfigService removed - using direct Constance access


class WebhookService(BaseService):
    """
    Webhook service with validation and processing logic.
    
    Handles webhook operations using Pydantic validation and provider-specific logic.
    """
    
    def __init__(self):
        """Initialize webhook service with dependencies."""
        super().__init__()
        self.payment_service = PaymentService()
        self.balance_service = BalanceService()
        # Direct Constance access instead of ConfigService
    
    def validate_webhook(self, request: WebhookValidationRequest) -> ServiceOperationResult:
        """
        Validate webhook signature and payload.
        
        Args:
            request: Webhook validation request
            
        Returns:
            ServiceOperationResult: Validation result
        """
        try:
            # Validate request
            if isinstance(request, dict):
                request = WebhookValidationRequest(**request)
            
            self.logger.info("Validating webhook", extra={
                'provider': request.provider,
                'has_signature': bool(request.signature)
            })
            
            # Provider-specific validation
            if request.provider.lower() == 'nowpayments':
                return self._validate_nowpayments_webhook(request)
            else:
                return self._create_error_result(
                    f"Unsupported provider: {request.provider}",
                    "unsupported_provider"
                )
                
        except Exception as e:
            return self._handle_exception(
                "validate_webhook", e,
                provider=request.provider if hasattr(request, 'provider') else None
            )
    
    def process_webhook(self, request: WebhookValidationRequest) -> WebhookProcessingResult:
        """
        Process validated webhook and update payment status.
        
        Args:
            request: Webhook validation request
            
        Returns:
            WebhookProcessingResult: Processing result with actions taken
        """
        try:
            # First validate webhook
            validation_result = self.validate_webhook(request)
            if not validation_result.success:
                return WebhookProcessingResult(
                    success=False,
                    provider=request.provider,
                    error_message=validation_result.message,
                    processed=False
                )
            
            self.logger.info("Processing webhook", extra={
                'provider': request.provider,
                'payload_keys': list(request.payload.keys())
            })
            
            # Provider-specific processing
            if request.provider.lower() == 'nowpayments':
                return self._process_nowpayments_webhook(request)
            else:
                return WebhookProcessingResult(
                    success=False,
                    provider=request.provider,
                    error_message=f"Unsupported provider: {request.provider}",
                    processed=False
                )
                
        except Exception as e:
            error_result = self._handle_exception(
                "process_webhook", e,
                provider=request.provider if hasattr(request, 'provider') else None
            )
            
            return WebhookProcessingResult(
                success=False,
                provider=request.provider if hasattr(request, 'provider') else 'unknown',
                error_message=error_result.message,
                processed=False
            )
    
    def _validate_nowpayments_webhook(self, request: WebhookValidationRequest) -> ServiceOperationResult:
        """Validate NowPayments webhook."""
        try:
            # Validate payload structure
            try:
                webhook_data = NowPaymentsWebhook(**request.payload)
            except Exception as e:
                return self._create_error_result(
                    f"Invalid NowPayments webhook payload: {e}",
                    "invalid_payload"
                )
            
            # Validate signature if provided
            signature_valid = True
            if request.signature:
                signature_result = self._validate_nowpayments_signature(request)
                signature_valid = signature_result.success
                
                if not signature_valid:
                    return self._create_error_result(
                        "Invalid webhook signature",
                        "invalid_signature"
                    )
            
            return self._create_success_result(
                "NowPayments webhook validated successfully",
                {
                    'provider': 'nowpayments',
                    'payment_id': webhook_data.payment_id,
                    'status': webhook_data.payment_status,
                    'signature_valid': signature_valid,
                    'parsed_data': webhook_data.model_dump()
                }
            )
            
        except Exception as e:
            return self._create_error_result(
                f"NowPayments validation error: {e}",
                "validation_error"
            )
    
    def _validate_nowpayments_signature(self, request: WebhookValidationRequest) -> ServiceOperationResult:
        """Validate NowPayments webhook signature."""
        try:
            # Get secret key from Constance settings
            constance_settings = self.config_service.get_constance_settings()
            provider_keys = constance_settings.get_provider_keys('nowpayments')
            secret_key = provider_keys.get('ipn_secret', '')
            
            if not secret_key:
                return self._create_error_result(
                    "NowPayments IPN secret not configured",
                    "missing_secret_key"
                )
            
            # Create signature validator
            payload_string = json.dumps(request.payload, separators=(',', ':'), sort_keys=True)
            
            signature_validator = WebhookSignature(
                provider='nowpayments',
                signature=request.signature,
                payload=payload_string,
                secret_key=secret_key,
                algorithm='sha512'
            )
            
            is_valid = signature_validator.validate_signature()
            
            if is_valid:
                return self._create_success_result("Signature is valid")
            else:
                return self._create_error_result(
                    "Invalid signature",
                    "invalid_signature"
                )
                
        except Exception as e:
            return self._create_error_result(
                f"Signature validation error: {e}",
                "signature_validation_error"
            )
    
    def _process_nowpayments_webhook(self, request: WebhookValidationRequest) -> WebhookProcessingResult:
        """Process NowPayments webhook."""
        try:
            # Parse webhook data
            webhook_data = NowPaymentsWebhook(**request.payload)
            
            # Find payment by provider payment ID
            try:
                payment = UniversalPayment.objects.get(
                    provider_payment_id=webhook_data.payment_id
                )
            except UniversalPayment.DoesNotExist:
                return WebhookProcessingResult(
                    success=False,
                    provider='nowpayments',
                    error_message=f"Payment not found: {webhook_data.payment_id}",
                    processed=False
                )
            
            # Store original status
            original_status = payment.status
            actions_taken = []
            
            # Convert NowPayments status to universal status
            new_status = webhook_data.to_universal_status()
            
            # Process status change
            def process_webhook_transaction():
                nonlocal actions_taken
                
                if new_status == 'completed' and original_status != 'completed':
                    # Mark payment as completed
                    success = payment.mark_completed(
                        actual_amount_usd=float(webhook_data.actually_paid) if webhook_data.actually_paid else None,
                        transaction_hash=webhook_data.txn_id
                    )
                    
                    if success:
                        actions_taken.append("payment_completed")
                        
                        # Add funds to user balance
                        balance_result = self.balance_service.add_funds(
                            user_id=payment.user_id,
                            amount=payment.amount_usd,
                            description=f"Payment completed: {payment.id}",
                            payment_id=str(payment.id)
                        )
                        
                        if balance_result.success:
                            actions_taken.append("balance_updated")
                        else:
                            self.logger.error("Failed to update balance", extra={
                                'payment_id': str(payment.id),
                                'user_id': payment.user_id,
                                'error': balance_result.message
                            })
                
                elif new_status == 'failed' and original_status not in ['failed', 'cancelled']:
                    # Mark payment as failed
                    success = payment.mark_failed(
                        reason=f"Provider status: {webhook_data.payment_status}",
                        error_code=webhook_data.payment_status
                    )
                    
                    if success:
                        actions_taken.append("payment_failed")
                
                elif new_status == 'expired' and original_status not in ['failed', 'cancelled', 'expired']:
                    # Mark payment as failed due to expiration
                    success = payment.mark_failed(
                        reason="Payment expired",
                        error_code="expired"
                    )
                    
                    if success:
                        actions_taken.append("payment_expired")
                
                # Update provider-specific fields
                if webhook_data.txn_id and not payment.transaction_hash:
                    payment.transaction_hash = webhook_data.txn_id
                    payment.save(update_fields=['transaction_hash', 'updated_at'])
                    actions_taken.append("transaction_hash_updated")
                
                return True
            
            # Execute in transaction
            self._execute_with_transaction(process_webhook_transaction)
            
            # Refresh payment
            payment.refresh_from_db()
            
            self._log_operation(
                "process_nowpayments_webhook",
                True,
                payment_id=str(payment.id),
                provider_payment_id=webhook_data.payment_id,
                status_change=f"{original_status} -> {payment.status}",
                actions_taken=actions_taken
            )
            
            return WebhookProcessingResult(
                success=True,
                provider='nowpayments',
                payment_id=str(payment.id),
                status_before=original_status,
                status_after=payment.status,
                actions_taken=actions_taken,
                processed=True,
                balance_updated='balance_updated' in actions_taken
            )
            
        except Exception as e:
            error_result = self._handle_exception(
                "process_nowpayments_webhook", e,
                provider_payment_id=webhook_data.payment_id if 'webhook_data' in locals() else None
            )
            
            return WebhookProcessingResult(
                success=False,
                provider='nowpayments',
                error_message=error_result.message,
                processed=False
            )
    
    def get_webhook_stats(self, days: int = 30) -> ServiceOperationResult:
        """
        Get webhook processing statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            ServiceOperationResult: Webhook statistics
        """
        try:
            # This would typically query a webhook log table
            # For now, return basic stats from payments
            from datetime import timedelta
            
            since = timezone.now() - timedelta(days=days)
            
            # Count payments updated recently (proxy for webhook activity)
            recent_updates = UniversalPayment.objects.filter(
                updated_at__gte=since
            ).exclude(
                created_at=models.F('updated_at')  # Exclude newly created payments
            ).count()
            
            # Status distribution of recent updates
            status_distribution = UniversalPayment.objects.filter(
                updated_at__gte=since
            ).values('status').annotate(
                count=models.Count('id')
            ).order_by('-count')
            
            stats = {
                'period_days': days,
                'recent_payment_updates': recent_updates,
                'status_distribution': list(status_distribution),
                'generated_at': timezone.now().isoformat()
            }
            
            return self._create_success_result(
                f"Webhook statistics for {days} days",
                stats
            )
            
        except Exception as e:
            return self._handle_exception("get_webhook_stats", e)
    
    def health_check(self) -> ServiceOperationResult:
        """Perform webhook service health check."""
        try:
            # Check dependencies
            payment_health = self.payment_service.health_check()
            balance_health = self.balance_service.health_check()
            
            # Check recent webhook activity (payments with provider_payment_id)
            recent_webhooks = UniversalPayment.objects.filter(
                provider_payment_id__isnull=False,
                updated_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            stats = {
                'service_name': 'WebhookService',
                'payment_service_healthy': payment_health.success,
                'balance_service_healthy': balance_health.success,
                'recent_webhook_activity': recent_webhooks,
                'supported_providers': ['nowpayments']
            }
            
            overall_healthy = payment_health.success and balance_health.success
            
            if overall_healthy:
                return self._create_success_result(
                    "WebhookService is healthy",
                    stats
                )
            else:
                return self._create_error_result(
                    "WebhookService has dependency issues",
                    "dependency_unhealthy",
                    stats
                )
                
        except Exception as e:
            return self._handle_exception("health_check", e)
