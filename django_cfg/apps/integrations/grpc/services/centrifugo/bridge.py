"""
Centrifugo Bridge Mixin for gRPC Services.

Universal mixin that enables automatic publishing of gRPC stream events
to Centrifugo WebSocket channels using Pydantic configuration.

Enhanced with:
- Circuit Breaker pattern for resilience (aiobreaker - async-native)
- Automatic retry with exponential backoff for critical messages (tenacity)
- Dead Letter Queue (DLQ) for failed critical messages
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone as tz
from typing import Dict, Optional, Any, TYPE_CHECKING, Deque

from aiobreaker import CircuitBreaker
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from .config import CentrifugoChannels, ChannelConfig
from .transformers import transform_protobuf_to_dict

if TYPE_CHECKING:
    from django_cfg.apps.integrations.centrifugo import CentrifugoClient

logger = logging.getLogger(__name__)


@dataclass
class FailedMessage:
    """Failed Centrifugo message for retry queue."""
    channel: str
    data: Dict[str, Any]
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)
    field_name: str = ""


class CentrifugoBridgeMixin:
    """
    Universal mixin for publishing gRPC stream events to Centrifugo.

    Uses Pydantic models for type-safe, validated configuration.

    Features:
    - Type-safe Pydantic configuration
    - Automatic event publishing to WebSocket channels
    - Built-in protobuf → JSON transformation
    - Graceful degradation if Centrifugo unavailable
    - Custom transform functions support
    - Template-based channel naming
    - Per-channel rate limiting
    - Critical event bypassing

    Production-Ready Resilience (NEW):
    - Circuit Breaker pattern (fails after 5 errors, recovers after 60s)
    - Automatic retry with exponential backoff for critical messages (3 attempts)
    - Dead Letter Queue (DLQ) for failed critical messages (max 1000 messages)
    - Background retry loop (every 10 seconds)

    Usage:
        ```python
        from django_cfg.apps.integrations.grpc.mixins import (
            CentrifugoBridgeMixin,
            CentrifugoChannels,
            ChannelConfig,
        )

        class BotChannels(CentrifugoChannels):
            heartbeat: ChannelConfig = ChannelConfig(
                template='bot#{bot_id}#heartbeat',
                rate_limit=0.1
            )
            status: ChannelConfig = ChannelConfig(
                template='bot#{bot_id}#status',
                critical=True
            )

        class BotStreamingService(
            bot_streaming_service_pb2_grpc.BotStreamingServiceServicer,
            CentrifugoBridgeMixin
        ):
            centrifugo_channels = BotChannels()

            async def ConnectBot(self, request_iterator, context):
                async for message in request_iterator:
                    # Your business logic
                    await self._handle_message(bot_id, message)

                    # Auto-publish to Centrifugo (1 line!)
                    await self._notify_centrifugo(message, bot_id=bot_id)
        ```
    """

    # Class-level Pydantic config (optional, can be set in __init__)
    centrifugo_channels: Optional[CentrifugoChannels] = None

    def __init__(self):
        """Initialize Centrifugo bridge from Pydantic configuration."""
        super().__init__()

        # Instance attributes
        self._centrifugo_enabled: bool = False
        self._centrifugo_graceful: bool = True
        self._centrifugo_client: Optional['CentrifugoClient'] = None
        self._centrifugo_mappings: Dict[str, Dict[str, Any]] = {}
        self._centrifugo_last_publish: Dict[str, float] = {}

        # Circuit Breaker for Centrifugo resilience
        self._circuit_breaker = CircuitBreaker(
            fail_max=5,              # Open after 5 consecutive failures
            timeout_duration=timedelta(seconds=60),  # Stay open for 60 seconds
            name='centrifugo_bridge'
        )

        # Dead Letter Queue for failed critical messages (bounded to prevent memory issues)
        self._failed_messages: Deque[FailedMessage] = deque(maxlen=1000)
        self._retry_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Auto-setup if config exists
        if self.centrifugo_channels:
            logger.info(f"Setting up Centrifugo bridge with {len(self.centrifugo_channels.get_channel_mappings())} channels")
            self._setup_from_pydantic_config(self.centrifugo_channels)

            # Don't start background retry task here - will be started lazily on first publish
            # (avoids event loop issues during initialization)
        else:
            logger.debug("No centrifugo_channels configured, skipping Centrifugo bridge setup")

    def _setup_from_pydantic_config(self, config: CentrifugoChannels):
        """
        Setup Centrifugo bridge from Pydantic configuration.

        Args:
            config: CentrifugoChannels instance with channel mappings
        """
        self._centrifugo_enabled = config.enabled
        self._centrifugo_graceful = config.graceful_degradation

        # Extract channel mappings
        for field_name, channel_config in config.get_channel_mappings().items():
            if channel_config.enabled:
                self._centrifugo_mappings[field_name] = {
                    'template': channel_config.template,
                    'rate_limit': channel_config.rate_limit or config.default_rate_limit,
                    'critical': channel_config.critical,
                    'transform': channel_config.transform,
                    'metadata': channel_config.metadata,
                }

        # Initialize client if enabled
        if self._centrifugo_enabled and self._centrifugo_mappings:
            self._initialize_centrifugo_client()
        else:
            logger.debug(f"Skipping Centrifugo client init: enabled={self._centrifugo_enabled}, mappings={len(self._centrifugo_mappings)}")

    def _initialize_centrifugo_client(self):
        """Lazy initialize Centrifugo client."""
        try:
            # Use DirectCentrifugoClient for gRPC bridge (bypasses wrapper)
            # Gets settings from django-cfg config automatically via get_centrifugo_config()
            from django_cfg.apps.integrations.centrifugo import DirectCentrifugoClient

            self._centrifugo_client = DirectCentrifugoClient()
            logger.info(
                f"Centrifugo bridge enabled with {len(self._centrifugo_mappings)} channels"
            )
        except Exception as e:
            logger.warning(
                f"Centrifugo client not available: {e}. "
                "If running locally with Docker, try restarting Docker Desktop:\n"
                '  osascript -e \'quit app "Docker Desktop"\' && sleep 2 && open -a "Docker Desktop"'
            )
            if not self._centrifugo_graceful:
                raise
            self._centrifugo_enabled = False

    def _on_circuit_open(self, breaker, *args, **kwargs):
        """Called when circuit breaker opens (too many failures)."""
        logger.error(
            f"🔴 Centrifugo circuit breaker OPEN: {breaker.fail_counter} failures. "
            f"Blocking publishes for {breaker._reset_timeout}s"
        )

    def _on_circuit_close(self, breaker, *args, **kwargs):
        """Called when circuit breaker closes (recovered)."""
        logger.info(
            f"🟢 Centrifugo circuit breaker CLOSED: Service recovered"
        )

    def _ensure_retry_task_started(self):
        """Lazily start background retry task if not already running."""
        if self._retry_task is None and self._centrifugo_enabled:
            try:
                self._retry_task = asyncio.create_task(self._retry_failed_messages_loop())
                logger.debug("Started background retry task for failed messages")
            except RuntimeError:
                # No event loop available yet, will try again later
                logger.debug("Event loop not available yet, retry task will start on next attempt")

    async def _retry_failed_messages_loop(self):
        """Background task to retry failed critical messages."""
        try:
            while not self._shutdown_event.is_set():
                await asyncio.sleep(10)  # Retry every 10 seconds

                if not self._failed_messages:
                    continue

                queue_size = len(self._failed_messages)
                logger.info(f"Retrying {queue_size} failed Centrifugo messages...")

                # Process all failed messages
                retry_queue = list(self._failed_messages)
                self._failed_messages.clear()

                for msg in retry_queue:
                    if msg.retry_count >= 3:
                        # Max retries exceeded - drop message
                        logger.error(
                            f"Dropping message after 3 retries: {msg.field_name} → {msg.channel}"
                        )
                        continue

                    try:
                        # Retry with exponential backoff decorator
                        await self._publish_with_retry(msg.channel, msg.data)
                        logger.info(f"✅ Retry succeeded: {msg.field_name} → {msg.channel}")

                    except (RetryError, Exception) as e:
                        # Retry failed, re-queue with incremented counter
                        msg.retry_count += 1
                        self._failed_messages.append(msg)
                        logger.warning(
                            f"Retry {msg.retry_count}/3 failed for {msg.field_name}: {e}"
                        )

        except asyncio.CancelledError:
            logger.info("Retry loop cancelled, shutting down...")
        except Exception as e:
            logger.error(f"Error in retry loop: {e}", exc_info=True)

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        reraise=True,
    )
    async def _publish_with_retry(self, channel: str, data: Dict[str, Any]):
        """Publish to Centrifugo with automatic retry (exponential backoff)."""
        await self._centrifugo_client.publish(channel=channel, data=data)

    async def shutdown(self):
        """Gracefully shutdown the bridge (cancel retry task)."""
        if self._retry_task:
            self._shutdown_event.set()
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass
            logger.info("Centrifugo bridge shutdown complete")

    def _notify_centrifugo(
        self,
        message: Any,  # Protobuf message
        **context: Any  # Template variables for channel rendering
    ) -> None:
        """
        Publish protobuf message to Centrifugo (fire-and-forget, non-blocking).

        This is a non-blocking wrapper that creates a background task.
        Does NOT block the gRPC stream while waiting for Centrifugo response.

        Automatically detects which field is set in the message and publishes
        to the corresponding channel.

        Args:
            message: Protobuf message (e.g., BotMessage with heartbeat/status/etc.)
            **context: Template variables for channel name rendering
                Example: bot_id='123', user_id='456'

        Example:
            ```python
            # message = BotMessage with heartbeat field set
            self._notify_centrifugo(message, bot_id='bot-123')
            # ✅ Returns immediately, publishes in background
            # ✅ Does NOT block gRPC stream
            ```
        """
        if not self._centrifugo_enabled or not self._centrifugo_client:
            return

        # Fire-and-forget: create background task (non-blocking)
        task = asyncio.create_task(self._notify_centrifugo_async(message, **context))

        # Add error callback to prevent silent failures
        task.add_done_callback(self._handle_publish_task_error)

    async def _notify_centrifugo_async(
        self,
        message: Any,
        **context: Any
    ) -> bool:
        """
        Internal async method for publishing to Centrifugo.

        This is called by _notify_centrifugo() in a background task.
        Should not be called directly from gRPC stream handlers.
        """
        try:
            # Lazily start retry task on first publish
            self._ensure_retry_task_started()

            # Check each mapped field
            for field_name, mapping in self._centrifugo_mappings.items():
                if message.HasField(field_name):
                    return await self._publish_field(
                        field_name,
                        message,
                        mapping,
                        context
                    )

            return False

        except Exception as e:
            logger.error(f"Error in Centrifugo publish task: {e}", exc_info=True)
            return False

    def _handle_publish_task_error(self, task: asyncio.Task) -> None:
        """Error callback for background publish tasks."""
        try:
            # This will raise if the task raised an exception
            task.result()
        except asyncio.CancelledError:
            pass  # Task was cancelled, ignore
        except Exception as e:
            logger.error(f"Uncaught error in Centrifugo publish task: {e}", exc_info=True)

    async def _publish_field(
        self,
        field_name: str,
        message: Any,
        mapping: Dict[str, Any],
        context: dict
    ) -> bool:
        """
        Publish specific message field to Centrifugo with circuit breaker protection.

        Args:
            field_name: Name of the protobuf field
            message: Full protobuf message
            mapping: Channel mapping configuration
            context: Template variables

        Returns:
            True if published successfully
        """
        try:
            # Render channel from template
            channel = mapping['template'].format(**context)

            # Rate limiting check (unless critical)
            if not mapping['critical'] and mapping['rate_limit']:
                now = time.time()
                last = self._centrifugo_last_publish.get(channel, 0)
                if now - last < mapping['rate_limit']:
                    logger.debug(f"Rate limit: skipping {field_name} for {channel}")
                    return False
                self._centrifugo_last_publish[channel] = now

            # Get field value
            field_value = getattr(message, field_name)

            # Transform to dict
            data = self._transform_field(field_name, field_value, mapping, context)

            # Publish to Centrifugo with circuit breaker protection
            try:
                if mapping['critical']:
                    # Critical messages: circuit breaker + retry with exponential backoff
                    await self._circuit_breaker.call(
                        self._publish_with_retry,
                        channel,
                        data
                    )
                else:
                    # Non-critical: only circuit breaker, no retry
                    await self._circuit_breaker.call(
                        self._centrifugo_client.publish,
                        channel=channel,
                        data=data
                    )

                logger.debug(f"Published {field_name} to {channel}")
                return True

            except Exception as circuit_error:
                # Circuit breaker is open or publish failed
                error_name = type(circuit_error).__name__
                if 'CircuitBreakerError' in error_name or 'CircuitBreakerOpen' in error_name:
                    logger.warning(
                        f"Circuit breaker open, cannot publish {field_name} to {channel}"
                    )

                    if mapping['critical']:
                        # Queue critical message for background retry
                        self._failed_messages.append(FailedMessage(
                            channel=channel,
                            data=data,
                            retry_count=0,
                            field_name=field_name
                        ))
                        logger.info(f"Queued critical message for retry: {field_name}")

                    return False
                else:
                    # Re-raise if not circuit breaker error
                    raise

        except KeyError as e:
            logger.error(
                f"Missing template variable in channel: {e}. "
                f"Template: {mapping['template']}, Context: {context}"
            )
            return False

        except (RetryError, Exception) as e:
            # Publish failed even after retries
            logger.error(
                f"Failed to publish {field_name} to Centrifugo: {e}",
                exc_info=True if not isinstance(e, RetryError) else False
            )

            # Queue critical messages for background retry
            if mapping['critical']:
                self._failed_messages.append(FailedMessage(
                    channel=channel,
                    data=data,
                    retry_count=0,
                    field_name=field_name
                ))
                logger.warning(f"Queued failed critical message: {field_name}")

            if not self._centrifugo_graceful:
                raise

            return False

    def _transform_field(
        self,
        field_name: str,
        field_value: Any,
        mapping: Dict[str, Any],
        context: dict
    ) -> dict:
        """
        Transform protobuf field to JSON-serializable dict.

        Args:
            field_name: Field name
            field_value: Protobuf message field value
            mapping: Channel mapping with optional transform function
            context: Template context variables

        Returns:
            JSON-serializable dictionary
        """
        # Use custom transform if provided
        if mapping['transform']:
            data = mapping['transform'](field_name, field_value)
        else:
            # Default protobuf → dict transform
            data = transform_protobuf_to_dict(field_value)

        # Add metadata
        data['type'] = field_name
        data['timestamp'] = datetime.now(tz.utc).isoformat()

        # Merge channel metadata
        if mapping['metadata']:
            for key, value in mapping['metadata'].items():
                if key not in data:
                    data[key] = value

        # Add context variables (bot_id, user_id, etc.)
        for key, value in context.items():
            if key not in data:
                data[key] = value

        return data


__all__ = ["CentrifugoBridgeMixin"]
