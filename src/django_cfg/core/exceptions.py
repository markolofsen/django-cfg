"""
Custom exceptions for django_cfg module.

Following CRITICAL_REQUIREMENTS.md - proper exception handling with specific types.
No exception suppression, all errors must be properly typed and handled.
"""

from typing import Optional, Dict, Any, List


class DjangoCfgException(Exception):
    """
    Base exception for all django_cfg related errors.
    
    All django_cfg exceptions inherit from this base class to allow
    for specific exception handling patterns.
    """
    
    def __init__(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ) -> None:
        """
        Initialize exception with detailed context.
        
        Args:
            message: Human-readable error message
            context: Additional context information for debugging
            suggestions: List of suggested fixes or actions
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        """Return formatted error message with context."""
        parts = [self.message]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.suggestions:
            suggestions_str = "; ".join(self.suggestions)
            parts.append(f"Suggestions: {suggestions_str}")
        
        return " | ".join(parts)


class ConfigurationError(DjangoCfgException):
    """
    Raised when configuration is invalid or incomplete.
    
    This exception is raised when:
    - Required configuration fields are missing
    - Configuration values are invalid
    - Configuration conflicts are detected
    - Environment-specific configuration issues
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration error.
        
        Args:
            message: Error description
            field_name: Name of the configuration field causing the error
            field_value: Value that caused the error
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if field_name is not None:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = field_value
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.field_name = field_name
        self.field_value = field_value


class ValidationError(DjangoCfgException):
    """
    Raised when Pydantic model validation fails.
    
    This exception is raised when:
    - Pydantic model validation fails
    - Type validation errors occur
    - Field constraint violations
    - Custom validation logic fails
    """
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> None:
        """
        Initialize validation error.
        
        Args:
            message: Error description
            model_name: Name of the Pydantic model that failed validation
            validation_errors: List of Pydantic validation errors
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if model_name is not None:
            context['model_name'] = model_name
        if validation_errors is not None:
            context['validation_errors'] = validation_errors
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.model_name = model_name
        self.validation_errors = validation_errors or []


class EnvironmentError(DjangoCfgException):
    """
    Raised when environment detection or configuration fails.
    
    This exception is raised when:
    - Environment cannot be detected
    - Environment-specific configuration is missing
    - Environment configuration conflicts
    - YAML configuration file issues
    """
    
    def __init__(
        self,
        message: str,
        environment: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize environment error.
        
        Args:
            message: Error description
            environment: Environment name that caused the error
            config_file: Configuration file that caused the error
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if environment is not None:
            context['environment'] = environment
        if config_file is not None:
            context['config_file'] = config_file
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.environment = environment
        self.config_file = config_file


class IntegrationError(DjangoCfgException):
    """
    Raised when third-party integration fails.
    
    This exception is raised when:
    - Django REST Framework integration issues
    - Revolution API zone configuration problems
    - Unfold dashboard configuration errors
    - Other third-party package integration failures
    """
    
    def __init__(
        self,
        message: str,
        integration_name: Optional[str] = None,
        package_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize integration error.
        
        Args:
            message: Error description
            integration_name: Name of the integration that failed
            package_name: Name of the third-party package
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if integration_name is not None:
            context['integration_name'] = integration_name
        if package_name is not None:
            context['package_name'] = package_name
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.integration_name = integration_name
        self.package_name = package_name


class DatabaseError(DjangoCfgException):
    """
    Raised when database configuration or connection issues occur.
    
    This exception is raised when:
    - Database connection configuration is invalid
    - Database routing rules conflict
    - Database connection testing fails
    - Multi-database setup issues
    """
    
    def __init__(
        self,
        message: str,
        database_alias: Optional[str] = None,
        connection_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """
        Initialize database error.
        
        Args:
            message: Error description
            database_alias: Database alias that caused the error
            connection_params: Database connection parameters
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if database_alias is not None:
            context['database_alias'] = database_alias
        if connection_params is not None:
            context['connection_params'] = connection_params
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.database_alias = database_alias
        self.connection_params = connection_params


class CacheError(DjangoCfgException):
    """
    Raised when cache configuration or connection issues occur.
    
    This exception is raised when:
    - Cache backend configuration is invalid
    - Redis connection issues
    - Cache backend selection problems
    - Cache key or timeout configuration errors
    """
    
    def __init__(
        self,
        message: str,
        cache_alias: Optional[str] = None,
        backend_type: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize cache error.
        
        Args:
            message: Error description
            cache_alias: Cache alias that caused the error
            backend_type: Cache backend type (redis, memory, etc.)
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if cache_alias is not None:
            context['cache_alias'] = cache_alias
        if backend_type is not None:
            context['backend_type'] = backend_type
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.cache_alias = cache_alias
        self.backend_type = backend_type


class SecurityError(DjangoCfgException):
    """
    Raised when security configuration issues occur.
    
    This exception is raised when:
    - Security settings are insufficient for production
    - CORS configuration conflicts
    - SSL/TLS configuration problems
    - Security domain validation failures
    """
    
    def __init__(
        self,
        message: str,
        security_setting: Optional[str] = None,
        severity: str = "medium",
        **kwargs
    ) -> None:
        """
        Initialize security error.
        
        Args:
            message: Error description
            security_setting: Security setting that caused the error
            severity: Error severity (low, medium, high, critical)
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get('context', {})
        if security_setting is not None:
            context['security_setting'] = security_setting
        context['severity'] = severity
        
        kwargs['context'] = context
        super().__init__(message, **kwargs)
        
        self.security_setting = security_setting
        self.severity = severity


# Exception hierarchy for easy catching
__all__ = [
    "DjangoCfgException",
    "ConfigurationError", 
    "ValidationError",
    "EnvironmentError",
    "IntegrationError",
    "DatabaseError",
    "CacheError",
    "SecurityError",
]
