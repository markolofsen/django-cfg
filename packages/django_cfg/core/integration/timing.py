"""
Timing utilities for tracking server startup and initialization times.

This module provides utilities to track timing information for Django and gRPC
server startup processes.
"""

import time
from typing import Optional


class ServerStartupTimer:
    """
    Track server startup timing information.

    Usage:
        timer = ServerStartupTimer()
        # ... server initialization ...
        elapsed = timer.elapsed()
        formatted = timer.format_elapsed()
    """

    def __init__(self):
        """Initialize timer with current timestamp."""
        self._start_time = time.time()

    def elapsed(self) -> float:
        """
        Get elapsed time in seconds.

        Returns:
            Elapsed time in seconds as a float
        """
        return time.time() - self._start_time

    def format_elapsed(self, decimals: int = 2) -> str:
        """
        Format elapsed time as a human-readable string.

        Args:
            decimals: Number of decimal places for seconds (default: 2)

        Returns:
            Formatted string like "1.23s" or "12.34s"
        """
        elapsed = self.elapsed()
        return f"{elapsed:.{decimals}f}s"

    def format_elapsed_detailed(self) -> str:
        """
        Format elapsed time with detailed breakdown.

        Returns:
            Formatted string like "1m 23.45s" or "2.34s"
        """
        elapsed = self.elapsed()

        if elapsed >= 60:
            # Show minutes and seconds
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            return f"{minutes}m {seconds:.2f}s"
        else:
            # Just seconds
            return f"{elapsed:.2f}s"


# Global startup timer for Django server
_django_startup_timer: Optional[ServerStartupTimer] = None

# Global startup timer for gRPC server
_grpc_startup_timer: Optional[ServerStartupTimer] = None


def start_django_timer() -> ServerStartupTimer:
    """
    Start tracking Django server startup time.

    Returns:
        ServerStartupTimer instance
    """
    global _django_startup_timer
    _django_startup_timer = ServerStartupTimer()
    return _django_startup_timer


def start_grpc_timer() -> ServerStartupTimer:
    """
    Start tracking gRPC server startup time.

    Returns:
        ServerStartupTimer instance
    """
    global _grpc_startup_timer
    _grpc_startup_timer = ServerStartupTimer()
    return _grpc_startup_timer


def get_django_timer() -> Optional[ServerStartupTimer]:
    """
    Get Django server startup timer.

    Returns:
        ServerStartupTimer instance or None if not started
    """
    return _django_startup_timer


def get_grpc_timer() -> Optional[ServerStartupTimer]:
    """
    Get gRPC server startup timer.

    Returns:
        ServerStartupTimer instance or None if not started
    """
    return _grpc_startup_timer


def get_django_startup_time() -> Optional[str]:
    """
    Get formatted Django server startup time.

    Returns:
        Formatted string like "1.23s" or None if timer not started
    """
    if _django_startup_timer:
        return _django_startup_timer.format_elapsed()
    return None


def get_grpc_startup_time() -> Optional[str]:
    """
    Get formatted gRPC server startup time.

    Returns:
        Formatted string like "1.23s" or None if timer not started
    """
    if _grpc_startup_timer:
        return _grpc_startup_timer.format_elapsed()
    return None


__all__ = [
    'ServerStartupTimer',
    'start_django_timer',
    'start_grpc_timer',
    'get_django_timer',
    'get_grpc_timer',
    'get_django_startup_time',
    'get_grpc_startup_time',
]
