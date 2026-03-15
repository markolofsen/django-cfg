"""
Wrapped Handler for gRPC async methods.

Preserves async methods for grpc.aio - the standard grpc.*_rpc_method_handler()
functions create sync handlers which don't work properly with async server.
"""


class WrappedHandler:
    """
    Wrapper for RpcMethodHandler that preserves async methods for grpc.aio.

    The standard grpc.*_rpc_method_handler() functions create sync handlers,
    which don't work properly with grpc.aio async server.
    """

    def __init__(self, original_handler, **wrapped_methods):
        self.request_streaming = original_handler.request_streaming
        self.response_streaming = original_handler.response_streaming
        self.request_deserializer = original_handler.request_deserializer
        self.response_serializer = original_handler.response_serializer

        self.unary_unary = wrapped_methods.get('unary_unary', original_handler.unary_unary)
        self.unary_stream = wrapped_methods.get('unary_stream', original_handler.unary_stream)
        self.stream_unary = wrapped_methods.get('stream_unary', original_handler.stream_unary)
        self.stream_stream = wrapped_methods.get('stream_stream', original_handler.stream_stream)


__all__ = ["WrappedHandler"]
