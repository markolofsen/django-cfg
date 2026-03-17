"""
django_grpc.services.client.internal_interceptor — Auto-inject internal secret.

Client-side interceptor that adds ``x-internal-secret`` metadata to all
outgoing gRPC calls, enabling trusted bypass of JWT auth on the server.

Usage::

    from django_cfg.modules.django_grpc.services.client import InternalSecretClientInterceptor

    interceptors = [InternalSecretClientInterceptor(secret)]
    channel = grpc.aio.insecure_channel(addr, interceptors=interceptors)
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import grpc
    import grpc.aio
    _HAS_GRPC = True
except ImportError:
    _HAS_GRPC = False


class _ClientCallDetails:
    """Mutable ClientCallDetails replacement with updated metadata.

    grpc.aio.ClientCallDetails uses read-only properties, so we create
    a plain object that quacks like one.
    """

    def __init__(
        self,
        method: str,
        timeout: float | None,
        metadata: list[tuple[str, str]] | None,
        credentials: Any,
        wait_for_ready: bool | None,
    ) -> None:
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready


def _inject_metadata(
    client_call_details: Any,
    secret: str,
) -> _ClientCallDetails:
    """Return new client_call_details with x-internal-secret injected."""
    metadata: list[tuple[str, str]] = []
    if client_call_details.metadata is not None:
        metadata = list(client_call_details.metadata)
    metadata.append(("x-internal-secret", secret))

    return _ClientCallDetails(
        method=client_call_details.method,
        timeout=client_call_details.timeout,
        metadata=metadata,
        credentials=client_call_details.credentials,
        wait_for_ready=client_call_details.wait_for_ready,
    )


if _HAS_GRPC:
    class InternalSecretClientInterceptor(
        grpc.aio.UnaryUnaryClientInterceptor,
        grpc.aio.UnaryStreamClientInterceptor,
        grpc.aio.StreamUnaryClientInterceptor,
        grpc.aio.StreamStreamClientInterceptor,
    ):
        """Auto-injects ``x-internal-secret`` on all outgoing gRPC calls.

        Attach to a channel to mark all requests as trusted internal calls::

            channel = grpc.aio.insecure_channel(
                addr,
                interceptors=[InternalSecretClientInterceptor(secret)],
            )
        """

        def __init__(self, secret: str) -> None:
            if not secret:
                raise ValueError("internal_secret must be a non-empty string")
            self._secret = secret

        async def intercept_unary_unary(self, continuation, client_call_details, request):
            new_details = _inject_metadata(client_call_details, self._secret)
            return await continuation(new_details, request)

        async def intercept_unary_stream(self, continuation, client_call_details, request):
            new_details = _inject_metadata(client_call_details, self._secret)
            return await continuation(new_details, request)

        async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
            new_details = _inject_metadata(client_call_details, self._secret)
            return await continuation(new_details, request_iterator)

        async def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
            new_details = _inject_metadata(client_call_details, self._secret)
            return await continuation(new_details, request_iterator)

else:
    class InternalSecretClientInterceptor:  # type: ignore[no-redef]
        """Stub when grpcio is not installed."""
        def __init__(self, secret: str) -> None:
            raise ImportError("grpcio is required for InternalSecretClientInterceptor")


__all__ = ["InternalSecretClientInterceptor"]
