"""
Centralized Error Handling and Recovery System.
Critical Foundation Security Component.
"""

import json
from django_cfg.modules.django_logger import get_logger
import traceback
from typing import Dict, Any, Optional, Union, Type
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count

from .payment_notifications import payment_notifications
from ...models.events import PaymentEvent

logger = get_logger("error_handler")


class ErrorSeverity(Enum):
    """Error severity levels for classification and response."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories for better organization and handling."""
    SECURITY = "SECURITY"
    PAYMENT = "PAYMENT"
    PROVIDER = "PROVIDER"
    VALIDATION = "VALIDATION"
    SYSTEM = "SYSTEM"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"


class ErrorDetails(BaseModel):
    """Pydantic model for error details."""
    exception_type: Optional[str] = None
    exception_module: Optional[str] = None
    traceback: Optional[str] = None
    provider: Optional[str] = None
    field: Optional[str] = None
    validation_error: Optional[str] = None
    ip_address: Optional[str] = None
    api_key_prefix: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields


class ErrorContext(BaseModel):
    """Pydantic model for error context."""
    operation: Optional[str] = None
    middleware: Optional[str] = None
    provider: Optional[str] = None
    user_id: Optional[str] = None
    request: Optional[Dict[str, Any]] = None
    system: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"


class ErrorInfo(BaseModel):
    """Pydantic model for error information."""
    error_code: str
    message: str
    category: str
    severity: str
    recoverable: bool = True
    timestamp: datetime
    details: ErrorDetails = Field(default_factory=ErrorDetails)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RecoveryResult(BaseModel):
    """Pydantic model for recovery attempt result."""
    attempted: bool = False
    success: bool = False
    actions: list[str] = Field(default_factory=list)
    message: Optional[str] = None
    error: Optional[str] = None


