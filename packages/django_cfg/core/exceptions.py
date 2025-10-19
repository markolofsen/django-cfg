"""
Django-CFG Core Exceptions

Custom exception classes for django-cfg with enhanced error context.
"""

from typing import Any, Dict, List, Optional


class DjangoCfgException(Exception):
    """
    Base exception for django-cfg with enhanced error reporting.

    Supports additional context and actionable suggestions.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        environment: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize exception with enhanced context.

        Args:
            message: Primary error message
            context: Additional context data
            suggestions: List of actionable suggestions
            environment: Environment where error occurred
            **kwargs: Additional metadata
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []
        self.environment = environment
        self.metadata = kwargs

    def __str__(self) -> str:
        """Format error message with context."""
        parts = [self.message]

        if self.suggestions:
            parts.append("\nSuggestions:")
            for suggestion in self.suggestions:
                parts.append(f"  - {suggestion}")

        if self.context:
            parts.append(f"\nContext: {self.context}")

        return "\n".join(parts)


class ConfigurationError(DjangoCfgException):
    """Raised when configuration is invalid or incomplete."""
    pass


class ValidationError(DjangoCfgException):
    """Raised when validation fails."""
    pass


class EnvironmentError(DjangoCfgException):
    """Raised when environment-related errors occur."""
    pass


class CacheError(DjangoCfgException):
    """Raised when cache configuration or operations fail."""
    pass


class DatabaseError(DjangoCfgException):
    """Raised when database configuration or connection issues occur."""
    pass


__all__ = [
    "DjangoCfgException",
    "ConfigurationError",
    "ValidationError",
    "EnvironmentError",
    "CacheError",
    "DatabaseError",
]
