"""
Observability Interceptor for gRPC.

Combines metrics, logging, request_logger, and centrifugo into a single interceptor
to eliminate the 5-layer async generator nesting bug in bidirectional streaming.

The problem: Each interceptor wraps request_iterator in counting_iterator(),
creating 5 layers of async generator nesting. After ~15 messages, buffer
backpressure causes premature StopAsyncIteration.

Solution: Consolidate all observability features into ONE counting_iterator().

Architecture:
    BEFORE: Metrics → Logging → RequestLogger → Centrifugo → Auth → Handler
    AFTER:  Auth → Observability → Handler (only 2 layers!)

Configuration via GRPCObservabilityConfig:
    - log_to_db: Enable/disable database logging
    - log_streaming: Log streaming calls (default False - they create pending entries)
    - log_errors_only: Only log errors to DB
    - sampling_rate: Sample rate for logging (0.0 to 1.0)
"""

from __future__ import annotations

import inspect
import logging
import time
import uuid
from typing import Callable, Optional, Any

import grpc
import grpc.aio
from django.db import close_old_connections

from .metrics import get_metrics_collector
from .utils import (
    get_observability_config,
    is_centrifugo_configured,
    extract_peer,
    extract_user_agent,
    parse_method,
)
from .wrapped_handler import WrappedHandler
from .db_logger import RequestLogger
from .publishers import EventPublisher

logger = logging.getLogger(__name__)


