"""django_grpc module — Exception hierarchy."""

from __future__ import annotations


class DjangoGrpcError(Exception):
    """Base exception for django_grpc module."""

    def __init__(
        self,
        message: str,
        *,
        suggestion: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.suggestion = suggestion
        self.original_error = original_error

    def __str__(self) -> str:
        base = super().__str__()
        if self.suggestion:
            return f"{base} — Hint: {self.suggestion}"
        return base


class DjangoGrpcConfigError(DjangoGrpcError):
    """Raised when the module is not configured correctly."""


class DjangoGrpcSyncError(DjangoGrpcError):
    """Raised when an optimistic lock retry limit is exceeded."""


__all__ = [
    "DjangoGrpcError",
    "DjangoGrpcConfigError",
    "DjangoGrpcSyncError",
]
