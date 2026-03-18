"""
django_grpc.services.interceptors.errors — Error handling interceptor.

Catches exceptions and converts them to appropriate gRPC status codes.
Uses grpc.aio.ServerInterceptor so it works correctly in async servers
and does NOT wrap request_iterator (no streaming buffer overhead).
"""

from __future__ import annotations

import logging
from typing import Any, Callable

import grpc
import grpc.aio
try:
    from grpc._cython.cygrpc import AbortError as _AbortError
except ImportError:
    _AbortError = None  # type: ignore[assignment,misc]
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.db import OperationalError

logger = logging.getLogger(__name__)

# Maps exception types to (grpc.StatusCode, message_template) pairs.
_ERROR_MAPPINGS: dict[type[Exception], tuple[grpc.StatusCode, str]] = {
    DjangoValidationError: (grpc.StatusCode.INVALID_ARGUMENT, "Validation error: {message}"),
    ObjectDoesNotExist:    (grpc.StatusCode.NOT_FOUND,         "Object not found: {message}"),
    PermissionDenied:      (grpc.StatusCode.PERMISSION_DENIED, "Permission denied: {message}"),
    OperationalError:      (grpc.StatusCode.UNAVAILABLE,       "Database temporarily unavailable. Please retry."),
    ValueError:            (grpc.StatusCode.INVALID_ARGUMENT,  "Invalid value: {message}"),
    KeyError:              (grpc.StatusCode.INVALID_ARGUMENT,  "Missing required field: {message}"),
    NotImplementedError:   (grpc.StatusCode.UNIMPLEMENTED,     "Not implemented: {message}"),
    TimeoutError:          (grpc.StatusCode.DEADLINE_EXCEEDED, "Operation timed out: {message}"),
}


def _resolve_error(error: Exception) -> tuple[grpc.StatusCode, str] | None:
    """Return (status_code, formatted_message) for the given exception.

    Returns None if the error is already a gRPC error — callers must re-raise
    it directly so context.abort() is not called (gRPC runtime handles it).

    R-12 fix: previously raised grpc.RpcError from inside the interceptor's
    except-block which created a chained exception and bypassed context.abort(),
    leaving the stream in an inconsistent state. Now returns None so the caller
    can `raise` cleanly with `raise from None`.
    """
    if isinstance(error, grpc.RpcError):
        return None  # caller will re-raise directly

    # AbortError is raised by context.abort() in grpc.aio handlers.
    # It does NOT inherit from grpc.RpcError, but calling abort() again
    # causes UsageError("Abort already called!"). Must re-raise as-is.
    if _AbortError is not None and isinstance(error, _AbortError):
        return None

    for exc_type, (code, template) in _ERROR_MAPPINGS.items():
        if isinstance(error, exc_type):
            return code, template.format(message=str(error) or type(error).__name__)

    logger.error(
        "[gRPC Error] %s: %s", type(error).__name__, error, exc_info=True
    )
    return grpc.StatusCode.INTERNAL, f"Internal server error: {error}"


class ErrorHandlingInterceptor(grpc.aio.ServerInterceptor):
    """
    async gRPC interceptor that converts Python exceptions to gRPC status codes.

    Implemented as grpc.aio.ServerInterceptor so it works correctly in
    grpc.aio servers and does NOT wrap request_iterator — zero streaming
    buffer overhead. Satisfies the max-2-interceptors constraint.

    Error Mapping:
        ValidationError          → INVALID_ARGUMENT
        ObjectDoesNotExist       → NOT_FOUND
        PermissionDenied         → PERMISSION_DENIED
        OperationalError         → UNAVAILABLE
        ValueError / KeyError    → INVALID_ARGUMENT
        NotImplementedError      → UNIMPLEMENTED
        TimeoutError             → DEADLINE_EXCEEDED
        Exception (all others)   → INTERNAL
    """

    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Any],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """Wrap each handler type in a try/except that maps exceptions to gRPC codes."""
        from .wrapped_handler import WrappedHandler

        handler = await continuation(handler_call_details)  # type: ignore[misc]
        if handler is None:
            return None  # type: ignore[return-value]

        method_name = getattr(handler_call_details, "method", "unknown")

        if handler.unary_unary:
            async def _unary_unary(request: Any, context: grpc.aio.ServicerContext) -> Any:
                try:
                    return await handler.unary_unary(request, context)
                except Exception as exc:
                    # R-12: _resolve_error returns None for grpc.RpcError —
                    # re-raise directly so gRPC runtime handles it and
                    # context.abort() is NOT called (would double-abort).
                    resolved = _resolve_error(exc)
                    if resolved is None:
                        raise
                    code, msg = resolved
                    logger.warning("[gRPC] %s %s: %s", method_name, code.name, msg)
                    await context.abort(code, msg)

            return WrappedHandler(handler, unary_unary=_unary_unary)  # type: ignore[return-value]

        if handler.unary_stream:
            async def _unary_stream(request: Any, context: grpc.aio.ServicerContext) -> Any:
                try:
                    async for item in handler.unary_stream(request, context):
                        yield item
                except Exception as exc:
                    resolved = _resolve_error(exc)
                    if resolved is None:
                        raise
                    code, msg = resolved
                    logger.warning("[gRPC] %s %s: %s", method_name, code.name, msg)
                    await context.abort(code, msg)

            return WrappedHandler(handler, unary_stream=_unary_stream)  # type: ignore[return-value]

        if handler.stream_unary:
            async def _stream_unary(request_iterator: Any, context: grpc.aio.ServicerContext) -> Any:
                try:
                    return await handler.stream_unary(request_iterator, context)
                except Exception as exc:
                    resolved = _resolve_error(exc)
                    if resolved is None:
                        raise
                    code, msg = resolved
                    logger.warning("[gRPC] %s %s: %s", method_name, code.name, msg)
                    await context.abort(code, msg)

            return WrappedHandler(handler, stream_unary=_stream_unary)  # type: ignore[return-value]

        if handler.stream_stream:
            async def _stream_stream(request_iterator: Any, context: grpc.aio.ServicerContext) -> Any:
                try:
                    async for item in handler.stream_stream(request_iterator, context):
                        yield item
                except Exception as exc:
                    resolved = _resolve_error(exc)
                    if resolved is None:
                        raise
                    code, msg = resolved
                    logger.warning("[gRPC] %s %s: %s", method_name, code.name, msg)
                    await context.abort(code, msg)

            return WrappedHandler(handler, stream_stream=_stream_stream)  # type: ignore[return-value]

        return handler


__all__ = ["ErrorHandlingInterceptor"]
