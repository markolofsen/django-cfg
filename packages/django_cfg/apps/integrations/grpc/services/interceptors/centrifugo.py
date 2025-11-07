"""
Centrifugo Publishing Interceptor for gRPC.

Automatically publishes gRPC call metadata to Centrifugo WebSocket channels.
Works alongside CentrifugoBridgeMixin for complete event visibility.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone as tz
from typing import Callable, Optional, Any, Dict

import grpc
import grpc.aio

logger = logging.getLogger(__name__)


class CentrifugoInterceptor(grpc.aio.ServerInterceptor):
    """
    Async gRPC interceptor that publishes call metadata to Centrifugo.

    Automatically publishes:
    - RPC method invocations (start/end)
    - Timing information
    - Status codes
    - Message counts
    - Error information
    - Client peer information

    Works in parallel with CentrifugoBridgeMixin:
    - Interceptor: Publishes RPC-level metadata (method, timing, status)
    - Mixin: Publishes message-level data (protobuf field contents)

    Example:
        ```python
        # In Django settings
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.interceptors.CentrifugoInterceptor",
            ]
        }
        ```

    Channel naming:
        - RPC calls: `grpc#{service}#{method}#meta`
        - Errors: `grpc#{service}#{method}#errors`

    Published metadata:
        {
            "event_type": "rpc_start" | "rpc_end" | "rpc_error",
            "method": "/service.Service/Method",
            "service": "service.Service",
            "method_name": "Method",
            "peer": "ipv4:127.0.0.1:12345",
            "timestamp": "2025-11-05T...",
            "duration_ms": 123.45,  # Only on rpc_end
            "status": "OK" | "ERROR",
            "message_count": 10,  # For streaming
            "error": {...},  # Only on error
        }
    """

    def __init__(
        self,
        enabled: bool = True,
        publish_start: bool = False,
        publish_end: bool = True,
        publish_errors: bool = True,
        publish_stream_messages: bool = False,
        channel_template: str = "grpc#{service}#{method}#meta",
        error_channel_template: str = "grpc#{service}#{method}#errors",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Centrifugo interceptor.

        Args:
            enabled: Enable/disable publishing
            publish_start: Publish RPC start events
            publish_end: Publish RPC completion events
            publish_errors: Publish RPC error events
            publish_stream_messages: Publish each streaming message (can be noisy)
            channel_template: Channel name template for metadata
            error_channel_template: Channel name template for errors
            metadata: Additional metadata to include in all events
        """
        self.enabled = enabled
        self.publish_start = publish_start
        self.publish_end = publish_end
        self.publish_errors = publish_errors
        self.publish_stream_messages = publish_stream_messages
        self.channel_template = channel_template
        self.error_channel_template = error_channel_template
        self.metadata = metadata or {}

        self._centrifugo_publisher: Optional[Any] = None
        self._initialize_publisher()

    def _initialize_publisher(self):
        """Initialize Centrifugo publisher lazily with direct client."""
        if not self.enabled:
            logger.debug("CentrifugoInterceptor disabled")
            return

        try:
            from django_cfg.apps.integrations.centrifugo.services import get_centrifugo_publisher
            # Use Publisher with DirectClient (use_direct=True by default)
            # This bypasses wrapper and goes directly to Centrifugo
            self._centrifugo_publisher = get_centrifugo_publisher()
            logger.info("CentrifugoInterceptor initialized with DirectCentrifugoClient")
        except Exception as e:
            logger.warning(
                f"Failed to initialize Centrifugo publisher in interceptor: {e}. "
                f"Interceptor will continue without publishing."
            )
            self.enabled = False

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Intercept async gRPC service call for Centrifugo publishing.

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler with Centrifugo publishing
        """
        if not self.enabled or not self._centrifugo_publisher:
            # Pass through without interception
            return await continuation(handler_call_details)

        method_name = handler_call_details.method
        peer = self._extract_peer(handler_call_details.invocation_metadata)
        service_name, method_short = self._parse_method_name(method_name)

        # Publish start event
        if self.publish_start:
            await self._publish_event(
                event_type="rpc_start",
                method=method_name,
                service=service_name,
                method_name=method_short,
                peer=peer,
            )

        # Get handler and wrap it
        handler = await continuation(handler_call_details)

        if handler is None:
            logger.warning(f"[CentrifugoInterceptor] No handler found for {method_name}")
            return None

        # Wrap handler methods to publish events
        return self._wrap_handler(handler, method_name, service_name, method_short, peer)

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        method_name: str,
        service_name: str,
        method_short: str,
        peer: str,
    ) -> grpc.RpcMethodHandler:
        """
        Wrap handler to add Centrifugo publishing.

        Args:
            handler: Original RPC method handler
            method_name: Full gRPC method name
            service_name: Service name
            method_short: Short method name
            peer: Client peer information

        Returns:
            Wrapped RPC method handler
        """
        # Determine handler type and wrap accordingly
        if handler.unary_unary:
            wrapped = self._wrap_unary_unary(
                handler.unary_unary, method_name, service_name, method_short, peer
            )
            return grpc.unary_unary_rpc_method_handler(
                wrapped,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.unary_stream:
            wrapped = self._wrap_unary_stream(
                handler.unary_stream, method_name, service_name, method_short, peer
            )
            return grpc.unary_stream_rpc_method_handler(
                wrapped,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_unary:
            wrapped = self._wrap_stream_unary(
                handler.stream_unary, method_name, service_name, method_short, peer
            )
            return grpc.stream_unary_rpc_method_handler(
                wrapped,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_stream:
            wrapped = self._wrap_stream_stream(
                handler.stream_stream, method_name, service_name, method_short, peer
            )
            return grpc.stream_stream_rpc_method_handler(
                wrapped,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return handler

    def _wrap_unary_unary(self, behavior, method_name, service_name, method_short, peer):
        """Wrap unary-unary RPC."""
        async def wrapper(request, context):
            start_time = time.time()
            try:
                response = await behavior(request, context)
                duration = (time.time() - start_time) * 1000

                if self.publish_end:
                    await self._publish_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        status="OK",
                    )

                return response
            except Exception as e:
                duration = (time.time() - start_time) * 1000

                if self.publish_errors:
                    await self._publish_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        error=e,
                    )
                raise

        return wrapper

    def _wrap_unary_stream(self, behavior, method_name, service_name, method_short, peer):
        """Wrap unary-stream RPC."""
        async def wrapper(request, context):
            start_time = time.time()
            message_count = 0
            try:
                async for response in behavior(request, context):
                    message_count += 1

                    if self.publish_stream_messages:
                        await self._publish_event(
                            event_type="stream_message",
                            method=method_name,
                            service=service_name,
                            method_name=method_short,
                            peer=peer,
                            message_count=message_count,
                            direction="server_to_client",
                        )

                    yield response

                duration = (time.time() - start_time) * 1000

                if self.publish_end:
                    await self._publish_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        status="OK",
                        message_count=message_count,
                    )

            except Exception as e:
                duration = (time.time() - start_time) * 1000

                if self.publish_errors:
                    await self._publish_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        error=e,
                        message_count=message_count,
                    )
                raise

        return wrapper

    def _wrap_stream_unary(self, behavior, method_name, service_name, method_short, peer):
        """Wrap stream-unary RPC."""
        async def wrapper(request_iterator, context):
            start_time = time.time()
            message_count = 0
            try:
                # Count incoming messages
                requests = []
                async for req in request_iterator:
                    message_count += 1

                    if self.publish_stream_messages:
                        await self._publish_event(
                            event_type="stream_message",
                            method=method_name,
                            service=service_name,
                            method_name=method_short,
                            peer=peer,
                            message_count=message_count,
                            direction="client_to_server",
                        )

                    requests.append(req)

                # Process
                async def request_iter():
                    for r in requests:
                        yield r

                response = await behavior(request_iter(), context)
                duration = (time.time() - start_time) * 1000

                if self.publish_end:
                    await self._publish_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        status="OK",
                        message_count=message_count,
                    )

                return response
            except Exception as e:
                duration = (time.time() - start_time) * 1000

                if self.publish_errors:
                    await self._publish_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        error=e,
                        message_count=message_count,
                    )
                raise

        return wrapper

    def _wrap_stream_stream(self, behavior, method_name, service_name, method_short, peer):
        """Wrap bidirectional streaming RPC."""
        async def wrapper(request_iterator, context):
            start_time = time.time()
            in_count = 0
            out_count = 0
            try:
                # Wrap request iterator to count messages
                async def counting_iterator():
                    nonlocal in_count
                    async for req in request_iterator:
                        in_count += 1

                        if self.publish_stream_messages:
                            await self._publish_event(
                                event_type="stream_message",
                                method=method_name,
                                service=service_name,
                                method_name=method_short,
                                peer=peer,
                                message_count=in_count,
                                direction="client_to_server",
                            )

                        yield req

                # Stream responses
                async for response in behavior(counting_iterator(), context):
                    out_count += 1

                    if self.publish_stream_messages:
                        await self._publish_event(
                            event_type="stream_message",
                            method=method_name,
                            service=service_name,
                            method_name=method_short,
                            peer=peer,
                            message_count=out_count,
                            direction="server_to_client",
                        )

                    yield response

                duration = (time.time() - start_time) * 1000

                if self.publish_end:
                    await self._publish_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        status="OK",
                        in_message_count=in_count,
                        out_message_count=out_count,
                    )

            except Exception as e:
                duration = (time.time() - start_time) * 1000

                if self.publish_errors:
                    await self._publish_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration,
                        error=e,
                        in_message_count=in_count,
                        out_message_count=out_count,
                    )
                raise

        return wrapper

    async def _publish_event(self, **data):
        """Publish event to Centrifugo via Publisher."""
        try:
            # Build channel name
            channel = self.channel_template.format(
                service=data.get('service', 'unknown'),
                method=data.get('method_name', 'unknown'),
            )

            # Use Publisher's publish_grpc_event for type-safe gRPC events
            await self._centrifugo_publisher.publish_grpc_event(
                channel=channel,
                method=data.get('method', ''),
                status=data.get('status', 'UNKNOWN'),
                duration_ms=data.get('duration_ms', 0.0),
                peer=data.get('peer'),
                metadata={
                    'event_type': data.get('event_type'),
                    **self.metadata,
                },
                **{k: v for k, v in data.items() if k not in ['method', 'status', 'duration_ms', 'peer', 'event_type', 'service', 'method_name']},
            )

            logger.debug(f"Published gRPC event to {channel}: {data.get('event_type')}")

        except Exception as e:
            logger.warning(f"Failed to publish gRPC event to Centrifugo: {e}")

    async def _publish_error(self, error: Exception, **data):
        """Publish error to Centrifugo via Publisher."""
        try:
            # Build error channel name
            channel = self.error_channel_template.format(
                service=data.get('service', 'unknown'),
                method=data.get('method_name', 'unknown'),
            )

            # Use Publisher's publish_grpc_event with error status
            await self._centrifugo_publisher.publish_grpc_event(
                channel=channel,
                method=data.get('method', ''),
                status='ERROR',
                duration_ms=data.get('duration_ms', 0.0),
                peer=data.get('peer'),
                metadata={
                    'event_type': 'rpc_error',
                    'error': {
                        'type': type(error).__name__,
                        'message': str(error),
                    },
                    **self.metadata,
                },
                **{k: v for k, v in data.items() if k not in ['method', 'duration_ms', 'peer', 'error', 'service', 'method_name']},
            )

            logger.debug(f"Published gRPC error to {channel}")

        except Exception as e:
            logger.warning(f"Failed to publish gRPC error to Centrifugo: {e}")

    @staticmethod
    def _extract_peer(invocation_metadata) -> str:
        """Extract peer information from metadata."""
        if invocation_metadata:
            for key, value in invocation_metadata:
                if key == "x-forwarded-for":
                    return value
        return "unknown"

    @staticmethod
    def _parse_method_name(full_method: str) -> tuple[str, str]:
        """
        Parse full gRPC method name.

        Args:
            full_method: e.g., "/trading_bots.BotStreamingService/ConnectBot"

        Returns:
            (service_name, method_name): ("trading_bots.BotStreamingService", "ConnectBot")
        """
        parts = full_method.strip("/").split("/")
        if len(parts) == 2:
            return parts[0], parts[1]
        return "unknown", full_method


__all__ = ["CentrifugoInterceptor"]
