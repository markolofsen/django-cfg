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

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone as tz
from typing import Callable, Optional, Any

import grpc
import grpc.aio
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_observability_config():
    """Get observability config from django-cfg or fallback to defaults."""
    try:
        from django_cfg.core import get_current_config
        config = get_current_config()
        if config and hasattr(config, 'grpc') and config.grpc:
            return config.grpc.observability
    except Exception:
        pass
    return None


def _is_centrifugo_configured() -> bool:
    """Check if Centrifugo is configured in django-cfg."""
    try:
        from django_cfg.core import get_current_config
        config = get_current_config()
        if config and hasattr(config, 'centrifugo') and config.centrifugo:
            # Check if it's enabled
            return getattr(config.centrifugo, 'enabled', True)
    except Exception:
        pass
    return False


# =============================================================================
# Metrics Collection (from metrics.py)
# =============================================================================

class MetricsCollector:
    """Thread-safe metrics collector for gRPC."""

    def __init__(self):
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.total_requests = 0
        self.total_errors = 0

    def record_request(self, method: str):
        self.request_counts[method] += 1
        self.total_requests += 1

    def record_error(self, method: str):
        self.error_counts[method] += 1
        self.total_errors += 1

    def record_response_time(self, method: str, duration_ms: float):
        self.response_times[method].append(duration_ms)

    def get_stats(self, method: str = None) -> dict:
        if method:
            times = self.response_times.get(method, [])
            return {
                "requests": self.request_counts.get(method, 0),
                "errors": self.error_counts.get(method, 0),
                "avg_time_ms": sum(times) / len(times) if times else 0,
                "min_time_ms": min(times) if times else 0,
                "max_time_ms": max(times) if times else 0,
            }
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / self.total_requests if self.total_requests > 0 else 0,
            "methods": {m: self.get_stats(m) for m in self.request_counts.keys()},
        }

    def reset(self):
        self.request_counts.clear()
        self.error_counts.clear()
        self.response_times.clear()
        self.total_requests = 0
        self.total_errors = 0


# Global metrics collector (singleton)
_metrics = MetricsCollector()


def get_metrics(method: str = None) -> dict:
    """Get metrics for a method or all methods."""
    return _metrics.get_stats(method)


def reset_metrics():
    """Reset all metrics."""
    _metrics.reset()


