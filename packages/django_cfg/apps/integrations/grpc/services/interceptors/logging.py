"""
Async Logging Interceptor for gRPC.

Provides comprehensive logging for async gRPC requests and responses.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

import grpc
import grpc.aio

logger = logging.getLogger(__name__)


class LoggingInterceptor(grpc.aio.ServerInterceptor):
    """
    Async gRPC interceptor for request/response logging.

    Features:
    - Logs all incoming requests
    - Logs response status and timing
    - Logs errors and exceptions
    - Structured logging with metadata
    - Performance tracking
    - Async/await support

    Example:
        ```python
        # In Django settings (auto-configured in dev mode)
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.interceptors.LoggingInterceptor",
            ]
        }
        ```

    Log Format:
        [gRPC] METHOD | STATUS | TIME | DETAILS
    """

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Intercept async gRPC service call for logging.

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler with logging
        """
        method_name = handler_call_details.method
        peer = self._extract_peer(handler_call_details.invocation_metadata)

        # DEBUG: Print to stdout to ensure we see it
        print(f"\n🔥🔥🔥 [LOGGING_INTERCEPTOR] intercept_service called! method={method_name}", flush=True)

        # Log incoming request
        logger.info(f"[gRPC] ➡️  {method_name} | peer={peer}")

        # Get handler and wrap it
        handler = await continuation(handler_call_details)

        if handler is None:
            logger.warning(f"[gRPC] ⚠️  {method_name} | No handler found")
            return None

        # Wrap handler methods to log responses
        return self._wrap_handler(handler, method_name, peer)

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        method_name: str,
        peer: str,
    ) -> grpc.RpcMethodHandler:
        """
        Wrap handler to add logging.

        Args:
            handler: Original RPC method handler
            method_name: gRPC method name
            peer: Client peer information

        Returns:
            Wrapped RPC method handler
        """
        # DEBUG: Print handler info
        print(f"\n🔧🔧🔧 [LOGGING_INTERCEPTOR] _wrap_handler called!", flush=True)
        print(f"   handler type: {type(handler)}", flush=True)
        print(f"   handler.unary_unary: {handler.unary_unary}", flush=True)
        print(f"   handler.unary_stream: {handler.unary_stream}", flush=True)
        print(f"   handler.stream_unary: {handler.stream_unary}", flush=True)
        print(f"   handler.stream_stream: {handler.stream_stream}", flush=True)
        print(f"   request_streaming: {handler.request_streaming}", flush=True)
        print(f"   response_streaming: {handler.response_streaming}", flush=True)

        def wrap_unary_unary(behavior):
            def wrapper(request, context):
                start_time = time.time()
                try:
                    response = behavior(request, context)
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.info(
                        f"[gRPC] ✅ {method_name} | "
                        f"status=OK | "
                        f"time={duration:.2f}ms | "
                        f"peer={peer}"
                    )
                    return response
                except Exception as e:
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.error(
                        f"[gRPC] ❌ {method_name} | "
                        f"status=ERROR | "
                        f"time={duration:.2f}ms | "
                        f"error={type(e).__name__}: {str(e)} | "
                        f"peer={peer}",
                        exc_info=True
                    )
                    raise
            return wrapper

        def wrap_unary_stream(behavior):
            def wrapper(request, context):
                start_time = time.time()
                message_count = 0
                try:
                    for response in behavior(request, context):
                        message_count += 1
                        yield response
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.info(
                        f"[gRPC] ✅ {method_name} (stream) | "
                        f"status=OK | "
                        f"messages={message_count} | "
                        f"time={duration:.2f}ms | "
                        f"peer={peer}"
                    )
                except Exception as e:
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.error(
                        f"[gRPC] ❌ {method_name} (stream) | "
                        f"status=ERROR | "
                        f"messages={message_count} | "
                        f"time={duration:.2f}ms | "
                        f"error={type(e).__name__}: {str(e)} | "
                        f"peer={peer}",
                        exc_info=True
                    )
                    raise
            return wrapper

        def wrap_stream_unary(behavior):
            def wrapper(request_iterator, context):
                start_time = time.time()
                message_count = 0
                try:
                    # Count messages
                    requests = []
                    for req in request_iterator:
                        message_count += 1
                        requests.append(req)

                    # Process
                    response = behavior(iter(requests), context)
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.info(
                        f"[gRPC] ✅ {method_name} (client stream) | "
                        f"status=OK | "
                        f"messages={message_count} | "
                        f"time={duration:.2f}ms | "
                        f"peer={peer}"
                    )
                    return response
                except Exception as e:
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.error(
                        f"[gRPC] ❌ {method_name} (client stream) | "
                        f"status=ERROR | "
                        f"messages={message_count} | "
                        f"time={duration:.2f}ms | "
                        f"error={type(e).__name__}: {str(e)} | "
                        f"peer={peer}",
                        exc_info=True
                    )
                    raise
            return wrapper

        def wrap_stream_stream(behavior):
            print(f"\n🎯🎯🎯 [LOGGING_INTERCEPTOR] wrap_stream_stream called for behavior={behavior}", flush=True)
            # All behaviors are async now
            async def async_wrapper(request_iterator, context):
                print(f"\n🚀🚀🚀 [LOGGING_INTERCEPTOR] async_wrapper INVOKED!", flush=True)
                start_time = time.time()
                out_count = 0
                try:
                    logger.info(f"[gRPC] 🔄 {method_name} (bidi stream) | peer={peer}")

                    async for response in behavior(request_iterator, context):
                        out_count += 1
                        yield response

                    duration = (time.time() - start_time) * 1000  # ms
                    logger.info(
                        f"[gRPC] ✅ {method_name} (bidi stream) | "
                        f"status=OK | "
                        f"out={out_count} | "
                        f"time={duration:.2f}ms | "
                        f"peer={peer}"
                    )
                except Exception as e:
                    duration = (time.time() - start_time) * 1000  # ms
                    logger.error(
                        f"[gRPC] ❌ {method_name} (bidi stream) | "
                        f"status=ERROR | "
                        f"out={out_count} | "
                        f"time={duration:.2f}ms | "
                        f"error={type(e).__name__}: {str(e)} | "
                        f"peer={peer}",
                        exc_info=True
                    )
                    raise
            return async_wrapper

        # Return wrapped handler based on type
        # IMPORTANT: For grpc.aio, we must NOT use grpc.*_rpc_method_handler()
        # functions as they create sync handlers. Instead, we create a simple
        # object that mimics RpcMethodHandler but preserves async methods.
        if handler.unary_unary:
            return _WrappedHandler(handler, unary_unary=wrap_unary_unary(handler.unary_unary))
        elif handler.unary_stream:
            return _WrappedHandler(handler, unary_stream=wrap_unary_stream(handler.unary_stream))
        elif handler.stream_unary:
            return _WrappedHandler(handler, stream_unary=wrap_stream_unary(handler.stream_unary))
        elif handler.stream_stream:
            return _WrappedHandler(handler, stream_stream=wrap_stream_stream(handler.stream_stream))
        else:
            return handler

    def _extract_peer(self, metadata: tuple) -> str:
        """
        Extract peer information from metadata.

        Args:
            metadata: gRPC invocation metadata

        Returns:
            Peer identifier string
        """
        if not metadata:
            return "unknown"

        # Convert to dict for easier access
        metadata_dict = dict(metadata)

        # Try to get user-agent or return unknown
        return metadata_dict.get("user-agent", "unknown")


class _WrappedHandler:
    """
    Wrapper for RpcMethodHandler that preserves async methods for grpc.aio.

    The standard grpc.*_rpc_method_handler() functions create sync handlers,
    which don't work properly with grpc.aio async server. This class simply
    wraps the original handler and replaces one method with a wrapped version.
    """

    def __init__(self, original_handler, **wrapped_methods):
        """
        Create wrapped handler.

        Args:
            original_handler: Original RpcMethodHandler
            **wrapped_methods: Methods to replace (unary_unary, stream_stream, etc.)
        """
        self.request_streaming = original_handler.request_streaming
        self.response_streaming = original_handler.response_streaming
        self.request_deserializer = original_handler.request_deserializer
        self.response_serializer = original_handler.response_serializer

        # Copy original methods, replace with wrapped versions
        self.unary_unary = wrapped_methods.get('unary_unary', original_handler.unary_unary)
        self.unary_stream = wrapped_methods.get('unary_stream', original_handler.unary_stream)
        self.stream_unary = wrapped_methods.get('stream_unary', original_handler.stream_unary)
        self.stream_stream = wrapped_methods.get('stream_stream', original_handler.stream_stream)


__all__ = ["LoggingInterceptor"]
