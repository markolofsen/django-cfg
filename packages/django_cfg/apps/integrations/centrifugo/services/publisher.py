"""
Centrifugo Publishing Service.

Unified high-level API for publishing events to Centrifugo.
Abstracts away CentrifugoClient details and provides domain-specific methods.

Usage:
    >>> from django_cfg.apps.integrations.centrifugo.services import CentrifugoPublisher
    >>>
    >>> publisher = CentrifugoPublisher()
    >>>
    >>> # Publish gRPC event
    >>> await publisher.publish_grpc_event(
    ...     channel="grpc#bot#123#status",
    ...     method="/bot.BotService/Start",
    ...     status="OK",
    ...     duration_ms=150
    ... )
    >>>
    >>> # Publish demo event
    >>> await publisher.publish_demo_event(
    ...     channel="grpc#demo#test",
    ...     metadata={"test": True}
    ... )
"""

from __future__ import annotations

from datetime import datetime, timezone as tz
from typing import Any, Dict, Optional

from django_cfg.utils import get_logger

from ..services.client import (
    CentrifugoClient,
    DirectCentrifugoClient,
    PublishResponse,
    get_centrifugo_client,
    get_direct_centrifugo_client,
)

logger = get_logger("centrifugo.publisher")


class CentrifugoPublisher:
    """
    High-level publishing service for Centrifugo events.

    Provides domain-specific methods that abstract away low-level client details.
    All methods are async and handle errors gracefully.

    Features:
    - Unified API for all Centrifugo publishing
    - Automatic timestamp injection
    - Type-safe event metadata
    - Error handling and logging
    - Easy to mock for testing
    """

    def __init__(
        self,
        client: Optional[CentrifugoClient | DirectCentrifugoClient] = None,
        use_direct: bool = True,
    ):
        """
        Initialize publisher.

        Args:
            client: Optional client instance (CentrifugoClient or DirectCentrifugoClient)
            use_direct: Use DirectCentrifugoClient (bypass wrapper, default=True)
        """
        if client:
            self._client = client
            logger.debug("CentrifugoPublisher initialized with custom client")
        elif use_direct:
            # Use direct client (no wrapper, no DB logging)
            self._client = get_direct_centrifugo_client()
            logger.debug("CentrifugoPublisher initialized with DirectCentrifugoClient")
        else:
            # Use wrapper client (with auth & DB logging)
            self._client = get_centrifugo_client()
            logger.debug("CentrifugoPublisher initialized with CentrifugoClient (wrapper)")

    @property
    def client(self) -> CentrifugoClient | DirectCentrifugoClient:
        """Get underlying client instance."""
        return self._client

    async def publish_grpc_event(
        self,
        channel: str,
        method: str,
        status: str = "OK",
        duration_ms: float = 0.0,
        peer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ) -> PublishResponse:
        """
        Publish gRPC event (interceptor-style metadata).

        Args:
            channel: Centrifugo channel (e.g., "grpc#bot#123#status")
            method: Full gRPC method name (e.g., "/bot.BotService/Start")
            status: RPC status code (default: "OK")
            duration_ms: RPC duration in milliseconds
            peer: Client peer address
            metadata: Additional metadata dict
            **extra: Additional fields

        Returns:
            PublishResponse with result

        Example:
            >>> await publisher.publish_grpc_event(
            ...     channel="grpc#bot#123#status",
            ...     method="/bot.BotService/Start",
            ...     status="OK",
            ...     duration_ms=150,
            ...     peer="127.0.0.1:50051"
            ... )
        """
        # Parse method name
        service_name = None
        method_name = None
        if method.startswith("/") and "/" in method[1:]:
            parts = method[1:].split("/")
            service_name = parts[0]
            method_name = parts[1]

        # Build event data
        event_data = {
            "event_type": "grpc_event",
            "method": method,
            "status": status,
            "timestamp": datetime.now(tz.utc).isoformat(),
        }

        if service_name:
            event_data["service"] = service_name
        if method_name:
            event_data["method_name"] = method_name
        if duration_ms:
            event_data["duration_ms"] = duration_ms
        if peer:
            event_data["peer"] = peer
        if metadata:
            event_data.update(metadata)
        if extra:
            event_data.update(extra)

        logger.debug(f"Publishing gRPC event: {channel} ({method})")

        # DirectCentrifugoClient uses simpler API
        if isinstance(self._client, DirectCentrifugoClient):
            return await self._client.publish(channel=channel, data=event_data)
        else:
            return await self._client.publish(channel=channel, data=event_data)

    async def publish_demo_event(
        self,
        channel: str,
        metadata: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ) -> PublishResponse:
        """
        Publish demo/test event.

        Args:
            channel: Centrifugo channel
            metadata: Event metadata
            **extra: Additional fields

        Returns:
            PublishResponse with result

        Example:
            >>> await publisher.publish_demo_event(
            ...     channel="grpc#demo#test",
            ...     metadata={"test": True, "source": "demo.py"}
            ... )
        """
        event_data = {
            "event_type": "demo_event",
            "timestamp": datetime.now(tz.utc).isoformat(),
            "test_mode": True,
        }

        if metadata:
            event_data.update(metadata)
        if extra:
            event_data.update(extra)

        logger.debug(f"Publishing demo event: {channel}")

        if isinstance(self._client, DirectCentrifugoClient):
            return await self._client.publish(channel=channel, data=event_data)
        else:
            return await self._client.publish(channel=channel, data=event_data)

    async def publish_notification(
        self,
        channel: str,
        title: str,
        message: str,
        level: str = "info",
        user: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ) -> PublishResponse:
        """
        Publish user notification.

        Args:
            channel: Centrifugo channel (e.g., "notifications#user#123")
            title: Notification title
            message: Notification message
            level: Notification level (info, warning, error, success)
            user: Django User instance
            metadata: Additional metadata
            **extra: Additional fields

        Returns:
            PublishResponse with result

        Example:
            >>> await publisher.publish_notification(
            ...     channel="notifications#user#123",
            ...     title="Bot Started",
            ...     message="Your bot has started successfully",
            ...     level="success"
            ... )
        """
        event_data = {
            "event_type": "notification",
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now(tz.utc).isoformat(),
        }

        if metadata:
            event_data.update(metadata)
        if extra:
            event_data.update(extra)

        logger.debug(f"Publishing notification: {channel} ({title})")

        # DirectCentrifugoClient doesn't support 'user' parameter
        if isinstance(self._client, DirectCentrifugoClient):
            return await self._client.publish(channel=channel, data=event_data)
        else:
            return await self._client.publish(channel=channel, data=event_data, user=user)

    async def publish_status_change(
        self,
        channel: str,
        old_status: str,
        new_status: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ) -> PublishResponse:
        """
        Publish status change event.

        Args:
            channel: Centrifugo channel
            old_status: Previous status
            new_status: New status
            reason: Reason for status change
            metadata: Additional metadata
            **extra: Additional fields

        Returns:
            PublishResponse with result

        Example:
            >>> await publisher.publish_status_change(
            ...     channel="bot#123#status",
            ...     old_status="STOPPED",
            ...     new_status="RUNNING",
            ...     reason="User requested start"
            ... )
        """
        event_data = {
            "event_type": "status_change",
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now(tz.utc).isoformat(),
        }

        if reason:
            event_data["reason"] = reason
        if metadata:
            event_data.update(metadata)
        if extra:
            event_data.update(extra)

        logger.debug(f"Publishing status change: {channel} ({old_status} → {new_status})")

        return await self._client.publish(channel=channel, data=event_data)

    async def publish_custom(
        self,
        channel: str,
        event_type: str,
        data: Dict[str, Any],
        user: Optional[Any] = None,
    ) -> PublishResponse:
        """
        Publish custom event with arbitrary data.

        Args:
            channel: Centrifugo channel
            event_type: Custom event type
            data: Event data dict
            user: Django User instance

        Returns:
            PublishResponse with result

        Example:
            >>> await publisher.publish_custom(
            ...     channel="custom#events",
            ...     event_type="custom_event",
            ...     data={"foo": "bar", "count": 42}
            ... )
        """
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now(tz.utc).isoformat(),
            **data,
        }

        logger.debug(f"Publishing custom event: {channel} ({event_type})")

        # DirectCentrifugoClient doesn't support 'user' parameter
        if isinstance(self._client, DirectCentrifugoClient):
            return await self._client.publish(channel=channel, data=event_data)
        else:
            return await self._client.publish(channel=channel, data=event_data, user=user)


# Singleton instance
_publisher_instance: Optional[CentrifugoPublisher] = None


def get_centrifugo_publisher(client: Optional[CentrifugoClient] = None) -> CentrifugoPublisher:
    """
    Get singleton CentrifugoPublisher instance.

    Args:
        client: Optional CentrifugoClient (creates new publisher if provided)

    Returns:
        CentrifugoPublisher instance

    Example:
        >>> from django_cfg.apps.integrations.centrifugo.services import get_centrifugo_publisher
        >>> publisher = get_centrifugo_publisher()
        >>> await publisher.publish_demo_event(channel="test", metadata={"foo": "bar"})
    """
    global _publisher_instance

    if client is not None:
        # Create new instance with custom client
        return CentrifugoPublisher(client=client)

    if _publisher_instance is None:
        _publisher_instance = CentrifugoPublisher()

    return _publisher_instance


__all__ = [
    "CentrifugoPublisher",
    "get_centrifugo_publisher",
]