# =============================================================================
# Observability Interceptor
# =============================================================================

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
    Constructor args override the config for backwards compatibility.

    Example:
        ```python
        # In api/config.py:
        grpc = GRPCConfig(
            enabled=True,
            observability=GRPCObservabilityConfig(
                log_to_db=False,  # Disable for production
                log_streaming=False,  # Don't log bidi streams
                sampling_rate=0.1,  # Log 10% of requests
            )
        )
        ```
    """

    def __init__(self):
        """
        Initialize observability interceptor.

        Configuration is auto-loaded from GRPCObservabilityConfig.
        Smart defaults: metrics ON, logging ON, DB logging configurable.
        Centrifugo is auto-detected from django-cfg config.
        """
        # Load config from django-cfg
        obs_config = _get_observability_config()

        # Always-on features (no overhead)
        self.enable_metrics = True
        self.enable_logging = True

        # Centrifugo: auto-detect from django-cfg config
        self.enable_centrifugo = _is_centrifugo_configured()

        # Configurable from GRPCObservabilityConfig
        if obs_config:
            self.enable_request_logger = obs_config.log_to_db
            self.log_errors_only = obs_config.log_errors_only
        else:
            # Sensible defaults
            self.enable_request_logger = True
            self.log_errors_only = False

        # Never log request/response data by default (too heavy)
        self.log_request_data = False
        self.log_response_data = False

        # Never log streaming calls to DB (they create 'pending' entries)
        self.log_streaming = False

        # Metrics collector
        self.metrics = _metrics

        # Centrifugo config
        self._centrifugo_publisher: Optional[Any] = None
        self._telegram_service: Optional[Any] = None
        self.publish_to_telegram = False
        self._init_centrifugo()

    def _init_centrifugo(self):
        """Initialize Centrifugo publisher lazily."""
        if not self.enable_centrifugo:
            self.centrifugo_enabled = False
            return

        centrifugo_config = getattr(settings, "GRPC_CENTRIFUGO", {})
        self.centrifugo_enabled = centrifugo_config.get("enabled", True)
        self.publish_start = centrifugo_config.get("publish_start", False)
        self.publish_end = centrifugo_config.get("publish_end", True)
        self.publish_errors = centrifugo_config.get("publish_errors", True)
        self.publish_stream_messages = centrifugo_config.get("publish_stream_messages", False)
        self.channel_template = centrifugo_config.get("channel_template", "grpc#{service}#{method}#meta")
        self.error_channel_template = centrifugo_config.get("error_channel_template", "grpc#{service}#{method}#errors")
        self.centrifugo_metadata = centrifugo_config.get("metadata", {})
        # publish_to_telegram is already set from GRPCObservabilityConfig in __init__

        if not self.centrifugo_enabled:
            return

        try:
            from django_cfg.apps.integrations.centrifugo.services import get_centrifugo_publisher
            self._centrifugo_publisher = get_centrifugo_publisher()
            logger.info("ObservabilityInterceptor: Centrifugo publisher initialized")
        except Exception as e:
            logger.warning(f"ObservabilityInterceptor: Failed to init Centrifugo: {e}")
            self.centrifugo_enabled = False

        if self.publish_to_telegram:
            try:
                from django_cfg.modules.django_telegram import DjangoTelegram
                self._telegram_service = DjangoTelegram()
                if not self._telegram_service.is_configured:
                    self.publish_to_telegram = False
            except Exception as e:
                logger.warning(f"ObservabilityInterceptor: Failed to init Telegram: {e}")
                self.publish_to_telegram = False

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC service call for observability.

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler with observability
        """
        method_name = handler_call_details.method
        metadata = handler_call_details.invocation_metadata
        peer = self._extract_peer(metadata)
        user_agent = self._extract_user_agent(metadata)
        service_name, method_short = self._parse_method(method_name)

        # Generate request ID for tracking
        request_id = str(uuid.uuid4())

        # Record request in metrics
        if self.enable_metrics:
            self.metrics.record_request(method_name)

        # Log incoming request
        if self.enable_logging:
            logger.info(f"[gRPC] --> {method_name} | peer={peer}")

        # Publish start event to Centrifugo
        if self.enable_centrifugo and self.centrifugo_enabled and self.publish_start:
            await self._publish_centrifugo_event(
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

        if handler.stream_stream:
            wrapped = self._wrap_stream_stream(
                handler.stream_stream,
                method_name, service_name, method_short, peer, user_agent, request_id
            )
            return _WrappedHandler(handler, stream_stream=wrapped)

        if handler.unary_unary:
            wrapped = self._wrap_unary_unary(
                handler.unary_unary,
                method_name, service_name, method_short, peer, user_agent, request_id
            )
            return _WrappedHandler(handler, unary_unary=wrapped)

        if handler.unary_stream:
            wrapped = self._wrap_unary_stream(
                handler.unary_stream,
                method_name, service_name, method_short, peer, user_agent, request_id
            )
            return _WrappedHandler(handler, unary_stream=wrapped)

        if handler.stream_unary:
            wrapped = self._wrap_stream_unary(
                handler.stream_unary,
                method_name, service_name, method_short, peer, user_agent, request_id
            )
            return _WrappedHandler(handler, stream_unary=wrapped)

        return handler

    def _wrap_stream_stream(
        self, behavior, method_name, service_name, method_short, peer, user_agent, request_id
    ):
        """
        Wrap bidirectional streaming RPC - THE CRITICAL METHOD.

        This is where the bug was: multiple interceptors each had their own
        counting_iterator(), creating 5 layers of nesting. Now we have ONE.
        """
        async def wrapper(request_iterator, context):
            start_time = time.time()
            in_count = 0
            out_count = 0
            log_entry = None

            # Create database log entry (request logger feature)
            # Skip streaming calls unless explicitly enabled (they create 'pending' entries)
            should_log_to_db = (
                self.enable_request_logger
                and self.log_streaming  # NEW: must enable streaming logs explicitly
            )
            if should_log_to_db:
                log_entry = await self._create_log_entry(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_short,
                    full_method=method_name,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                )

            # SINGLE counting_iterator combining ALL observability features
            async def observability_iterator():
                nonlocal in_count
                try:
                    async for req in request_iterator:
                        in_count += 1

                        # Get message type (safely - some messages don't have 'payload' oneof)
                        msg_type = 'unknown'
                        if hasattr(req, 'WhichOneof'):
                            try:
                                msg_type = req.WhichOneof('payload') or 'unknown'
                            except ValueError:
                                # Message doesn't have 'payload' field (e.g. ServerReflectionRequest)
                                msg_type = type(req).__name__

                        # Logging
                        if self.enable_logging:
                            logger.debug(f"[gRPC] <-- {method_name} #{in_count} type={msg_type}")

                        # Centrifugo stream message
                        if self.enable_centrifugo and self.centrifugo_enabled and self.publish_stream_messages:
                            await self._publish_centrifugo_event(
                                event_type="stream_message",
                                method=method_name,
                                service=service_name,
                                method_name=method_short,
                                peer=peer,
                                message_count=in_count,
                                direction="client_to_server",
                            )

                        yield req

                except Exception as e:
                    logger.error(f"[gRPC] Stream error in {method_name}: {type(e).__name__}: {e}")
                    raise

            try:
                # Log stream start
                if self.enable_logging:
                    logger.info(f"[gRPC] <-> {method_name} (bidi stream) | peer={peer}")

                # Process stream with SINGLE iterator wrapper
                async for response in behavior(observability_iterator(), context):
                    out_count += 1

                    # Centrifugo outbound stream message
                    if self.enable_centrifugo and self.centrifugo_enabled and self.publish_stream_messages:
                        await self._publish_centrifugo_event(
                            event_type="stream_message",
                            method=method_name,
                            service=service_name,
                            method_name=method_short,
                            peer=peer,
                            message_count=out_count,
                            direction="server_to_client",
                        )

                    yield response

                # Stream completed successfully
                duration_ms = (time.time() - start_time) * 1000

                # Metrics
                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)

                # Logging
                if self.enable_logging:
                    logger.info(
                        f"[gRPC] OK {method_name} (bidi stream) | "
                        f"in={in_count} out={out_count} | "
                        f"time={duration_ms:.2f}ms | peer={peer}"
                    )

                # Request logger - mark success
                if should_log_to_db and log_entry:
                    await self._mark_log_success(
                        log_entry,
                        duration_ms=int(duration_ms),
                        response_data={"in_count": in_count, "out_count": out_count},
                    )

                # Centrifugo - end event
                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_end:
                    await self._publish_centrifugo_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        status="OK",
                        in_message_count=in_count,
                        out_message_count=out_count,
                    )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                # Metrics - error
                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)
                    self.metrics.record_error(method_name)

                # Logging - error
                if self.enable_logging:
                    logger.error(
                        f"[gRPC] ERR {method_name} (bidi stream) | "
                        f"in={in_count} out={out_count} | "
                        f"time={duration_ms:.2f}ms | "
                        f"error={type(e).__name__}: {e} | peer={peer}",
                        exc_info=True
                    )

                # Request logger - mark error
                if should_log_to_db and log_entry:
                    await self._mark_log_error(
                        log_entry,
                        error=e,
                        context=context,
                        duration_ms=int(duration_ms),
                    )

                # Centrifugo - error event
                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_errors:
                    await self._publish_centrifugo_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        error=e,
                        in_message_count=in_count,
                        out_message_count=out_count,
                    )

                raise

        return wrapper

    def _wrap_unary_unary(
        self, behavior, method_name, service_name, method_short, peer, user_agent, request_id
    ):
        """Wrap unary-unary RPC."""
        async def wrapper(request, context):
            start_time = time.time()
            log_entry = None

            # Determine if we should log this request to DB
            # If log_errors_only, we'll create log entry only on error
            should_create_log = (
                self.enable_request_logger
                and not self.log_errors_only
            )

            if should_create_log:
                log_entry = await self._create_log_entry(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_short,
                    full_method=method_name,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                    request=request if self.log_request_data else None,
                )

            try:
                # Handle both async and sync behaviors (Health Check is sync)
                import inspect
                if inspect.iscoroutinefunction(behavior):
                    response = await behavior(request, context)
                else:
                    response = behavior(request, context)

                duration_ms = (time.time() - start_time) * 1000

                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)

                if self.enable_logging:
                    logger.info(f"[gRPC] OK {method_name} | time={duration_ms:.2f}ms | peer={peer}")

                if log_entry:
                    await self._mark_log_success(
                        log_entry,
                        duration_ms=int(duration_ms),
                        response=response if self.log_response_data else None,
                    )

                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_end:
                    await self._publish_centrifugo_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        status="OK",
                    )

                return response

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)
                    self.metrics.record_error(method_name)

                if self.enable_logging:
                    logger.error(
                        f"[gRPC] ERR {method_name} | time={duration_ms:.2f}ms | "
                        f"error={type(e).__name__}: {e} | peer={peer}",
                        exc_info=True
                    )

                # Always log errors to DB (even if log_errors_only or sampled out)
                if self.enable_request_logger:
                    if log_entry:
                        await self._mark_log_error(log_entry, error=e, context=context, duration_ms=int(duration_ms))
                    elif self.log_errors_only:
                        # Create log entry for error if we didn't create one before
                        log_entry = await self._create_log_entry(
                            request_id=request_id,
                            service_name=service_name,
                            method_name=method_short,
                            full_method=method_name,
                            peer=peer,
                            user_agent=user_agent,
                            context=context,
                            request=request if self.log_request_data else None,
                        )
                        if log_entry:
                            await self._mark_log_error(log_entry, error=e, context=context, duration_ms=int(duration_ms))

                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_errors:
                    await self._publish_centrifugo_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        error=e,
                    )

                raise

        return wrapper

    def _wrap_unary_stream(
        self, behavior, method_name, service_name, method_short, peer, user_agent, request_id
    ):
        """Wrap unary-stream (server streaming) RPC."""
        async def wrapper(request, context):
            start_time = time.time()
            out_count = 0
            log_entry = None

            if self.enable_request_logger:
                log_entry = await self._create_log_entry(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_short,
                    full_method=method_name,
                    peer=peer,
                    user_agent=user_agent,
                    context=context,
                    request=request if self.log_request_data else None,
                )

            try:
                if self.enable_logging:
                    logger.info(f"[gRPC] --> {method_name} (server stream) | peer={peer}")

                async for response in behavior(request, context):
                    out_count += 1
                    yield response

                duration_ms = (time.time() - start_time) * 1000

                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)

                if self.enable_logging:
                    logger.info(
                        f"[gRPC] OK {method_name} (server stream) | "
                        f"messages={out_count} | time={duration_ms:.2f}ms | peer={peer}"
                    )

                if self.enable_request_logger and log_entry:
                    await self._mark_log_success(
                        log_entry,
                        duration_ms=int(duration_ms),
                        response_data={"message_count": out_count},
                    )

                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_end:
                    await self._publish_centrifugo_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        status="OK",
                        message_count=out_count,
                    )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)
                    self.metrics.record_error(method_name)

                if self.enable_logging:
                    logger.error(
                        f"[gRPC] ERR {method_name} (server stream) | "
                        f"messages={out_count} | time={duration_ms:.2f}ms | "
                        f"error={type(e).__name__}: {e} | peer={peer}",
                        exc_info=True
                    )

                if self.enable_request_logger and log_entry:
                    await self._mark_log_error(log_entry, error=e, context=context, duration_ms=int(duration_ms))

                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_errors:
                    await self._publish_centrifugo_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        error=e,
                        message_count=out_count,
                    )

                raise

        return wrapper

    def _wrap_stream_unary(
        self, behavior, method_name, service_name, method_short, peer, user_agent, request_id
    ):
        """Wrap stream-unary (client streaming) RPC."""
        async def wrapper(request_iterator, context):
            start_time = time.time()
            in_count = 0
            log_entry = None

            if self.enable_request_logger:
                log_entry = await self._create_log_entry(
                    request_id=request_id,
                    service_name=service_name,
                    method_name=method_short,
                    full_method=method_name,
                    peer=peer,
                    user_agent=user_agent,
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
                    logger.info(f"[gRPC] <-- {method_name} (client stream) | messages={in_count} | peer={peer}")

                response = await behavior(request_iter(), context)
                duration_ms = (time.time() - start_time) * 1000

                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)

                if self.enable_logging:
                    logger.info(
                        f"[gRPC] OK {method_name} (client stream) | "
                        f"messages={in_count} | time={duration_ms:.2f}ms | peer={peer}"
                    )

                if self.enable_request_logger and log_entry:
                    await self._mark_log_success(
                        log_entry,
                        duration_ms=int(duration_ms),
                        request_data={"message_count": in_count},
                        response=response if self.log_response_data else None,
                    )

                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_end:
                    await self._publish_centrifugo_event(
                        event_type="rpc_end",
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        status="OK",
                        message_count=in_count,
                    )

                return response

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                if self.enable_metrics:
                    self.metrics.record_response_time(method_name, duration_ms)
                    self.metrics.record_error(method_name)

                if self.enable_logging:
                    logger.error(
                        f"[gRPC] ERR {method_name} (client stream) | "
                        f"messages={in_count} | time={duration_ms:.2f}ms | "
                        f"error={type(e).__name__}: {e} | peer={peer}",
                        exc_info=True
                    )

                if self.enable_request_logger and log_entry:
                    await self._mark_log_error(log_entry, error=e, context=context, duration_ms=int(duration_ms))

                if self.enable_centrifugo and self.centrifugo_enabled and self.publish_errors:
                    await self._publish_centrifugo_error(
                        method=method_name,
                        service=service_name,
                        method_name=method_short,
                        peer=peer,
                        duration_ms=duration_ms,
                        error=e,
                        message_count=in_count,
                    )

                raise

        return wrapper

    # =========================================================================
    # Request Logger Database Methods
    # =========================================================================

    async def _create_log_entry(
        self,
        request_id: str,
        service_name: str,
        method_name: str,
        full_method: str,
        peer: str,
        user_agent: str,
        context: grpc.aio.ServicerContext,
        request=None,
    ):
        """Create log entry in database."""
        try:
            from ...models import GRPCRequestLog
            from ...auth import get_current_grpc_user, get_current_grpc_api_key

            user = get_current_grpc_user()
            api_key = get_current_grpc_api_key()
            client_ip = self._extract_ip_from_peer(peer)

            log_entry = await GRPCRequestLog.objects.acreate(
                request_id=request_id,
                service_name=service_name,
                method_name=method_name,
                full_method=full_method,
                user=user if user else None,
                api_key=api_key,
                is_authenticated=user is not None,
                client_ip=client_ip,
            )
            return log_entry

        except Exception as e:
            logger.error(f"Failed to create log entry: {e}", exc_info=True)
            return None

    async def _mark_log_success(
        self,
        log_entry,
        duration_ms: int,
        response=None,
        request_data: dict = None,
        response_data: dict = None,
    ):
        """Mark log entry as successful."""
        if log_entry is None:
            return

        try:
            from ...models import GRPCRequestLog

            if response:
                response_data = self._serialize_message(response)

            await GRPCRequestLog.objects.amark_success(
                log_entry,
                duration_ms=duration_ms,
                response_data=response_data,
            )
        except Exception as e:
            logger.error(f"Failed to mark log success: {e}", exc_info=True)

    async def _mark_log_error(
        self,
        log_entry,
        error: Exception,
        context: grpc.aio.ServicerContext,
        duration_ms: int,
    ):
        """Mark log entry as error."""
        if log_entry is None:
            return

        try:
            from ...models import GRPCRequestLog

            grpc_code = self._get_grpc_code(error, context)

            await GRPCRequestLog.objects.amark_error(
                log_entry,
                grpc_status_code=grpc_code,
                error_message=str(error),
                error_details={"type": type(error).__name__},
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.error(f"Failed to mark log error: {e}", exc_info=True)

    # =========================================================================
    # Centrifugo Methods
    # =========================================================================

    async def _publish_centrifugo_event(self, **data):
        """Publish event to Centrifugo."""
        if not self._centrifugo_publisher:
            return

        try:
            channel = self.channel_template.format(
                service=data.get('service', 'unknown'),
                method=data.get('method_name', 'unknown'),
            )

            await self._centrifugo_publisher.publish_grpc_event(
                channel=channel,
                method=data.get('method', ''),
                status=data.get('status', 'UNKNOWN'),
                duration_ms=data.get('duration_ms', 0.0),
                peer=data.get('peer'),
                metadata={
                    'event_type': data.get('event_type'),
                    **self.centrifugo_metadata,
                },
                **{k: v for k, v in data.items()
                   if k not in ['method', 'status', 'duration_ms', 'peer', 'event_type', 'service', 'method_name']},
            )

            if self.publish_to_telegram and data.get('status') == 'OK' and data.get('event_type') == 'rpc_end':
                await self._send_to_telegram(**data)

        except Exception as e:
            logger.warning(f"Failed to publish Centrifugo event: {e}")

    async def _publish_centrifugo_error(self, error: Exception, **data):
        """Publish error to Centrifugo."""
        if not self._centrifugo_publisher:
            return

        try:
            channel = self.error_channel_template.format(
                service=data.get('service', 'unknown'),
                method=data.get('method_name', 'unknown'),
            )

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
                    **self.centrifugo_metadata,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to publish Centrifugo error: {e}")

    async def _send_to_telegram(self, **data):
        """Send notification to Telegram."""
        if not self._telegram_service:
            return

        try:
            method = data.get('method', 'unknown')
            duration_ms = data.get('duration_ms', 0.0)
            peer = data.get('peer', 'unknown')

            message = f"`{method}` ({duration_ms:.2f}ms)"
            if peer and peer != 'unknown':
                message += f" - {peer}"

            from django_cfg.modules.django_telegram import TelegramParseMode
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._telegram_service.send_message(
                    message=message,
                    parse_mode=TelegramParseMode.MARKDOWN
                )
            )
        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    @staticmethod
    def _extract_peer(metadata) -> str:
        if metadata:
            for key, value in metadata:
                if key == "x-forwarded-for":
                    return value
        return "unknown"

    @staticmethod
    def _extract_user_agent(metadata) -> str:
        if metadata:
            metadata_dict = dict(metadata)
            return metadata_dict.get("user-agent", "unknown")
        return "unknown"

    @staticmethod
    def _parse_method(full_method: str) -> tuple[str, str]:
        parts = full_method.strip("/").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return full_method, "unknown"

    @staticmethod
    def _extract_ip_from_peer(peer: str) -> str | None:
        try:
            if ":" in peer:
                parts = peer.split(":")
                if len(parts) >= 3 and parts[0] in ["ipv4", "ipv6"]:
                    return parts[1]
                elif len(parts) == 2:
                    return parts[0]
        except Exception:
            pass
        return None

    @staticmethod
    def _get_grpc_code(error: Exception, context: grpc.aio.ServicerContext) -> str:
        try:
            if hasattr(error, "code"):
                return error.code().name
            if hasattr(context, "_state") and hasattr(context._state, "code"):
                return context._state.code.name
            return "UNKNOWN"
        except Exception:
            return "UNKNOWN"

    @staticmethod
    def _serialize_message(message) -> dict | None:
        try:
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(message)
        except Exception:
            return None


# =============================================================================
# Wrapped Handler
# =============================================================================

class _WrappedHandler:
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


__all__ = [
    "ObservabilityInterceptor",
    "MetricsCollector",
    "get_metrics",
    "reset_metrics",
]
