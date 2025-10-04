"""
Logging Middleware for RPC

Automatically logs all RPC requests/responses with timing.
"""

import time
from typing import Any, Awaitable, Callable, Dict
from uuid import UUID

from .logger import RPCLogger


class LoggingMiddleware:
    """
    Middleware for automatic RPC logging.

    Wraps RPC handlers to automatically log:
    - Request parameters
    - Response data
    - Duration
    - Success/failure
    - Errors

    Example:
        >>> router = MessageRouter(connection_manager)
        >>> middleware = LoggingMiddleware(logger)
        >>>
        >>> @router.register("create_user")
        >>> async def create_user(conn, params):
        ...     return await middleware.wrap(
        ...         handler=create_user_impl,
        ...         method="create_user",
        ...         conn=conn,
        ...         params=params,
        ...     )
    """

    def __init__(self, logger: RPCLogger):
        """
        Initialize logging middleware.

        Args:
            logger: RPCLogger instance
        """
        self.logger = logger

    async def wrap_handler(
        self,
        handler: Callable,
        method: str,
        conn: Any,
        params: Dict[str, Any],
        correlation_id: str,
    ) -> Any:
        """
        Wrap RPC handler with logging.

        Args:
            handler: Handler function to wrap
            method: RPC method name
            conn: Connection context
            params: Request parameters
            correlation_id: Correlation ID

        Returns:
            Handler result

        Raises:
            Exception: Re-raises handler exceptions after logging
        """
        # Extract context
        user_id = getattr(conn, "user_id", None)
        connection_id = getattr(conn, "connection_id", None)

        # Log request
        self.logger.log_rpc_request(
            method=method,
            params=params,
            correlation_id=correlation_id,
            user_id=user_id,
            connection_id=connection_id,
        )

        # Execute handler with timing
        start_time = time.perf_counter()
        success = True
        error_code = None
        result = None

        try:
            result = await handler(conn, params)
            return result

        except Exception as e:
            success = False
            error_code = type(e).__name__

            # Log error
            self.logger.error(
                f"RPC handler error: {method}",
                exc_info=True,
                correlation_id=correlation_id,
                method=method,
                user_id=user_id,
                connection_id=str(connection_id) if connection_id else None,
            )

            raise

        finally:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log response
            self.logger.log_rpc_response(
                method=method,
                result=result,
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                success=success,
                error_code=error_code,
            )

    def create_wrapper(self, method: str):
        """
        Create a wrapper decorator for a specific method.

        Args:
            method: RPC method name

        Returns:
            Decorator function

        Example:
            >>> middleware = LoggingMiddleware(logger)
            >>>
            >>> @middleware.create_wrapper("create_user")
            >>> async def create_user_handler(conn, params):
            ...     # Handler implementation
            ...     return result
        """

        def decorator(handler: Callable) -> Callable:
            async def wrapped(conn, params):
                # Extract correlation_id from params or generate
                correlation_id = params.get("correlation_id", "unknown")

                return await self.wrap_handler(
                    handler=handler,
                    method=method,
                    conn=conn,
                    params=params,
                    correlation_id=correlation_id,
                )

            return wrapped

        return decorator


def auto_log_rpc(logger: RPCLogger):
    """
    Decorator factory for automatic RPC logging.

    Args:
        logger: RPCLogger instance

    Returns:
        Decorator function

    Example:
        >>> logger = RPCLogger(config)
        >>>
        >>> @auto_log_rpc(logger)
        >>> @router.register("create_user")
        >>> async def create_user(conn, params: CreateUserParams):
        ...     # Handler implementation
        ...     return UserResult(...)
    """

    def decorator(handler: Callable) -> Callable:
        async def wrapped(conn, params, *args, **kwargs):
            # Extract metadata
            method = kwargs.get("_method_name") or handler.__name__
            correlation_id = (
                getattr(params, "correlation_id", None)
                or kwargs.get("correlation_id")
                or "unknown"
            )
            user_id = getattr(conn, "user_id", None)
            connection_id = getattr(conn, "connection_id", None)

            # Log request
            params_dict = (
                params.model_dump() if hasattr(params, "model_dump") else params
            )
            logger.log_rpc_request(
                method=method,
                params=params_dict,
                correlation_id=correlation_id,
                user_id=user_id,
                connection_id=connection_id,
            )

            # Execute with timing
            start_time = time.perf_counter()
            success = True
            error_code = None
            result = None

            try:
                result = await handler(conn, params, *args, **kwargs)
                return result

            except Exception as e:
                success = False
                error_code = type(e).__name__

                logger.error(
                    f"Handler error: {method}",
                    exc_info=True,
                    correlation_id=correlation_id,
                    method=method,
                    user_id=user_id,
                )

                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000

                result_dict = (
                    result.model_dump() if hasattr(result, "model_dump") else result
                )
                logger.log_rpc_response(
                    method=method,
                    result=result_dict,
                    correlation_id=correlation_id,
                    duration_ms=duration_ms,
                    success=success,
                    error_code=error_code,
                )

        return wrapped

    return decorator


__all__ = [
    "LoggingMiddleware",
    "auto_log_rpc",
]
