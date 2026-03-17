"""
django_grpc.services.interceptors.publishers — Fire-and-forget event publishers.

Handles Centrifugo and Telegram notifications from the observability interceptor.
All publish calls are non-blocking (asyncio.create_task).
"""

from __future__ import annotations

import asyncio
import dataclasses
import logging
from typing import Any

from django_cfg.modules.django_grpc.config.observability import ObservabilityConfig
from django_cfg.modules.django_centrifugo.services import get_centrifugo_publisher as _get_centrifugo_publisher
from django_cfg.modules.django_telegram import DjangoTelegram, TelegramParseMode
from .event_types import GrpcEventPayload, RpcEndEvent, RpcErrorEvent

logger = logging.getLogger(__name__)

# A-01 fix: strong references to fire-and-forget tasks.
# asyncio.create_task() returns a Task that can be GC-collected before it
# completes if no other reference is held. Storing tasks in this set keeps
# them alive; the done-callback removes them automatically.
_background_tasks: set[asyncio.Task] = set()


def _fire_and_forget(coro) -> asyncio.Task:
    """Schedule a coroutine as a fire-and-forget task, keeping a strong ref."""
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


def _get_obs_config() -> ObservabilityConfig:
    """Read observability config from the grpc_module singleton. Falls back to defaults."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import settings
        return settings.observability
    except Exception:
        return ObservabilityConfig()


class EventPublisher:
    """Handles publishing events to Centrifugo and Telegram (fire-and-forget)."""

    def __init__(
        self,
        centrifugo_enabled: bool = False,
        telegram_enabled: bool = False,
        is_development: bool = False,
        config: ObservabilityConfig | None = None,
    ):
        self.centrifugo_enabled = centrifugo_enabled
        self.is_development = is_development

        obs = config or _get_obs_config()

        # Centrifugo publish flags — read from config
        self.publish_start = obs.centrifugo.publish_start
        self.publish_end = obs.centrifugo.publish_end
        self.publish_errors = obs.centrifugo.publish_errors
        self.publish_stream_messages = obs.centrifugo.publish_stream_messages
        self.channel_template = obs.centrifugo.channel_template
        self.error_channel_template = obs.centrifugo.error_channel_template
        self.centrifugo_metadata: dict[str, Any] = {}

        # H-4: max retries for Centrifugo publish (default 3 from config)
        self._max_retries: int = obs.centrifugo.max_retries

        # H-1: semaphore to bound concurrent fire-and-forget publish tasks.
        # Without this, every stream message spawns an unbounded asyncio.Task.
        # The semaphore cap prevents memory/queue exhaustion under stream load.
        # Lazily created on first use to avoid event-loop issues at __init__ time.
        self._publish_semaphore: asyncio.Semaphore | None = None
        self._publish_semaphore_cap: int = obs.centrifugo.max_concurrent_publishes

        # Telegram settings — read from config; constructor arg overrides config.enabled
        self.telegram_enabled = telegram_enabled or obs.telegram.enabled
        self.telegram_exclude_methods = list(obs.telegram.exclude_methods)

        self._centrifugo_publisher: Any = None  # set by init_centrifugo(); None means disabled
        self._telegram_service: Any = None      # set by init_telegram(); None means disabled

    def _get_semaphore(self) -> asyncio.Semaphore:
        """H-1: lazy semaphore — created inside the running event loop."""
        if self._publish_semaphore is None:
            self._publish_semaphore = asyncio.Semaphore(self._publish_semaphore_cap)
        return self._publish_semaphore

    def init_centrifugo(self) -> None:
        """Initialize Centrifugo publisher. Called once at server startup."""
        if not self.centrifugo_enabled:
            return
        self._centrifugo_publisher = _get_centrifugo_publisher()

    def init_telegram(self) -> None:
        """Initialize Telegram service. Called once at server startup."""
        if not self.telegram_enabled:
            return
        svc = DjangoTelegram()
        if not svc.is_configured:
            self.telegram_enabled = False
        else:
            self._telegram_service = svc

    async def publish_event(self, event: GrpcEventPayload) -> None:
        """Fire-and-forget publish event to Centrifugo."""
        if not self._centrifugo_publisher:
            return
        _fire_and_forget(self._publish_event_async(event))

    async def _publish_event_async(self, event: GrpcEventPayload) -> None:
        if not self._centrifugo_publisher:
            return
        # H-1: acquire semaphore to cap concurrent publish tasks.
        async with self._get_semaphore():
            channel = self.channel_template.format(
                service=event.service,
                method=event.method_name,
            )
            # Extra fields beyond the base GrpcEventData (e.g. message_count, direction)
            base_fields = {"method", "service", "method_name", "peer", "event_type"}
            extra = {
                f.name: getattr(event, f.name)
                for f in dataclasses.fields(event)
                if f.name not in base_fields
                and f.name not in ("status", "duration_ms", "error_type", "error_message")
            }

            status = getattr(event, "status", "UNKNOWN")
            duration_ms = getattr(event, "duration_ms", 0.0)

            # H-4: retry loop up to max_retries on transient exceptions.
            last_exc: Exception | None = None
            for attempt in range(self._max_retries + 1):
                try:
                    await self._centrifugo_publisher.publish_grpc_event(
                        channel=channel,
                        method=event.method,
                        status=status,
                        duration_ms=duration_ms,
                        peer=event.peer,
                        metadata={
                            "event_type": event.event_type,
                            **self.centrifugo_metadata,
                        },
                        **extra,
                    )
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    if attempt < self._max_retries:
                        await asyncio.sleep(0.1 * (attempt + 1))
            if last_exc is not None:
                logger.debug(
                    "Centrifugo publish failed after %d attempts: %s",
                    self._max_retries + 1, last_exc,
                )
                return
            if (
                self.telegram_enabled
                and isinstance(event, RpcEndEvent)
                and event.status == "OK"
            ):
                await self._send_to_telegram(event)

    async def publish_error(self, event: RpcErrorEvent) -> None:
        """Fire-and-forget publish error event to Centrifugo."""
        if not self._centrifugo_publisher:
            return
        _fire_and_forget(self._publish_error_async(event))

    async def _publish_error_async(self, event: RpcErrorEvent) -> None:
        if not self._centrifugo_publisher:
            return
        # H-1: acquire semaphore; H-4: retry loop
        async with self._get_semaphore():
            channel = self.error_channel_template.format(
                service=event.service,
                method=event.method_name,
            )
            last_exc: Exception | None = None
            for attempt in range(self._max_retries + 1):
                try:
                    await self._centrifugo_publisher.publish_grpc_event(
                        channel=channel,
                        method=event.method,
                        status="ERROR",
                        duration_ms=event.duration_ms,
                        peer=event.peer,
                        metadata={
                            "event_type": "rpc_error",
                            "error": {
                                "type": event.error_type,
                                "message": event.error_message,
                            },
                            **self.centrifugo_metadata,
                        },
                    )
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    if attempt < self._max_retries:
                        await asyncio.sleep(0.1 * (attempt + 1))
            if last_exc is not None:
                logger.debug(
                    "Centrifugo error publish failed after %d attempts: %s",
                    self._max_retries + 1, last_exc,
                )

    async def _send_to_telegram(self, event: RpcEndEvent) -> None:
        if not self._telegram_service:
            return
        try:
            if event.method in self.telegram_exclude_methods and not self.is_development:
                return
            message = f"`{event.method}` ({event.duration_ms:.2f}ms)"
            if event.peer and event.peer != "unknown":
                message += f" - {event.peer}"
            await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: self._telegram_service.send_message(
                    message=message,
                    parse_mode=TelegramParseMode.MARKDOWN,
                ),
            )
        except Exception as e:
            logger.warning("Failed to send Telegram notification: %s", e)


__all__ = ["EventPublisher"]
