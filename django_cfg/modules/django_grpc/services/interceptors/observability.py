"""
django_grpc.services.interceptors.observability — Consolidated observability interceptor.

Replaces 4 separate interceptors (Metrics, Logging, RequestLogger, Centrifugo) with ONE.
Uses a single counting_iterator — no nested wrapping, no buffer backpressure.

Architecture constraint: max 2 interceptors that wrap request_iterator.
    Auth → ObservabilityInterceptor → Handler   (only 2 layers!)

D1 logging is non-blocking: enqueue_log() puts entries in asyncio.Queue,
a background worker (started in apps.py) batch-flushes to D1.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

import grpc
import grpc.aio
from django.db import close_old_connections

from .event_types import RpcEndEvent, RpcErrorEvent, RpcStartEvent, StreamMessageEvent
from .metrics import get_metrics_collector
from .publishers import EventPublisher
from .utils import extract_peer, extract_traceparent, extract_user_agent, is_centrifugo_configured, parse_method
from .wrapped_handler import WrappedHandler

logger = logging.getLogger(__name__)


class ObservabilityInterceptor(grpc.aio.ServerInterceptor):
    """
    Single gRPC interceptor for all observability concerns:
    - In-memory metrics (always-on, zero cost)
    - Structured logging
    - Async D1 request logging (non-blocking enqueue)
    - Centrifugo publish (fire-and-forget)
    - Telegram notifications (optional)

    ONE counting_iterator in stream handlers — no buffer accumulation.
    """

    def __init__(
        self,
        centrifugo_client: Any | None = None,
        enable_request_logging: bool = True,
    ):
        self._centrifugo_client = centrifugo_client
        self.enable_request_logging = enable_request_logging

        self.metrics = get_metrics_collector()

        # Auto-detect Centrifugo if not explicitly provided
        centrifugo_enabled = centrifugo_client is not None or is_centrifugo_configured()

        from django_cfg.modules.django_grpc.services.management.config_helper import (
            is_development as _is_development,
        )
        obs_config = None
        try:
            from django_cfg.core.config import get_current_config
            from django_cfg.modules.django_grpc.__cfg__ import settings as grpc_settings
            cfg = get_current_config()
            if cfg:
                centrifugo = getattr(cfg, "centrifugo", None)
                if centrifugo and centrifugo.enabled:
                    centrifugo_enabled = True
            obs_config = grpc_settings.observability
        except Exception as e:
            logger.warning("Failed to load observability config, using defaults: %s", e)

        self.publisher = EventPublisher(
            centrifugo_enabled=centrifugo_enabled,
            is_development=_is_development(),
            config=obs_config,
        )
        self.publisher.init_centrifugo()
        self.publisher.init_telegram()

    # ------------------------------------------------------------------
    # Core intercept
    # ------------------------------------------------------------------

    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Any],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        # J-4 fix: offload close_old_connections() to a thread.
        # psycopg2 close() can issue a synchronous rollback — a blocking I/O call
        # on the event loop thread that stalls all concurrent RPCs while it runs.
        # asyncio.to_thread() delegates it to the default thread pool executor.
        #
        # J-6 — IMPORTANT Django database configuration requirement:
        # gRPC workers are long-lived async processes that share a single OS thread.
        # Django's persistent connections (CONN_MAX_AGE > 0) are NOT safe in this
        # environment: a connection can be reused across requests on different
        # coroutines while another coroutine is mid-transaction, causing data
        # corruption or "connection already closed" errors.
        #
        # REQUIRED in your Django settings for any app running `rungrpc`:
        #
        #   DATABASES = {
        #       "default": {
        #           ...
        #           "CONN_MAX_AGE": 0,   # ← disable persistent connections
        #       }
        #   }
        #
        # With CONN_MAX_AGE=0, Django opens a fresh connection per-request and
        # close_old_connections() becomes a fast no-op. Without it, stale
        # connections held across the event-loop boundary can cause subtle bugs
        # that are extremely difficult to reproduce.
        await asyncio.to_thread(close_old_connections)

        method = handler_call_details.method
        metadata = handler_call_details.invocation_metadata
        peer = extract_peer(metadata)
        user_agent = extract_user_agent(metadata)
        traceparent = extract_traceparent(metadata)  # H-6: W3C trace propagation
        service_name, method_short = parse_method(method)
        request_id = str(uuid.uuid4())

        self.metrics.record_request(method)
        if traceparent:
            logger.info("[gRPC] --> %s | peer=%s | traceparent=%s", method, peer, traceparent)
        else:
            logger.info("[gRPC] --> %s | peer=%s", method, peer)

        if self.publisher.centrifugo_enabled and self.publisher.publish_start:
            await self.publisher.publish_event(RpcStartEvent(
                method=method,
                service=service_name,
                method_name=method_short,
                peer=peer,
            ))

        handler = await continuation(handler_call_details)
        if handler is None:
            logger.warning("[gRPC] No handler found for %s", method)
            return None  # type: ignore[return-value]

        ctx = _WrapCtx(
            method=method,
            service_name=service_name,
            method_short=method_short,
            peer=peer,
            user_agent=user_agent,
            traceparent=traceparent,
            request_id=request_id,
        )
        return self._wrap(handler, ctx)

    # ------------------------------------------------------------------
    # Handler dispatch
    # ------------------------------------------------------------------

    def _wrap(self, handler: grpc.RpcMethodHandler, ctx: _WrapCtx) -> grpc.RpcMethodHandler:
        # WrappedHandler is duck-type compatible with grpc.RpcMethodHandler (same
        # attributes) but Pyright can't verify structural compatibility because grpc
        # stubs don't expose RpcMethodHandler as a Protocol.  The ignore tags are
        # intentional — removing them would require making WrappedHandler inherit
        # from grpc.RpcMethodHandler which would pull in the full grpc type hierarchy.
        if handler.stream_stream:
            return WrappedHandler(handler, stream_stream=self._wrap_bidi(handler.stream_stream, ctx))  # type: ignore[return-value]
        if handler.unary_unary:
            return WrappedHandler(handler, unary_unary=self._wrap_unary_unary(handler.unary_unary, ctx))  # type: ignore[return-value]
        if handler.unary_stream:
            return WrappedHandler(handler, unary_stream=self._wrap_unary_stream(handler.unary_stream, ctx))  # type: ignore[return-value]
        if handler.stream_unary:
            return WrappedHandler(handler, stream_unary=self._wrap_stream_unary(handler.stream_unary, ctx))  # type: ignore[return-value]
        return handler

    # ------------------------------------------------------------------
    # Wrappers
    # ------------------------------------------------------------------

    def _wrap_bidi(self, behavior, ctx: _WrapCtx):
        """Bidirectional streaming — ONE counting_iterator, no nesting."""
        async def wrapper(request_iterator, context):
            start_time = time.monotonic()
            in_count = 0
            out_count = 0

            # G-3: register disconnect callback so we log client disconnects
            # that happen mid-stream without raising an exception in the handler.
            # add_callback() schedules the callable on the event loop when the
            # RPC is cancelled / the client disconnects.
            _disconnect_logged = False

            def _on_disconnect():
                nonlocal _disconnect_logged
                if not _disconnect_logged:
                    _disconnect_logged = True
                    logger.info(
                        "[gRPC] client disconnected mid-stream: %s | peer=%s",
                        ctx.method, ctx.peer,
                    )

            try:
                context.add_callback(_on_disconnect)
            except Exception:
                pass  # add_callback() unavailable in some test stubs

            # Log request start (pending row)
            if self.enable_request_logging:
                self._enqueue_log_pending(ctx)

            async def counting_iterator():
                nonlocal in_count
                async for req in request_iterator:
                    in_count += 1
                    try:
                        msg_type = req.WhichOneof("payload") if hasattr(req, "WhichOneof") else "msg"
                    except Exception:
                        msg_type = "msg"
                    logger.debug("[gRPC] <-- %s #%d %s", ctx.method, in_count, msg_type)

                    if self.publisher.centrifugo_enabled and self.publisher.publish_stream_messages:
                        await self.publisher.publish_event(StreamMessageEvent(
                            method=ctx.method,
                            service=ctx.service_name,
                            method_name=ctx.method_short,
                            peer=ctx.peer,
                            message_count=in_count,
                            direction="client_to_server",
                        ))
                    yield req
                    await asyncio.sleep(0)  # yield event loop to prevent output loop starvation

            try:
                logger.info("[gRPC] <-> %s (bidi) | peer=%s", ctx.method, ctx.peer)
                async for response in behavior(counting_iterator(), context):
                    out_count += 1
                    if self.publisher.centrifugo_enabled and self.publisher.publish_stream_messages:
                        await self.publisher.publish_event(StreamMessageEvent(
                            method=ctx.method,
                            service=ctx.service_name,
                            method_name=ctx.method_short,
                            peer=ctx.peer,
                            message_count=out_count,
                            direction="server_to_client",
                        ))
                    yield response

                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_success(ctx, duration_ms, in_count=in_count, out_count=out_count, is_stream=True)

            except Exception as e:
                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_error(ctx, e, context, duration_ms, in_count=in_count, out_count=out_count, is_stream=True)
                raise

        return wrapper

    def _wrap_unary_unary(self, behavior, ctx: _WrapCtx):
        async def wrapper(request, context):
            start_time = time.monotonic()
            if self.enable_request_logging:
                self._enqueue_log_pending(ctx)
            try:
                response = await behavior(request, context)
                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_success(ctx, duration_ms)
                return response
            except Exception as e:
                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_error(ctx, e, context, duration_ms)
                raise
        return wrapper

    def _wrap_unary_stream(self, behavior, ctx: _WrapCtx):
        async def wrapper(request, context):
            start_time = time.monotonic()
            out_count = 0
            if self.enable_request_logging:
                self._enqueue_log_pending(ctx)
            # G-3: disconnect callback for server-streaming RPCs
            try:
                context.add_callback(lambda: logger.info(
                    "[gRPC] client disconnected (server-stream): %s | peer=%s", ctx.method, ctx.peer
                ))
            except Exception:
                pass
            try:
                logger.info("[gRPC] --> %s (server stream) | peer=%s", ctx.method, ctx.peer)
                async for response in behavior(request, context):
                    out_count += 1
                    yield response
                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_success(ctx, duration_ms, out_count=out_count, is_stream=True)
            except Exception as e:
                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_error(ctx, e, context, duration_ms, out_count=out_count, is_stream=True)
                raise
        return wrapper

    def _wrap_stream_unary(self, behavior, ctx: _WrapCtx):
        async def wrapper(request_iterator, context):
            start_time = time.monotonic()
            in_count = 0
            if self.enable_request_logging:
                self._enqueue_log_pending(ctx)
            # G-3: disconnect callback for client-streaming RPCs
            try:
                context.add_callback(lambda: logger.info(
                    "[gRPC] client disconnected (client-stream): %s | peer=%s", ctx.method, ctx.peer
                ))
            except Exception:
                pass

            # Pass a counting pass-through generator instead of buffering the full stream
            async def counting_iterator():
                nonlocal in_count
                async for req in request_iterator:
                    in_count += 1
                    yield req

            try:
                response = await behavior(counting_iterator(), context)
                duration_ms = int((time.monotonic() - start_time) * 1000)
                logger.info("[gRPC] <-- %s (client stream) | messages=%d | peer=%s", ctx.method, in_count, ctx.peer)
                await self._on_success(ctx, duration_ms, in_count=in_count, is_stream=True)
                return response
            except Exception as e:
                duration_ms = int((time.monotonic() - start_time) * 1000)
                await self._on_error(ctx, e, context, duration_ms, in_count=in_count, is_stream=True)
                raise
        return wrapper

    # ------------------------------------------------------------------
    # Success / error callbacks
    # ------------------------------------------------------------------

    async def _on_success(
        self,
        ctx: _WrapCtx,
        duration_ms: int,
        in_count: int = 0,
        out_count: int = 0,
        is_stream: bool = False,
    ) -> None:
        self.metrics.record_response_time(ctx.method, float(duration_ms))
        self.metrics.record_request_end(ctx.method)  # G-6: decrement in-flight gauge
        if in_count:
            self.metrics.record_messages_received(ctx.method, in_count)  # H-5
        if out_count:
            self.metrics.record_messages_sent(ctx.method, out_count)  # H-5

        if is_stream:
            logger.info(
                "[gRPC] OK %s (stream) | in=%d out=%d | time=%dms | peer=%s",
                ctx.method, in_count, out_count, duration_ms, ctx.peer,
            )
        else:
            logger.info("[gRPC] OK %s | time=%dms | peer=%s", ctx.method, duration_ms, ctx.peer)

        if self.enable_request_logging:
            self._enqueue_log_complete(ctx, duration_ms=duration_ms, status="success")

        if self.publisher.centrifugo_enabled and self.publisher.publish_end:
            await self.publisher.publish_event(RpcEndEvent(
                method=ctx.method,
                service=ctx.service_name,
                method_name=ctx.method_short,
                peer=ctx.peer,
                duration_ms=float(duration_ms),
                status="OK",
                in_message_count=in_count,
                out_message_count=out_count,
            ))

    async def _on_error(
        self,
        ctx: _WrapCtx,
        error: Exception,
        context: grpc.aio.ServicerContext,
        duration_ms: int,
        in_count: int = 0,
        out_count: int = 0,
        is_stream: bool = False,
    ) -> None:
        self.metrics.record_response_time(ctx.method, float(duration_ms))
        self.metrics.record_error(ctx.method)
        self.metrics.record_request_end(ctx.method)  # G-6: decrement in-flight gauge
        if in_count:
            self.metrics.record_messages_received(ctx.method, in_count)  # H-5
        if out_count:
            self.metrics.record_messages_sent(ctx.method, out_count)  # H-5

        if is_stream:
            logger.error(
                "[gRPC] ERR %s (stream) | in=%d out=%d | time=%dms | error=%s: %s | peer=%s",
                ctx.method, in_count, out_count, duration_ms, type(error).__name__, error, ctx.peer,
                exc_info=True,
            )
        else:
            logger.error(
                "[gRPC] ERR %s | time=%dms | error=%s: %s | peer=%s",
                ctx.method, duration_ms, type(error).__name__, error, ctx.peer,
                exc_info=True,
            )

        if self.enable_request_logging:
            from .utils import get_grpc_code
            grpc_code = get_grpc_code(error, context)
            self._enqueue_log_complete(
                ctx,
                duration_ms=duration_ms,
                status="error",
                grpc_status_code=grpc_code,
                error_message=str(error),
            )

        if self.publisher.centrifugo_enabled and self.publisher.publish_errors:
            await self.publisher.publish_error(RpcErrorEvent(
                method=ctx.method,
                service=ctx.service_name,
                method_name=ctx.method_short,
                peer=ctx.peer,
                duration_ms=float(duration_ms),
                in_message_count=in_count,
                out_message_count=out_count,
                error_type=type(error).__name__,
                error_message=str(error),
            ))

    # ------------------------------------------------------------------
    # D1 log helpers (non-blocking)
    # ------------------------------------------------------------------

    def _enqueue_log_pending(self, ctx: _WrapCtx) -> None:
        """Enqueue the initial 'pending' log row to the D1 async worker."""
        try:
            from django_cfg.modules.django_grpc.events.log_worker import GrpcLogEntry, enqueue_log
            from django_cfg.modules.django_grpc.events.types import GrpcRequestStatus

            user_row = _get_current_user()
            enqueue_log(GrpcLogEntry(
                request_id=ctx.request_id,
                service_name=ctx.service_name,
                method_name=ctx.method_short,
                full_method=ctx.method,
                status=GrpcRequestStatus.PENDING.value,
                duration_ms=None,
                user_id=user_row.get("user_id") if user_row else None,
                is_authenticated=1 if user_row else 0,
                client_ip=None,
                grpc_status_code=None,
                error_message=None,
                created_at=datetime.now(timezone.utc).isoformat(),
                completed_at=None,
            ))
        except Exception as e:
            logger.debug("Log enqueue (pending) failed (non-fatal): %s", e)

    def _enqueue_log_complete(
        self,
        ctx: _WrapCtx,
        duration_ms: int,
        status: str,
        grpc_status_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Enqueue the completion log row (same request_id, second row in D1)."""
        try:
            from django_cfg.modules.django_grpc.events.log_worker import GrpcLogEntry, enqueue_log

            user_row = _get_current_user()
            now = datetime.now(timezone.utc).isoformat()
            enqueue_log(GrpcLogEntry(
                request_id=ctx.request_id,
                service_name=ctx.service_name,
                method_name=ctx.method_short,
                full_method=ctx.method,
                status=status,
                duration_ms=duration_ms,
                user_id=user_row.get("user_id") if user_row else None,
                is_authenticated=1 if user_row else 0,
                client_ip=None,
                grpc_status_code=grpc_status_code,
                error_message=error_message,
                created_at=now,
                completed_at=now,
            ))
        except Exception as e:
            logger.debug("Log enqueue (complete) failed (non-fatal): %s", e)


def _get_current_user():
    """Read current user from contextvars (set by JWTAuthInterceptor)."""
    try:
        from django_cfg.modules.django_grpc.services.auth.context import _grpc_user_var
        return _grpc_user_var.get()
    except Exception:
        return None


class _WrapCtx:
    """Immutable per-request context for handler wrappers."""

    __slots__ = ("method", "service_name", "method_short", "peer", "user_agent", "traceparent", "request_id")

    def __init__(
        self,
        method: str,
        service_name: str,
        method_short: str,
        peer: str,
        user_agent: str,
        traceparent: str | None,
        request_id: str,
    ):
        self.method = method
        self.service_name = service_name
        self.method_short = method_short
        self.peer = peer
        self.user_agent = user_agent
        self.traceparent = traceparent  # H-6: W3C traceparent for trace propagation
        self.request_id = request_id


# Re-export metrics helpers for convenience
from .metrics import get_metrics, reset_metrics  # noqa: E402

__all__ = [
    "ObservabilityInterceptor",
    "get_metrics",
    "reset_metrics",
]
