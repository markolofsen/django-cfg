"""
Cloudflare Module Exception Classes.
"""

from typing import Any, Dict, Optional


class CloudflareError(Exception):
    """Base exception for all Cloudflare module errors."""

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        suggestion: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.suggestion = suggestion
        self.details = details or {}
        self.original_error = original_error
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.error_code:
            parts.insert(0, f"[{self.error_code}]")
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return " ".join(parts)


class CloudflareConfigError(CloudflareError):
    """Raised when configuration is missing or invalid."""

    def __init__(self, message: str, missing_fields: Optional[list[str]] = None) -> None:
        super().__init__(
            message,
            error_code="CF_CONFIG_ERROR",
            suggestion="Check your CloudflareConfig settings (account_id, api_token, d1_database_id)",
            details={"missing_fields": missing_fields or []},
        )


class CloudflareQueryError(CloudflareError):
    """Raised when a D1 query fails."""

    def __init__(self, message: str, sql: Optional[str] = None) -> None:
        super().__init__(
            message,
            error_code="CF_QUERY_ERROR",
            suggestion="Check the SQL statement and parameters",
            details={"sql": (sql or "")[:200]},
        )


class CloudflareSchemaError(CloudflareError):
    """Raised when schema migration fails."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            error_code="CF_SCHEMA_ERROR",
            suggestion="Check D1 database connectivity and permissions",
        )


__all__ = [
    "CloudflareError",
    "CloudflareConfigError",
    "CloudflareQueryError",
    "CloudflareSchemaError",
]
