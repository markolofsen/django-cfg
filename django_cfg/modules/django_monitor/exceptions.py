"""django_monitor — Exception hierarchy."""

from __future__ import annotations


class MonitorError(Exception):
    """Base exception for django_monitor module."""

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


class MonitorConfigError(MonitorError):
    """Raised when the module is not configured correctly."""


class MonitorSyncError(MonitorError):
    """Raised when a D1 push operation fails."""


__all__ = [
    "MonitorError",
    "MonitorConfigError",
    "MonitorSyncError",
]
