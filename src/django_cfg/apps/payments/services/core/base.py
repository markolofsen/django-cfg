"""
Base service class for the Universal Payment System v2.0.

Provides common functionality for all services.
"""

from abc import ABC
from typing import Optional, Dict, Any, Type
from django.db import transaction
from django_cfg.modules.django_logger import get_logger
from ..types import ServiceOperationResult


class BaseService(ABC):
    """
    Base service class with common functionality.
    
    Provides logging, error handling, and transaction management.
    """
    
    def __init__(self):
        """Initialize base service."""
        self.logger = get_logger(f"services.{self.__class__.__name__.lower()}")
        self._cache = {}
        
        # Initialize config service
        from ...config.constance import get_payment_config_service
        self.config_service = get_payment_config_service()
    
    def _create_success_result(
        self, 
        message: str = "Operation completed successfully",
        data: Optional[Dict[str, Any]] = None
    ) -> ServiceOperationResult:
        """Create success result."""
        return ServiceOperationResult(
            success=True,
            message=message,
            data=data or {}
        )
    
    def _create_error_result(
        self,
        message: str,
        error_code: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> ServiceOperationResult:
        """Create error result."""
        return ServiceOperationResult(
            success=False,
            message=message,
            error_code=error_code,
            data=data or {}
        )
    
    def _log_operation(
        self,
        operation: str,
        success: bool,
        **kwargs
    ) -> None:
        """Log service operation."""
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'success': success,
            **kwargs
        }
        
        if success:
            self.logger.info(f"Operation {operation} completed successfully", extra=log_data)
        else:
            self.logger.error(f"Operation {operation} failed", extra=log_data)
    
    def _handle_exception(
        self,
        operation: str,
        exception: Exception,
        **context
    ) -> ServiceOperationResult:
        """Handle service exception."""
        error_message = f"Service error in {operation}: {str(exception)}"
        
        self.logger.error(error_message, extra={
            'service': self.__class__.__name__,
            'operation': operation,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            **context
        }, exc_info=True)
        
        return self._create_error_result(
            message=error_message,
            error_code=type(exception).__name__.lower(),
            data={'context': context}
        )
    
    @transaction.atomic
    def _execute_with_transaction(self, operation_func, *args, **kwargs):
        """Execute operation within database transaction."""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Transaction rolled back due to error: {e}")
            raise
    
    def _validate_input(self, data: Any, model_class: Type) -> Any:
        """Validate input data using Pydantic model."""
        try:
            if isinstance(data, dict):
                return model_class(**data)
            elif isinstance(data, model_class):
                return data
            else:
                return model_class.model_validate(data)
        except Exception as e:
            raise ValueError(f"Invalid input data: {e}")
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key."""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)
    
    def _cache_set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache."""
        # Simple in-memory cache for now
        # In production, this would use Redis
        self._cache[key] = value
    
    def _cache_delete(self, key: str) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)
    
    def _cache_clear(self, prefix: Optional[str] = None) -> None:
        """Clear cache entries."""
        if prefix:
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
        else:
            self._cache.clear()
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            'service_name': self.__class__.__name__,
            'cache_size': len(self._cache),
            'cache_keys': list(self._cache.keys())
        }
    
    def health_check(self) -> ServiceOperationResult:
        """Perform service health check."""
        try:
            # Basic health check - can be overridden by subclasses
            stats = self.get_service_stats()
            
            return self._create_success_result(
                message=f"{self.__class__.__name__} is healthy",
                data=stats
            )
        except Exception as e:
            return self._handle_exception("health_check", e)