class ObservabilityInterceptor(grpc.aio.ServerInterceptor):
    """
    Combined gRPC interceptor for all observability features.

    Consolidates:
    - MetricsInterceptor: Request counts, response times, error rates
    - LoggingInterceptor: Request/response logging
    - RequestLoggerInterceptor: Database logging to GRPCRequestLog
    - CentrifugoInterceptor: WebSocket publishing

    This eliminates 4 layers of generator nesting, fixing the 15-message
    StopAsyncIteration bug in bidirectional streaming.

    Configuration is auto-loaded from GRPCObservabilityConfig (django-cfg).
    """

    def __init__(self):
        """Initialize observability interceptor."""
        # Load config from django-cfg
        obs_config = get_observability_config()

        # Always-on features (no overhead)
        self.enable_metrics = True
        self.enable_logging = True

        # Centrifugo: auto-detect from django-cfg config
        self.enable_centrifugo = is_centrifugo_configured()

        # Configurable from GRPCObservabilityConfig
        if obs_config:
            self.enable_request_logger = obs_config.log_to_db
            self.log_errors_only = obs_config.log_errors_only
            publish_to_telegram = obs_config.telegram_notifications
        else:
            self.enable_request_logger = True
            self.log_errors_only = False
            publish_to_telegram = False

        # Never log request/response data by default (too heavy)
        self.log_request_data = False
        self.log_response_data = False

        # Never log streaming calls to DB (they create 'pending' entries)
        self.log_streaming = False

        # Metrics collector
        self.metrics = get_metrics_collector()

        # Request logger
        self.request_logger = RequestLogger(
            log_request_data=self.log_request_data,
            log_response_data=self.log_response_data,
        )

        # Event publisher (Centrifugo + Telegram)
        self._init_publisher(obs_config, publish_to_telegram)

    def _init_publisher(self, obs_config, publish_to_telegram: bool):
        """Initialize event publisher with config."""
        # Get development mode
        is_development = False
        centrifugo_enabled = False

        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if config:
                is_development = config.is_development
                if config.centrifugo and config.centrifugo.enabled:
                    centrifugo_enabled = True
        except Exception as e:
            logger.warning(f"ObservabilityInterceptor: Failed to get config: {e}")

        self.publisher = EventPublisher(
            centrifugo_enabled=centrifugo_enabled and self.enable_centrifugo,
            telegram_enabled=publish_to_telegram,
            is_development=is_development,
        )

        if obs_config:
            self.publisher.init_from_config(obs_config)

        self.publisher.init_centrifugo()
        self.publisher.init_telegram()

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """Intercept gRPC service call for observability."""
        # Close stale database connections before processing request
        # This prevents "connection is closed" errors in async gRPC context
        close_old_connections()

        method_name = handler_call_details.method
        metadata = handler_call_details.invocation_metadata
        peer = extract_peer(metadata)
        user_agent = extract_user_agent(metadata)
        service_name, method_short = parse_method(method_name)

        # Generate request ID for tracking
        request_id = str(uuid.uuid4())

        # Record request in metrics
        if self.enable_metrics:
            self.metrics.record_request(method_name)

        # Log incoming request
        if self.enable_logging:
            logger.info(f"[gRPC] --> {method_name} | peer={peer}")

        # Publish start event to Centrifugo
        if self.publisher.centrifugo_enabled and self.publisher.publish_start:
            await self.publisher.publish_event(
                event_type="rpc_start",
                method=method_name,
                service=service_name,
                method_name=method_short,
                peer=peer,
            )

        # Get handler
        handler = await continuation(handler_call_details)

        if handler is None:
            logger.warning(f"[gRPC] No handler found for {method_name}")
            return None

        # Wrap handler with observability
        return self._wrap_handler(
            handler=handler,
            method_name=method_name,
            service_name=service_name,
            method_short=method_short,
            peer=peer,
            user_agent=user_agent,
            request_id=request_id,
        )

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        method_name: str,
        service_name: str,
        method_short: str,
        peer: str,
        user_agent: str,
        request_id: str,
    ) -> grpc.RpcMethodHandler:
        """Wrap handler to add observability."""
        ctx = _WrapContext(
            interceptor=self,
            method_name=method_name,
            service_name=service_name,
            method_short=method_short,
            peer=peer,
            user_agent=user_agent,
            request_id=request_id,
        )

        if handler.stream_stream:
            wrapped = self._wrap_stream_stream(handler.stream_stream, ctx)
            return WrappedHandler(handler, stream_stream=wrapped)

        if handler.unary_unary:
            wrapped = self._wrap_unary_unary(handler.unary_unary, ctx)
            return WrappedHandler(handler, unary_unary=wrapped)

        if handler.unary_stream:
            wrapped = self._wrap_unary_stream(handler.unary_stream, ctx)
            return WrappedHandler(handler, unary_stream=wrapped)

        if handler.stream_unary:
            wrapped = self._wrap_stream_unary(handler.stream_unary, ctx)
            return WrappedHandler(handler, stream_unary=wrapped)

        return handler

    def _wrap_stream_stream(self, behavior, ctx: "_WrapContext"):
        """Wrap bidirectional streaming RPC - THE CRITICAL METHOD."""
        async def wrapper(request_iterator, context):
            start_time = time.time()
            in_count = 0
            out_count = 0
            log_entry = None

            # Skip streaming calls unless explicitly enabled
            should_log_to_db = self.enable_request_logger and self.log_streaming
            if should_log_to_db:
                log_entry = await self.request_logger.create_log_entry(
                    request_id=ctx.request_id,
                    service_name=ctx.service_name,
                    method_name=ctx.method_short,
                    full_method=ctx.method_name,
                    peer=ctx.peer,
                    user_agent=ctx.user_agent,
                    context=context,
                )

            # SINGLE counting_iterator combining ALL observability features
            async def observability_iterator():
                nonlocal in_count
                try:
                    async for req in request_iterator:
                        in_count += 1
                        msg_type = self._get_message_type(req)

                        if self.enable_logging:
                            logger.debug(f"[gRPC] <-- {ctx.method_name} #{in_count} type={msg_type}")

                        if self.publisher.centrifugo_enabled and self.publisher.publish_stream_messages:
                            await self.publisher.publish_event(
                                event_type="stream_message",
                                method=ctx.method_name,
                                service=ctx.service_name,
                                method_name=ctx.method_short,
                                peer=ctx.peer,
                                message_count=in_count,
                                direction="client_to_server",
                            )

                        yield req

                except Exception as e:
                    logger.error(f"[gRPC] Stream error in {ctx.method_name}: {type(e).__name__}: {e}")
                    raise

            try:
                if self.enable_logging:
                    logger.info(f"[gRPC] <-> {ctx.method_name} (bidi stream) | peer={ctx.peer}")

                async for response in behavior(observability_iterator(), context):
                    out_count += 1

                    if self.publisher.centrifugo_enabled and self.publisher.publish_stream_messages:
                        await self.publisher.publish_event(
                            event_type="stream_message",
                            method=ctx.method_name,
                            service=ctx.service_name,
                            method_name=ctx.method_short,
                            peer=ctx.peer,
                            message_count=out_count,
                            direction="server_to_client",
                        )

                    yield response

                # Stream completed successfully
                duration_ms = (time.time() - start_time) * 1000
                await self._on_success(ctx, duration_ms, log_entry, in_count, out_count, is_stream=True)

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                await self._on_error(ctx, e, context, duration_ms, log_entry, in_count, out_count, is_stream=True)
                raise

        return wrapper

    def _wrap_unary_unary(self, behavior, ctx: "_WrapContext"):
        """Wrap unary-unary RPC."""
        async def wrapper(request, context):
            start_time = time.time()
            log_entry = None

            should_create_log = self.enable_request_logger and not self.log_errors_only
            if should_create_log:
                log_entry = await self.request_logger.create_log_entry(
                    request_id=ctx.request_id,
                    service_name=ctx.service_name,
                    method_name=ctx.method_short,
                    full_method=ctx.method_name,
                    peer=ctx.peer,
                    user_agent=ctx.user_agent,
                    context=context,
                    request=request if self.log_request_data else None,
                )

            try:
                # Handle both async and sync behaviors
                if inspect.iscoroutinefunction(behavior):
                    response = await behavior(request, context)
                else:
                    response = behavior(request, context)

                duration_ms = (time.time() - start_time) * 1000
                await self._on_success(ctx, duration_ms, log_entry, response=response)
                return response

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                # Always log errors to DB
                if self.enable_request_logger and not log_entry and self.log_errors_only:
                    log_entry = await self.request_logger.create_log_entry(
                        request_id=ctx.request_id,
                        service_name=ctx.service_name,
                        method_name=ctx.method_short,
                        full_method=ctx.method_name,
                        peer=ctx.peer,
                        user_agent=ctx.user_agent,
                        context=context,
                    )

                await self._on_error(ctx, e, context, duration_ms, log_entry)
                raise

        return wrapper

    def _wrap_unary_stream(self, behavior, ctx: "_WrapContext"):
        """Wrap unary-stream (server streaming) RPC."""
        async def wrapper(request, context):
            start_time = time.time()
            out_count = 0
            log_entry = None

            if self.enable_request_logger:
                log_entry = await self.request_logger.create_log_entry(
                    request_id=ctx.request_id,
                    service_name=ctx.service_name,
                    method_name=ctx.method_short,
                    full_method=ctx.method_name,
                    peer=ctx.peer,
                    user_agent=ctx.user_agent,
                    context=context,
                    request=request if self.log_request_data else None,
                )

            try:
                if self.enable_logging:
                    logger.info(f"[gRPC] --> {ctx.method_name} (server stream) | peer={ctx.peer}")

                async for response in behavior(request, context):
                    out_count += 1
                    yield response

                duration_ms = (time.time() - start_time) * 1000
                await self._on_success(ctx, duration_ms, log_entry, out_count=out_count, is_stream=True)

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                await self._on_error(ctx, e, context, duration_ms, log_entry, out_count=out_count, is_stream=True)
                raise

        return wrapper

    def _wrap_stream_unary(self, behavior, ctx: "_WrapContext"):
        """Wrap stream-unary (client streaming) RPC."""
        async def wrapper(request_iterator, context):
            start_time = time.time()
            in_count = 0
            log_entry = None

            if self.enable_request_logger:
                log_entry = await self.request_logger.create_log_entry(
                    request_id=ctx.request_id,
                    service_name=ctx.service_name,
                    method_name=ctx.method_short,
                    full_method=ctx.method_name,
                    peer=ctx.peer,
                    user_agent=ctx.user_agent,
                    context=context,
                )

            # Count incoming messages
            requests = []
            async for req in request_iterator:
                in_count += 1
                requests.append(req)

            async def request_iter():
                for r in requests:
                    yield r

            try:
                if self.enable_logging:
                    logger.info(f"[gRPC] <-- {ctx.method_name} (client stream) | messages={in_count} | peer={ctx.peer}")

                response = await behavior(request_iter(), context)
                duration_ms = (time.time() - start_time) * 1000
                await self._on_success(ctx, duration_ms, log_entry, in_count=in_count, response=response, is_stream=True)
                return response

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                await self._on_error(ctx, e, context, duration_ms, log_entry, in_count=in_count, is_stream=True)
                raise

        return wrapper

    # =========================================================================
    # Callbacks
    # =========================================================================

    async def _on_success(
        self,
        ctx: "_WrapContext",
        duration_ms: float,
        log_entry: Optional[Any],
        in_count: int = 0,
        out_count: int = 0,
        response: Any = None,
        is_stream: bool = False,
    ):
        """Handle successful RPC completion."""
        if self.enable_metrics:
            self.metrics.record_response_time(ctx.method_name, duration_ms)

        if self.enable_logging:
            if is_stream:
                logger.info(
                    f"[gRPC] OK {ctx.method_name} (stream) | "
                    f"in={in_count} out={out_count} | "
                    f"time={duration_ms:.2f}ms | peer={ctx.peer}"
                )
            else:
                logger.info(f"[gRPC] OK {ctx.method_name} | time={duration_ms:.2f}ms | peer={ctx.peer}")

        if log_entry:
            response_data = {"in_count": in_count, "out_count": out_count} if is_stream else None
            await self.request_logger.mark_success(
                log_entry,
                duration_ms=int(duration_ms),
                response=response if not is_stream else None,
                response_data=response_data,
            )

        if self.publisher.centrifugo_enabled and self.publisher.publish_end:
            await self.publisher.publish_event(
                event_type="rpc_end",
                method=ctx.method_name,
                service=ctx.service_name,
                method_name=ctx.method_short,
                peer=ctx.peer,
                duration_ms=duration_ms,
                status="OK",
                in_message_count=in_count,
                out_message_count=out_count,
            )

    async def _on_error(
        self,
        ctx: "_WrapContext",
        error: Exception,
        context: grpc.aio.ServicerContext,
        duration_ms: float,
        log_entry: Optional[Any],
        in_count: int = 0,
        out_count: int = 0,
        is_stream: bool = False,
    ):
        """Handle RPC error."""
        if self.enable_metrics:
            self.metrics.record_response_time(ctx.method_name, duration_ms)
            self.metrics.record_error(ctx.method_name)

        if self.enable_logging:
            if is_stream:
                logger.error(
                    f"[gRPC] ERR {ctx.method_name} (stream) | "
                    f"in={in_count} out={out_count} | "
                    f"time={duration_ms:.2f}ms | "
                    f"error={type(error).__name__}: {error} | peer={ctx.peer}",
                    exc_info=True
                )
            else:
                logger.error(
                    f"[gRPC] ERR {ctx.method_name} | time={duration_ms:.2f}ms | "
                    f"error={type(error).__name__}: {error} | peer={ctx.peer}",
                    exc_info=True
                )

        if log_entry:
            await self.request_logger.mark_error(log_entry, error=error, context=context, duration_ms=int(duration_ms))

        if self.publisher.centrifugo_enabled and self.publisher.publish_errors:
            await self.publisher.publish_error(
                error=error,
                method=ctx.method_name,
                service=ctx.service_name,
                method_name=ctx.method_short,
                peer=ctx.peer,
                duration_ms=duration_ms,
                in_message_count=in_count,
                out_message_count=out_count,
            )

    @staticmethod
    def _get_message_type(req) -> str:
        """Get message type from request."""
        if hasattr(req, 'WhichOneof'):
            try:
                return req.WhichOneof('payload') or 'unknown'
            except ValueError:
                return type(req).__name__
        return 'unknown'


class _WrapContext:
    """Context for wrapped handlers."""

    def __init__(
        self,
        interceptor: ObservabilityInterceptor,
        method_name: str,
        service_name: str,
        method_short: str,
        peer: str,
        user_agent: str,
        request_id: str,
    ):
        self.interceptor = interceptor
        self.method_name = method_name
        self.service_name = service_name
        self.method_short = method_short
        self.peer = peer
        self.user_agent = user_agent
        self.request_id = request_id


# Re-export for backwards compatibility
from .metrics import get_metrics, reset_metrics

__all__ = [
    "ObservabilityInterceptor",
    "get_metrics",
    "reset_metrics",
]
