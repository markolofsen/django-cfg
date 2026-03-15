"""
Centrifugo auto-publishing integration.

Automatically publishes protobuf messages to Centrifugo WebSocket channels.
Works for both incoming messages (Client → Server) and outgoing commands (Server → Client).

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import logging
from typing import Optional
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToDict

from .circuit_breaker import CentrifugoCircuitBreaker

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
logger = logging.getLogger("grpc_streaming.centrifugo")


class CentrifugoPublisher:
    """
    Publisher for auto-publishing protobuf messages to Centrifugo.

    Features:
    - Auto-detects field names from protobuf messages
    - Generates channel names automatically
    - Includes circuit breaker for resilience
    - Non-blocking (fire-and-forget)
    """

    def __init__(
        self,
        centrifugo_publisher,
        channel_prefix: str = "grpc",
        circuit_breaker_enabled: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
        enable_logging: bool = True
    ):
        """
        Initialize Centrifugo publisher.

        Args:
            centrifugo_publisher: get_centrifugo_publisher() instance
            channel_prefix: Prefix for channel names (default: "grpc")
            circuit_breaker_enabled: Enable circuit breaker (default: True)
            circuit_breaker_threshold: Max failures before opening circuit
            circuit_breaker_timeout: Seconds to wait before testing recovery
            enable_logging: Enable logging
        """
        self.centrifugo = centrifugo_publisher
        self.channel_prefix = channel_prefix
        self.enable_logging = enable_logging

        # Circuit breaker
        self.circuit_breaker: Optional[CentrifugoCircuitBreaker] = None
        if circuit_breaker_enabled:
            self.circuit_breaker = CentrifugoCircuitBreaker(
                failure_threshold=circuit_breaker_threshold,
                recovery_timeout=circuit_breaker_timeout,
                success_threshold=2,
                enable_logging=enable_logging
            )

    async def publish_message(
        self,
        client_id: str,
        message: Message
    ) -> bool:
        """
        Publish incoming message (Client → Server).

        Channel format: {prefix}#{client_id}#{field_name}

        Args:
            client_id: Client UUID
            message: Protobuf message

        Returns:
            True if published successfully
        """
        return await self._publish(client_id, message, is_command=False)

    async def publish_command(
        self,
        client_id: str,
        command: Message
    ) -> bool:
        """
        Publish outgoing command (Server → Client).

        Channel format: {prefix}#{client_id}#command_{field_name}

        Args:
            client_id: Client UUID
            command: Protobuf command

        Returns:
            True if published successfully
        """
        return await self._publish(client_id, command, is_command=True)

    async def _publish(
        self,
        client_id: str,
        message: Message,
        is_command: bool
    ) -> bool:
        """
        Internal publish method.

        Args:
            client_id: Client UUID
            message: Protobuf message
            is_command: True for commands (Server → Client), False for messages (Client → Server)

        Returns:
            True if published successfully
        """
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_execute():
            if self.enable_logging:
                logger.debug(
                    f"⛔ Circuit breaker OPEN, skipping Centrifugo publish for {client_id[:8]}..."
                )
            return False

        try:
            # Extract field name from protobuf
            field_name = self._extract_field_name(message)
            if not field_name:
                return False

            # Build channel name
            if is_command:
                channel = f"{self.channel_prefix}#{client_id}#command_{field_name}"
                event_type = f"grpc_command_{field_name}"
            else:
                channel = f"{self.channel_prefix}#{client_id}#{field_name}"
                event_type = f"grpc_message_{field_name}"

            # Convert protobuf to dict
            message_dict = MessageToDict(
                message,
                preserving_proto_field_name=True,
                always_print_fields_with_no_presence=False
            )

            # Publish to Centrifugo
            await self.centrifugo.publish_custom(
                channel=channel,
                event_type=event_type,
                data=message_dict
            )

            # Record success
            if self.circuit_breaker:
                self.circuit_breaker.record_success()

            if self.enable_logging:
                direction = "→" if is_command else "←"
                logger.debug(
                    f"📡 Published {direction} {field_name} to {channel[:40]}..."
                )

            return True

        except Exception as e:
            # Record failure
            if self.circuit_breaker:
                self.circuit_breaker.record_failure(e)

            if self.enable_logging:
                logger.warning(
                    f"⚠️  Failed to publish to Centrifugo: {e}"
                )

            return False

    def _extract_field_name(self, message: Message) -> Optional[str]:
        """
        Extract field name from protobuf message.

        Tries WhichOneof() first, then falls back to ListFields().

        Args:
            message: Protobuf message

        Returns:
            Field name or None
        """
        # Try WhichOneof for oneof fields
        if hasattr(message, 'WhichOneof'):
            for oneof in message.DESCRIPTOR.oneofs:
                which = message.WhichOneof(oneof.name)
                if which:
                    return which

        # Fallback: ListFields
        if hasattr(message, 'ListFields'):
            fields = message.ListFields()
            if fields:
                return fields[0][0].name

        return None

    def get_stats(self) -> dict:
        """
        Get publisher statistics.

        Returns:
            Dictionary with circuit breaker stats
        """
        if self.circuit_breaker:
            return self.circuit_breaker.get_stats()
        return {}


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'CentrifugoPublisher',
]
