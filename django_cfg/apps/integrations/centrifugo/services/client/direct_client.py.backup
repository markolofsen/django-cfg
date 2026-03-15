"""
Direct Centrifugo Client.

Lightweight client for internal Django-to-Centrifugo communication.
Bypasses wrapper and connects directly to Centrifugo HTTP API.

Use this for:
- Internal gRPC events
- Demo/test events
- Background tasks
- Any server-side publishing

Use CentrifugoClient (with wrapper) for:
- External API calls (from Next.js frontend)
- When you need Django authorization
- When you need wrapper-level logging
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional
from uuid import uuid4

import httpx
from django_cfg.modules.django_logging import get_logger

from .exceptions import (
    CentrifugoConfigurationError,
    CentrifugoConnectionError,
    CentrifugoPublishError,
)

logger = get_logger("centrifugo.direct_client")


class PublishResponse:
    """Response from direct publish operation."""

    def __init__(self, message_id: str, published: bool):
        self.message_id = message_id
        self.published = published
        self.delivered = published  # For compatibility


class DirectCentrifugoClient:
    """
    Direct Centrifugo HTTP API client.

    Connects directly to Centrifugo without going through Django wrapper.
    Uses Centrifugo JSON-RPC format: POST /api with {method, params}.

    Features:
    - No database logging (lightweight)
    - No wrapper overhead
    - Direct API key authentication
    - Minimal latency for internal calls

    Example:
        >>> from django_cfg.apps.integrations.centrifugo.services.client import DirectCentrifugoClient
        >>>
        >>> client = DirectCentrifugoClient(
        ...     api_url="http://localhost:7120/api",
        ...     api_key="your-api-key"
        ... )
        >>>
        >>> result = await client.publish(
        ...     channel="grpc#bot#123",
        ...     data={"status": "running"}
        ... )
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        http_timeout: int = 10,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        verify_ssl: bool = False,
    ):
        """
        Initialize direct Centrifugo client.

        Args:
            api_url: Centrifugo HTTP API URL (e.g., "http://localhost:8000/api")
            api_key: Centrifugo API key for authentication
            http_timeout: HTTP request timeout (seconds)
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_url = api_url or self._get_api_url_from_settings()
        self.api_key = api_key or self._get_api_key_from_settings()
        self.http_timeout = http_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl

        # Create HTTP client
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"apikey {self.api_key}"

        self._http_client = httpx.AsyncClient(
            base_url=self.api_url.rstrip("/api"),  # Remove /api from base
            headers=headers,
            timeout=httpx.Timeout(self.http_timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            verify=self.verify_ssl,
        )

        logger.info(f"DirectCentrifugoClient initialized: {self.api_url}")

    def _get_api_url_from_settings(self) -> str:
        """Get Centrifugo API URL from django-cfg config."""
        from ..config_helper import get_centrifugo_config

        config = get_centrifugo_config()

        if config and config.centrifugo_api_url:
            return config.centrifugo_api_url

        raise CentrifugoConfigurationError(
            "Centrifugo API URL not configured",
            config_key="centrifugo.centrifugo_api_url",
        )

    def _get_api_key_from_settings(self) -> str:
        """Get Centrifugo API key from django-cfg config."""
        from ..config_helper import get_centrifugo_config

        config = get_centrifugo_config()

        if config and config.centrifugo_api_key:
            return config.centrifugo_api_key

        raise CentrifugoConfigurationError(
            "Centrifugo API key not configured",
            config_key="centrifugo.centrifugo_api_key",
        )

    async def publish(
        self,
        channel: str,
        data: Dict[str, Any],
    ) -> PublishResponse:
        """
        Publish message to Centrifugo channel.

        Args:
            channel: Centrifugo channel name
            data: Message data dict

        Returns:
            PublishResponse with result

        Raises:
            CentrifugoPublishError: If publish fails
            CentrifugoConnectionError: If connection fails

        Example:
            >>> result = await client.publish(
            ...     channel="grpc#bot#123#status",
            ...     data={"status": "running", "timestamp": "2025-11-05T09:00:00Z"}
            ... )
        """
        # Validate channel name and log warnings (development only)
        from ..channel_validator import log_channel_warnings
        log_channel_warnings(channel)

        message_id = str(uuid4())
        start_time = time.time()

        # Centrifugo JSON-RPC format
        payload = {
            "method": "publish",
            "params": {
                "channel": channel,
                "data": data,
            },
        }

        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = await self._http_client.post("/api", json=payload)

                if response.status_code == 200:
                    result = response.json()

                    # Check for Centrifugo error
                    if "error" in result and result["error"]:
                        error_msg = result["error"].get("message", "Unknown error")
                        raise CentrifugoPublishError(
                            f"Centrifugo API error: {error_msg}",
                            channel=channel,
                        )

                    duration_ms = int((time.time() - start_time) * 1000)
                    logger.debug(
                        f"Published to {channel} (message_id={message_id}, {duration_ms}ms)"
                    )

                    return PublishResponse(message_id=message_id, published=True)

                else:
                    raise CentrifugoPublishError(
                        f"HTTP {response.status_code}: {response.text}",
                        channel=channel,
                    )

            except httpx.ConnectError as e:
                last_error = CentrifugoConnectionError(
                    f"Failed to connect to Centrifugo: {e}",
                    wrapper_url=self.api_url,
                )
                logger.warning(
                    f"Connection attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )

            except Exception as e:
                last_error = CentrifugoPublishError(
                    f"Publish failed: {e}",
                    channel=channel,
                )
                logger.error(f"Publish attempt {attempt + 1}/{self.max_retries} failed: {e}")

            # Retry delay
            if attempt < self.max_retries - 1:
                import asyncio
                await asyncio.sleep(self.retry_delay)

        # All retries failed
        if last_error:
            raise last_error
        else:
            raise CentrifugoPublishError(
                f"Failed to publish after {self.max_retries} attempts",
                channel=channel,
            )

    async def close(self):
        """Close HTTP client connection."""
        await self._http_client.aclose()
        logger.debug("DirectCentrifugoClient closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Singleton instance
_direct_client_instance: Optional[DirectCentrifugoClient] = None


def get_direct_centrifugo_client() -> DirectCentrifugoClient:
    """
    Get singleton DirectCentrifugoClient instance.

    Returns:
        DirectCentrifugoClient instance

    Example:
        >>> from django_cfg.apps.integrations.centrifugo.services.client import get_direct_centrifugo_client
        >>> client = get_direct_centrifugo_client()
        >>> await client.publish(channel="test", data={"foo": "bar"})
    """
    global _direct_client_instance

    if _direct_client_instance is None:
        _direct_client_instance = DirectCentrifugoClient()

    return _direct_client_instance


__all__ = [
    "DirectCentrifugoClient",
    "get_direct_centrifugo_client",
    "PublishResponse",
]
