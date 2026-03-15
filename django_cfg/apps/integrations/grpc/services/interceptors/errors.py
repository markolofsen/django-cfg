"""
Error Handling Interceptor for gRPC.

Catches exceptions and converts them to appropriate gRPC errors.
"""

from __future__ import annotations

import logging
from typing import Callable

import grpc
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.db import OperationalError

logger = logging.getLogger(__name__)


class ErrorHandlingInterceptor(grpc.ServerInterceptor):
    """
    gRPC interceptor for error handling.

    Features:
    - Catches Python exceptions
    - Converts to appropriate gRPC status codes
    - Logs errors with context
    - Provides user-friendly error messages
    - Supports custom error mappings

    Example:
        ```python
        # In Django settings
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.interceptors.ErrorHandlingInterceptor",
            ]
        }
        ```

    Error Mapping:
        - ValidationError → INVALID_ARGUMENT
        - ObjectDoesNotExist → NOT_FOUND
        - PermissionDenied → PERMISSION_DENIED
        - NotImplementedError → UNIMPLEMENTED
        - TimeoutError → DEADLINE_EXCEEDED
        - Exception → INTERNAL
    """

    def __init__(self):
        """Initialize error handling interceptor."""
        self.error_mappings = {
            # Django exceptions
            DjangoValidationError: (
                grpc.StatusCode.INVALID_ARGUMENT,
                "Validation error: {message}"
            ),
            ObjectDoesNotExist: (
                grpc.StatusCode.NOT_FOUND,
                "Object not found: {message}"
            ),
            PermissionDenied: (
                grpc.StatusCode.PERMISSION_DENIED,
                "Permission denied: {message}"
            ),
            # Database errors - server temporarily unavailable
            # Client should retry connection, NOT re-authenticate
            OperationalError: (
                grpc.StatusCode.UNAVAILABLE,
                "Database temporarily unavailable. Please retry."
            ),
            # Python built-in exceptions
            ValueError: (
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid value: {message}"
            ),
            KeyError: (
                grpc.StatusCode.INVALID_ARGUMENT,
                "Missing required field: {message}"
            ),
            NotImplementedError: (
                grpc.StatusCode.UNIMPLEMENTED,
                "Not implemented: {message}"
            ),
            TimeoutError: (
                grpc.StatusCode.DEADLINE_EXCEEDED,
                "Operation timed out: {message}"
            ),
        }

    def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC service call for error handling.

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler with error handling
        """
        method_name = handler_call_details.method

        # Get handler and wrap it
        handler = continuation(handler_call_details)

        if handler is None:
            return None

        # Wrap handler methods to catch errors
        return self._wrap_handler(handler, method_name)

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        method_name: str,
    ) -> grpc.RpcMethodHandler:
        """
        Wrap handler to catch and convert exceptions.

        Args:
            handler: Original RPC method handler
            method_name: gRPC method name

        Returns:
            Wrapped RPC method handler
        """
        def wrap_unary_unary(behavior):
            def wrapper(request, context):
                try:
                    return behavior(request, context)
                except Exception as e:
                    self._handle_error(e, context, method_name)
            return wrapper

        def wrap_unary_stream(behavior):
            def wrapper(request, context):
                try:
                    for response in behavior(request, context):
                        yield response
                except Exception as e:
                    self._handle_error(e, context, method_name)
            return wrapper

        def wrap_stream_unary(behavior):
            def wrapper(request_iterator, context):
                try:
                    return behavior(request_iterator, context)
                except Exception as e:
                    self._handle_error(e, context, method_name)
            return wrapper

        def wrap_stream_stream(behavior):
            def wrapper(request_iterator, context):
                try:
                    for response in behavior(request_iterator, context):
                        yield response
                except Exception as e:
                    self._handle_error(e, context, method_name)
            return wrapper

        # Return wrapped handler based on type
        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                wrap_unary_unary(handler.unary_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                wrap_unary_stream(handler.unary_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                wrap_stream_unary(handler.stream_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.stream_stream:
            return grpc.stream_stream_rpc_method_handler(
                wrap_stream_stream(handler.stream_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        else:
            return handler

    def _handle_error(self, error: Exception, context: grpc.ServicerContext, method_name: str):
        """
        Handle exception and abort with appropriate gRPC status.

        Args:
            error: The caught exception
            context: gRPC servicer context
            method_name: Name of the gRPC method
        """
        # Check if it's already a gRPC error
        if isinstance(error, grpc.RpcError):
            # Re-raise gRPC errors as-is
            raise error

        # Get error mapping
        error_type = type(error)
        status_code = grpc.StatusCode.INTERNAL
        message_template = "Internal server error: {message}"

        # Find matching error mapping
        for exc_type, (code, template) in self.error_mappings.items():
            if isinstance(error, exc_type):
                status_code = code
                message_template = template
                break

        # Format error message
        error_message = str(error) or error_type.__name__
        formatted_message = message_template.format(message=error_message)

        # Log error
        if status_code == grpc.StatusCode.INTERNAL:
            # Internal errors should be logged with full traceback
            logger.error(
                f"[gRPC Error] {method_name} | "
                f"status={status_code.name} | "
                f"error={error_type.__name__}: {error_message}",
                exc_info=True
            )
        else:
            # Expected errors can be logged at warning level
            logger.warning(
                f"[gRPC Error] {method_name} | "
                f"status={status_code.name} | "
                f"error={error_type.__name__}: {error_message}"
            )

        # Abort with gRPC error
        context.abort(status_code, formatted_message)


__all__ = ["ErrorHandlingInterceptor"]
