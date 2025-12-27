"""
Event publishers for gRPC interceptors.

Handles Centrifugo and Telegram notifications.
"""

import asyncio
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EventPublisher:
    """Handles publishing events to Centrifugo and Telegram."""

    def __init__(
        self,
        centrifugo_enabled: bool = False,
        telegram_enabled: bool = False,
        is_development: bool = False,
    ):
        self.centrifugo_enabled = centrifugo_enabled
        self.telegram_enabled = telegram_enabled
        self.is_development = is_development

        # Config defaults
        self.publish_start = False
        self.publish_end = True
        self.publish_errors = True
        self.publish_stream_messages = False
        self.channel_template = "grpc:{service}:{method}:meta"
        self.error_channel_template = "grpc:{service}:{method}:errors"
        self.centrifugo_metadata = {}
        self.telegram_exclude_methods = [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        ]

        self._centrifugo_publisher: Optional[Any] = None
        self._telegram_service: Optional[Any] = None

    def init_from_config(self, obs_config):
        """Initialize settings from GRPCObservabilityConfig."""
        if obs_config:
            self.publish_start = obs_config.centrifugo_publish_start
            self.publish_end = obs_config.centrifugo_publish_end
            self.publish_errors = obs_config.centrifugo_publish_errors
            self.publish_stream_messages = obs_config.centrifugo_publish_stream_messages
            self.channel_template = obs_config.centrifugo_channel_template
            self.error_channel_template = obs_config.centrifugo_error_channel_template
            self.centrifugo_metadata = obs_config.centrifugo_metadata
            self.telegram_exclude_methods = obs_config.telegram_exclude_methods

    def init_centrifugo(self):
        """Initialize Centrifugo publisher."""
        if not self.centrifugo_enabled:
            return

        try:
            from django_cfg.apps.integrations.centrifugo.services import get_centrifugo_publisher
            self._centrifugo_publisher = get_centrifugo_publisher()
            logger.info("EventPublisher: Centrifugo publisher initialized")
        except Exception as e:
            logger.warning(f"EventPublisher: Failed to init Centrifugo: {e}")
            self.centrifugo_enabled = False

    def init_telegram(self):
        """Initialize Telegram service."""
        if not self.telegram_enabled:
            return

        try:
            from django_cfg.modules.django_telegram import DjangoTelegram
            self._telegram_service = DjangoTelegram()
            if not self._telegram_service.is_configured:
                self.telegram_enabled = False
        except Exception as e:
            logger.warning(f"EventPublisher: Failed to init Telegram: {e}")
            self.telegram_enabled = False

    async def publish_event(self, **data):
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

            if self.telegram_enabled and data.get('status') == 'OK' and data.get('event_type') == 'rpc_end':
                await self._send_to_telegram(**data)

        except Exception as e:
            logger.warning(f"Failed to publish Centrifugo event: {e}")

    async def publish_error(self, error: Exception, **data):
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

            # Skip methods in the exclusion list
            # BUT allow them in development mode
            if method in self.telegram_exclude_methods:
                if not self.is_development:
                    logger.debug(f"Skipping Telegram notification for excluded method: {method}")
                    return
                else:
                    logger.debug(f"Allowing {method} in development mode")

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


__all__ = ["EventPublisher"]