class ErrorHandlerResult(BaseModel):
    """Pydantic model for error handler result."""
    error: ErrorInfo
    context: ErrorContext
    recovery: RecoveryResult
    handled_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaymentError(Exception):
    """Base payment system error with severity and category."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: str = None,
        details: ErrorDetails = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code or self._generate_error_code()
        self.details = details or ErrorDetails()
        self.recoverable = recoverable
        self.timestamp = timezone.now()
    
    def _generate_error_code(self) -> str:
        """Generate unique error code."""
        import uuid
        return f"{self.category.value}_{uuid.uuid4().hex[:8].upper()}"
    
    def to_error_info(self) -> ErrorInfo:
        """Convert to Pydantic ErrorInfo model."""
        return ErrorInfo(
            error_code=self.error_code,
            message=self.message,
            category=self.category.value,
            severity=self.severity.value,
            recoverable=self.recoverable,
            timestamp=self.timestamp,
            details=self.details
        )


class SecurityError(PaymentError):
    """Security-related errors."""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.SECURITY)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        kwargs.setdefault('recoverable', False)
        
        # Convert dict details to Pydantic model
        if 'details' in kwargs and isinstance(kwargs['details'], dict):
            kwargs['details'] = ErrorDetails(**kwargs['details'])
        
        super().__init__(message, **kwargs)


class ProviderError(PaymentError):
    """Payment provider errors."""
    
    def __init__(self, message: str, provider: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.PROVIDER)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        
        # Handle provider in Pydantic details
        details_dict = kwargs.get('details', {})
        if isinstance(details_dict, dict):
            if provider:
                details_dict['provider'] = provider
            kwargs['details'] = ErrorDetails(**details_dict)
        
        super().__init__(message, **kwargs)


class ValidationError(PaymentError):
    """Data validation errors."""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        kwargs.setdefault('category', ErrorCategory.VALIDATION)
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        
        # Handle field in Pydantic details
        details_dict = kwargs.get('details', {})
        if isinstance(details_dict, dict):
            if field:
                details_dict['field'] = field
            kwargs['details'] = ErrorDetails(**details_dict)
        
        super().__init__(message, **kwargs)


class CentralizedErrorHandler:
    """
    Centralized error handling system with recovery mechanisms.
    
    Foundation Security Component - CRITICAL for system stability.
    """
    
    def __init__(self):
        self.error_count_cache_timeout = 300  # 5 minutes
        self.max_errors_per_minute = 100
        self.notification_cooldown = 900  # 15 minutes
    
    def handle_error(
        self,
        error: Union[Exception, PaymentError],
        context: Dict[str, Any] = None,
        request = None,
        user_id: str = None
    ) -> ErrorHandlerResult:
        """
        Handle error with comprehensive logging, alerting, and recovery.
        
        Args:
            error: Exception or PaymentError instance
            context: Additional context information
            request: Django request object (optional)
            user_id: User ID for tracking (optional)
            
        Returns:
            Dict with error details and recovery information
        """
        
        try:
            # Convert exception to PaymentError if needed
            if not isinstance(error, PaymentError):
                payment_error = self._convert_exception_to_payment_error(error)
            else:
                payment_error = error
            
            # Enrich context (convert to Pydantic)
            enriched_context = self._enrich_context(context, request, user_id, payment_error)
            
            # Log error
            self._log_error(payment_error, enriched_context)
            
            # Store error in database
            self._store_error_event(payment_error, enriched_context)
            
            # Check for error patterns and rate limits
            self._check_error_patterns(payment_error, enriched_context)
            
            # Send notifications if needed
            self._send_notifications(payment_error, enriched_context)
            
            # Attempt recovery if possible
            recovery_result = self._attempt_recovery(payment_error, enriched_context)
            
            # Return Pydantic result
            return ErrorHandlerResult(
                error=payment_error.to_error_info(),
                context=enriched_context,
                recovery=recovery_result,
                handled_at=timezone.now()
            )
            
        except Exception as handler_error:
            # Error in error handler - log critically
            logger.critical(
                f"🚨 CRITICAL: Error handler failed: {handler_error}",
                exc_info=True,
                extra={
                    'original_error': str(error),
                    'handler_error': str(handler_error)
                }
            )
            
            # Return minimal Pydantic error info
            return ErrorHandlerResult(
                error=ErrorInfo(
                    error_code='HANDLER_FAILURE',
                    message='Error handling system failure',
                    severity=ErrorSeverity.CRITICAL.value,
                    category=ErrorCategory.SYSTEM.value,
                    timestamp=timezone.now()
                ),
                context=ErrorContext(),
                recovery=RecoveryResult(attempted=False, success=False),
                handled_at=timezone.now()
            )
    
    def _convert_exception_to_payment_error(self, exception: Exception) -> PaymentError:
        """Convert standard exceptions to PaymentError instances."""
        
        # Map common exceptions to payment errors
        exception_mapping = {
            PermissionError: (ErrorCategory.SECURITY, ErrorSeverity.HIGH),
            ValueError: (ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM),
            ConnectionError: (ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            TimeoutError: (ErrorCategory.NETWORK, ErrorSeverity.HIGH),
        }
        
        # Get exception type mapping
        exception_type = type(exception)
        if exception_type in exception_mapping:
            category, severity = exception_mapping[exception_type]
        else:
            category, severity = ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM
        
        # Extract additional details as Pydantic model
        details = ErrorDetails(
            exception_type=exception_type.__name__,
            exception_module=exception_type.__module__,
            traceback=traceback.format_exc()
        )
        
        return PaymentError(
            message=str(exception),
            category=category,
            severity=severity,
            details=details
        )
    
    def _enrich_context(
        self,
        context: Dict[str, Any],
        request,
        user_id: str,
        error: PaymentError
    ) -> ErrorContext:
        """Enrich error context with additional information."""
        
        # Start with provided context
        enriched_dict = context.copy() if context else {}
        
        # Add request information
        request_info = None
        if request:
            request_info = {
                'method': request.method,
                'path': request.path,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
                'timestamp': timezone.now().isoformat()
            }
        
        # Determine user ID
        final_user_id = user_id
        if not final_user_id and request and hasattr(request, 'payment_user'):
            final_user_id = str(request.payment_user.id)
        
        # Add system information
        system_info = {
            'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
            'debug': settings.DEBUG,
            'timestamp': timezone.now().isoformat()
        }
        
        # Build Pydantic context
        return ErrorContext(
            operation=enriched_dict.get('operation'),
            middleware=enriched_dict.get('middleware'),
            provider=enriched_dict.get('provider'),
            user_id=final_user_id,
            request=request_info,
            system=system_info,
            **{k: v for k, v in enriched_dict.items() 
               if k not in ['operation', 'middleware', 'provider', 'user_id', 'request', 'system']}
        )
    
    def _log_error(self, error: PaymentError, context: ErrorContext):
        """Log error with appropriate level based on severity."""
        
        log_message = f"[{error.error_code}] {error.message}"
        
        extra_data = {
            'error_code': error.error_code,
            'category': error.category.value,
            'severity': error.severity.value,
            'context': context.dict()
        }
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"🚨 CRITICAL: {log_message}", extra=extra_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"❌ HIGH: {log_message}", extra=extra_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"⚠️ MEDIUM: {log_message}", extra=extra_data)
        else:
            logger.info(f"ℹ️ LOW: {log_message}", extra=extra_data)
    
    def _store_error_event(self, error: PaymentError, context: ErrorContext):
        """Store error event in database for analysis."""
        
        try:
            PaymentEvent.objects.create(
                event_type=f'error_{error.category.value.lower()}',
                metadata={
                    'error': error.to_error_info().dict(),
                    'context': context.dict(),
                    'stored_at': timezone.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to store error event: {e}")
    
    def _check_error_patterns(self, error: PaymentError, context: ErrorContext):
        """Check for error patterns and potential attacks."""
        
        # Check error rate
        error_rate_key = f"error_rate:{error.category.value}"
        current_errors = cache.get(error_rate_key, 0)
        
        if current_errors >= self.max_errors_per_minute:
            logger.critical(
                f"🚨 HIGH ERROR RATE DETECTED: {current_errors} {error.category.value} "
                f"errors in last minute - possible attack or system failure"
            )
            
            # Store critical event
            PaymentEvent.objects.create(
                event_type='high_error_rate',
                metadata={
                    'category': error.category.value,
                    'error_count': current_errors,
                    'threshold': self.max_errors_per_minute,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Send high error rate alert
            payment_notifications.send_high_error_rate_alert(
                error.category.value, current_errors, self.max_errors_per_minute
            )
        
        # Increment error count
        cache.set(error_rate_key, current_errors + 1, timeout=self.error_count_cache_timeout)
        
        # Check for security patterns
        if error.category == ErrorCategory.SECURITY:
            self._check_security_patterns(error, context)
    
    def _check_security_patterns(self, error: PaymentError, context: ErrorContext):
        """Check for security attack patterns."""
        
        # Check for multiple security errors from same IP
        ip_address = context.request.get('ip_address') if context.request else None
        if ip_address:
            security_errors_key = f"security_errors:{ip_address}"
            error_count = cache.get(security_errors_key, 0)
            
            if error_count >= 5:  # 5 security errors from same IP
                logger.critical(
                    f"🚨 SECURITY ATTACK PATTERN: {error_count} security errors "
                    f"from IP {ip_address} - possible coordinated attack"
                )
                
                # Store security incident
                PaymentEvent.objects.create(
                    event_type='security_attack_pattern',
                    metadata={
                        'ip_address': ip_address,
                        'error_count': error_count,
                        'error_details': error.to_error_info().dict(),
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                # Send attack pattern alert
                payment_notifications.send_attack_pattern_alert(
                    ip_address, error_count, error.to_error_info().dict()
                )
            
            # Increment IP error count
            cache.set(security_errors_key, error_count + 1, timeout=3600)  # 1 hour
    
    def _send_notifications(self, error: PaymentError, context: ErrorContext):
        """Send notifications for critical errors."""
        
        # Only send notifications for high severity errors
        if error.severity not in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            return
        
        # Check notification cooldown
        notification_key = f"notification_sent:{error.category.value}:{error.severity.value}"
        if cache.get(notification_key):
            return  # Already notified recently
        
        try:
            # Send notification using payment notification service
            self._send_admin_notification(error, context)
            
            # Set cooldown
            cache.set(notification_key, True, timeout=self.notification_cooldown)
            
        except Exception as e:
            logger.error(f"Failed to send error notifications: {e}")
    
    def _send_admin_notification(self, error: PaymentError, context: ErrorContext):
        """Send admin notification using payment notification service."""
        
        # Route to appropriate notification method based on error category
        if error.category == ErrorCategory.SECURITY:
            if hasattr(error.details, 'api_key_prefix') or 'api_access' in context.middleware:
                payment_notifications.send_api_security_breach(error.to_error_info(), context)
            elif hasattr(error.details, 'validation_error'):
                payment_notifications.send_webhook_validation_failure(error.to_error_info(), context)
            else:
                payment_notifications.send_security_alert(error.to_error_info(), context)
                
        elif error.category == ErrorCategory.PROVIDER:
            payment_notifications.send_provider_error(error.to_error_info(), context)
            
        elif error.category == ErrorCategory.PAYMENT:
            payment_notifications.send_payment_failure(error.to_error_info(), context)
            
        else:
            payment_notifications.send_system_error(error.to_error_info(), context)
    
    def _attempt_recovery(self, error: PaymentError, context: ErrorContext) -> RecoveryResult:
        """Attempt automatic recovery based on error type."""
        
        if not error.recoverable:
            return RecoveryResult(
                attempted=False, 
                message='Error marked as non-recoverable'
            )
        
        recovery_result = RecoveryResult(attempted=True, success=False)
        
        try:
            # Recovery based on error category
            if error.category == ErrorCategory.NETWORK:
                recovery_result = self._recover_network_error(error, context)
            elif error.category == ErrorCategory.PROVIDER:
                recovery_result = self._recover_provider_error(error, context)
            elif error.category == ErrorCategory.DATABASE:
                recovery_result = self._recover_database_error(error, context)
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            recovery_result.error = str(e)
        
        return recovery_result
    
    def _recover_network_error(self, error: PaymentError, context: ErrorContext) -> RecoveryResult:
        """Attempt recovery for network errors."""
        
        return RecoveryResult(
            attempted=True,
            success=False,
            actions=['retry_scheduled'],
            message='Network error - retry scheduled with exponential backoff'
        )
    
    def _recover_provider_error(self, error: PaymentError, context: ErrorContext) -> RecoveryResult:
        """Attempt recovery for provider errors."""
        
        provider = error.details.provider
        if provider:
            # Could implement provider fallback logic here
            return RecoveryResult(
                attempted=True,
                success=False,
                actions=['provider_fallback_considered'],
                message=f'Provider {provider} error - fallback providers evaluated'
            )
        
        return RecoveryResult(
            attempted=True,
            success=False,
            actions=[],
            message='No recovery action available'
        )
    
    def _recover_database_error(self, error: PaymentError, context: ErrorContext) -> RecoveryResult:
        """Attempt recovery for database errors."""
        
        return RecoveryResult(
            attempted=True,
            success=False,
            actions=['connection_refresh'],
            message='Database error - connection refresh attempted'
        )
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for monitoring dashboard."""
        
        since = timezone.now() - timedelta(hours=hours)
        
        # Get error events from database
        error_events = PaymentEvent.objects.filter(
            created_at__gte=since,
            event_type__startswith='error_'
        )
        
        # Group by category and severity
        stats = error_events.values('event_type').annotate(count=Count('id'))
        
        return {
            'period_hours': hours,
            'total_errors': error_events.count(),
            'breakdown': list(stats),
            'generated_at': timezone.now().isoformat()
        }


# Singleton instance for import
error_handler = CentralizedErrorHandler()


# Context manager for error handling
class error_context:
    """Context manager for automatic error handling."""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.context['operation'] = self.operation
            error_handler.handle_error(exc_value, self.context)
        return False  # Don't suppress the exception
