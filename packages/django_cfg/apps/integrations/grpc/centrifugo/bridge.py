"""
Centrifugo Bridge Mixin for gRPC Services.

Universal mixin that enables automatic publishing of gRPC stream events
to Centrifugo WebSocket channels using Pydantic configuration.
"""

import logging
import time
from datetime import datetime, timezone as tz
from typing import Dict, Optional, Any, TYPE_CHECKING

from .config import CentrifugoChannels, ChannelConfig
from .transformers import transform_protobuf_to_dict

if TYPE_CHECKING:
    from django_cfg.apps.integrations.centrifugo import CentrifugoClient

logger = logging.getLogger(__name__)


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

        # Auto-setup if config exists
        if self.centrifugo_channels:
            self._setup_from_pydantic_config(self.centrifugo_channels)

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

    def _initialize_centrifugo_client(self):
        """Lazy initialize Centrifugo client."""
        try:
            from django_cfg.apps.integrations.centrifugo import get_centrifugo_client
            self._centrifugo_client = get_centrifugo_client()
            logger.info(
                f"✅ Centrifugo bridge enabled with {len(self._centrifugo_mappings)} channels"
            )
        except Exception as e:
            logger.warning(f"⚠️ Centrifugo client not available: {e}")
            if not self._centrifugo_graceful:
                raise
            self._centrifugo_enabled = False

    async def _notify_centrifugo(
        self,
        message: Any,  # Protobuf message
        **context: Any  # Template variables for channel rendering
    ) -> bool:
        """
        Publish protobuf message to Centrifugo based on configured mappings.

        Automatically detects which field is set in the message and publishes
        to the corresponding channel.

        Args:
            message: Protobuf message (e.g., BotMessage with heartbeat/status/etc.)
            **context: Template variables for channel name rendering
                Example: bot_id='123', user_id='456'

        Returns:
            True if published successfully, False otherwise

        Example:
            ```python
            # message = BotMessage with heartbeat field set
            await self._notify_centrifugo(message, bot_id='bot-123')
            # → Publishes to channel: bot#bot-123#heartbeat
            ```
        """
        if not self._centrifugo_enabled or not self._centrifugo_client:
            return False

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

    async def _publish_field(
        self,
        field_name: str,
        message: Any,
        mapping: Dict[str, Any],
        context: dict
    ) -> bool:
        """
        Publish specific message field to Centrifugo.

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
                    logger.debug(f"⏱️ Rate limit: skipping {field_name} for {channel}")
                    return False
                self._centrifugo_last_publish[channel] = now

            # Get field value
            field_value = getattr(message, field_name)

            # Transform to dict
            data = self._transform_field(field_name, field_value, mapping, context)

            # Publish to Centrifugo
            await self._centrifugo_client.publish(
                channel=channel,
                data=data
            )

            logger.debug(f"✅ Published {field_name} to {channel}")
            return True

        except KeyError as e:
            logger.error(
                f"❌ Missing template variable in channel: {e}. "
                f"Template: {mapping['template']}, Context: {context}"
            )
            return False

        except Exception as e:
            logger.error(
                f"❌ Failed to publish {field_name} to Centrifugo: {e}",
                exc_info=True
            )
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
