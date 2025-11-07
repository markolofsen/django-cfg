"""
Connection Pool Cleanup Middleware.

Ensures database connections are properly returned to the pool after each
request, including error cases. Prevents connection leaks in production.

Usage:
    Add to MIDDLEWARE in settings.py:
    MIDDLEWARE = [
        # ... other middleware ...
        'django_cfg.middleware.pool_cleanup.ConnectionPoolCleanupMiddleware',
    ]

Note:
    This middleware should be placed AFTER all other middleware to ensure
    cleanup happens regardless of what other middleware does.
"""

import logging
import time
from typing import Callable

from django.db import connection, connections, transaction
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django_cfg.middleware.pool_cleanup')


class ConnectionPoolCleanupMiddleware(MiddlewareMixin):
    """
    Middleware to ensure database connections are cleaned up after each request.

    Features:
    - Closes connections after successful responses
    - Closes connections after exceptions
    - Rolls back uncommitted transactions on errors
    - Works with both sync and async views
    - Minimal performance overhead (<1ms)

    This middleware is critical when using connection pooling with
    ATOMIC_REQUESTS=False, as it ensures connections don't leak.
    """

    def __init__(self, get_response: Callable):
        """
        Initialize middleware.

        Args:
            get_response: The next middleware or view to call
        """
        super().__init__(get_response)
        self.get_response = get_response
        self._enable_logging = False  # Set to True for debug logging

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request through middleware chain.

        Args:
            request: The HTTP request

        Returns:
            HttpResponse from view or next middleware
        """
        start_time = time.time() if self._enable_logging else None

        try:
            response = self.get_response(request)
            return response
        finally:
            # Cleanup happens in finally block to ensure it runs
            self._cleanup_connections(request, rollback_on_error=False)

            if self._enable_logging and start_time:
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(f"Pool cleanup overhead: {duration_ms:.2f}ms")

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process response before returning to client.

        Called after view execution for successful responses.

        Args:
            request: The HTTP request
            response: The HTTP response from view

        Returns:
            The HTTP response (unchanged)
        """
        # Cleanup handled in __call__ finally block
        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """
        Process exception raised during request handling.

        Called when view raises an exception. Rolls back any pending
        transactions and closes connections.

        Args:
            request: The HTTP request
            exception: The exception that was raised

        Returns:
            None (allows exception to propagate)
        """
        logger.warning(
            f"Exception in request, rolling back transactions: {exception.__class__.__name__}",
            extra={
                'path': request.path,
                'method': request.method,
                'exception': str(exception),
            }
        )

        # Rollback all open transactions
        self._cleanup_connections(request, rollback_on_error=True)

        # Return None to allow exception to propagate
        return None

    def _cleanup_connections(self, request: HttpRequest, rollback_on_error: bool = False) -> None:
        """
        Clean up all database connections.

        Args:
            request: The HTTP request
            rollback_on_error: If True, rollback uncommitted transactions
        """
        for db_alias in connections:
            try:
                conn = connections[db_alias]

                # Check if connection is open
                if conn.connection is None:
                    continue

                # Rollback uncommitted transactions if requested
                if rollback_on_error:
                    self._rollback_transaction(conn, db_alias)

                # Close the connection to return it to pool
                # Django's close() is safe to call multiple times
                conn.close()

            except Exception as e:
                logger.error(
                    f"Error cleaning up connection '{db_alias}': {e}",
                    exc_info=True,
                    extra={
                        'database': db_alias,
                        'path': request.path,
                    }
                )

    def _rollback_transaction(self, conn, db_alias: str) -> None:
        """
        Rollback any uncommitted transaction on a connection.

        Args:
            conn: Database connection
            db_alias: Database alias for logging
        """
        try:
            # Check if there's an open transaction
            if conn.in_atomic_block:
                logger.debug(f"Rolling back transaction for database '{db_alias}'")
                conn.rollback()
        except Exception as e:
            logger.error(
                f"Error rolling back transaction for '{db_alias}': {e}",
                exc_info=True
            )


class AsyncConnectionPoolCleanupMiddleware:
    """
    Async version of ConnectionPoolCleanupMiddleware.

    Use this middleware in ASGI deployments for better async compatibility.

    Usage:
        MIDDLEWARE = [
            'django_cfg.middleware.pool_cleanup.AsyncConnectionPoolCleanupMiddleware',
        ]
    """

    def __init__(self, get_response: Callable):
        """
        Initialize async middleware.

        Args:
            get_response: The next middleware or view to call
        """
        self.get_response = get_response
        self._enable_logging = False

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request through middleware chain (async).

        Args:
            request: The HTTP request

        Returns:
            HttpResponse from view or next middleware
        """
        start_time = time.time() if self._enable_logging else None

        try:
            response = await self.get_response(request)
            return response
        except Exception as e:
            # Rollback on exception
            logger.warning(
                f"Exception in async request, rolling back: {e.__class__.__name__}",
                extra={'path': request.path, 'exception': str(e)}
            )
            self._cleanup_connections(request, rollback_on_error=True)
            raise
        finally:
            # Always cleanup connections
            self._cleanup_connections(request, rollback_on_error=False)

            if self._enable_logging and start_time:
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(f"Async pool cleanup overhead: {duration_ms:.2f}ms")

    def _cleanup_connections(self, request: HttpRequest, rollback_on_error: bool = False) -> None:
        """
        Clean up all database connections (sync code in async middleware).

        Args:
            request: The HTTP request
            rollback_on_error: If True, rollback uncommitted transactions
        """
        for db_alias in connections:
            try:
                conn = connections[db_alias]

                if conn.connection is None:
                    continue

                if rollback_on_error and conn.in_atomic_block:
                    logger.debug(f"Rolling back async transaction for '{db_alias}'")
                    conn.rollback()

                conn.close()

            except Exception as e:
                logger.error(
                    f"Error cleaning up async connection '{db_alias}': {e}",
                    exc_info=True,
                    extra={'database': db_alias, 'path': request.path}
                )


# Default export - use sync middleware
__all__ = ['ConnectionPoolCleanupMiddleware', 'AsyncConnectionPoolCleanupMiddleware']
