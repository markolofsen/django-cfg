"""
django_grpc.services.interceptors.wrapped_handler — WrappedHandler.

Preserves async methods when wrapping grpc.aio RpcMethodHandlers.

Problem: grpc.*_rpc_method_handler() creates SYNCHRONOUS handlers.
         In grpc.aio, sync handlers are silently ignored — the async
         handler is never called.

Solution: WrappedHandler copies all fields from the original handler
          and replaces only the specific method(s) being wrapped.

Usage (in every interceptor):
    handler = await continuation(handler_call_details)
    return WrappedHandler(handler, stream_stream=my_async_wrapper)

IMPORTANT: This is the SINGLE canonical WrappedHandler in this module.
           Do NOT create _WrappedHandler duplicates elsewhere.
           Bug #2 root cause: duplicate private classes in api_key_auth.py
           that diverged from this canonical version.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import grpc


class WrappedHandler:
    """Wrapper for RpcMethodHandler that preserves async methods for grpc.aio."""

    __slots__ = (
        "request_streaming",
        "response_streaming",
        "request_deserializer",
        "response_serializer",
        "unary_unary",
        "unary_stream",
        "stream_unary",
        "stream_stream",
    )

    # Slot-level type annotations (T-10)
    request_streaming: bool
    response_streaming: bool
    request_deserializer: Optional[Callable[..., Any]]
    response_serializer: Optional[Callable[..., Any]]
    unary_unary: Optional[Callable[..., Any]]
    unary_stream: Optional[Callable[..., Any]]
    stream_unary: Optional[Callable[..., Any]]
    stream_stream: Optional[Callable[..., Any]]

    def __init__(self, original_handler: "grpc.RpcMethodHandler", **wrapped_methods: Any) -> None:
        self.request_streaming    = original_handler.request_streaming
        self.response_streaming   = original_handler.response_streaming
        self.request_deserializer = original_handler.request_deserializer
        self.response_serializer  = original_handler.response_serializer

        self.unary_unary   = wrapped_methods.get("unary_unary",   original_handler.unary_unary)
        self.unary_stream  = wrapped_methods.get("unary_stream",  original_handler.unary_stream)
        self.stream_unary  = wrapped_methods.get("stream_unary",  original_handler.stream_unary)
        self.stream_stream = wrapped_methods.get("stream_stream", original_handler.stream_stream)


__all__ = ["WrappedHandler"]
