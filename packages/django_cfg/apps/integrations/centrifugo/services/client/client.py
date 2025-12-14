"""
Django-CFG Centrifugo Client.

Async client enabling Django applications to publish messages
to Centrifugo via Python Wrapper with ACK tracking.

Mirrors DjangoCfgRPCClient interface for easy migration from legacy WebSocket solution.
"""

import asyncio
import json
import time
from typing import Any, Optional, Type, TypeVar
from uuid import uuid4

import httpx
from django_cfg.utils import get_logger
from pydantic import BaseModel

from .exceptions import (
    CentrifugoConfigurationError,
    CentrifugoConnectionError,
    CentrifugoPublishError,
    CentrifugoTimeoutError,
    CentrifugoValidationError,
)

logger = get_logger("centrifugo.client")

TData = TypeVar("TData", bound=BaseModel)


class PublishResponse(BaseModel):
    """Response from publish operation."""

    message_id: str
    published: bool
    delivered: bool = False
    acks_received: int = 0
    timeout: bool = False


class CentrifugoClient:
    """
    Async Centrifugo client for Django to communicate with Centrifugo server.

    Features:
    - Async/await API for Django 5.2+ async views
    - Publishes messages via Python Wrapper HTTP API
    - Supports ACK tracking for delivery confirmation
    - Type-safe API with Pydantic models
    - Connection pooling for performance
    - Automatic logging with CentrifugoLogger
    - Mirrors DjangoCfgRPCClient interface for migration

    Example:
        >>> from django_cfg.apps.integrations.centrifugo import get_centrifugo_client
        >>>
        >>> client = get_centrifugo_client()
        >>>
        >>> # Simple publish (fire-and-forget)
        >>> result = await client.publish(
        ...     channel="broadcast",
        ...     data={"message": "Hello everyone"}
        ... )
        >>>
        >>> # Publish with ACK tracking
        >>> result = await client.publish_with_ack(
        ...     channel="user#123",
        ...     data={"title": "Notification", "message": "Test"},
        ...     ack_timeout=10
        ... )
        >>> if result.delivered:
        ...     print(f"Delivered to {result.acks_received} clients")
    """

    def __init__(
        self,
        wrapper_url: Optional[str] = None,
        wrapper_api_key: Optional[str] = None,
        default_timeout: int = 30,
        ack_timeout: int = 10,
        http_timeout: int = 35,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = False,
    ):
        """
        Initialize Centrifugo client.

        Args:
            wrapper_url: Python Wrapper HTTP API URL
            wrapper_api_key: Optional API key for wrapper authentication
            default_timeout: Default publish timeout (seconds)
            ack_timeout: Default ACK timeout (seconds)
            http_timeout: HTTP request timeout (seconds)
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            verify_ssl: Whether to verify SSL certificates (default: False, allows self-signed certs)
        """
        self.wrapper_url = wrapper_url or self._get_wrapper_url_from_settings()
        self.wrapper_api_key = wrapper_api_key
        self.default_timeout = default_timeout
        self.ack_timeout = ack_timeout
        self.http_timeout = http_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl

        # Create HTTP client with connection pooling
        headers = {"Content-Type": "application/json"}
        if self.wrapper_api_key:
            headers["X-API-Key"] = self.wrapper_api_key

        self._http_client = httpx.AsyncClient(
            base_url=self.wrapper_url,
            headers=headers,
            timeout=httpx.Timeout(self.http_timeout),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
            verify=self.verify_ssl,
        )

        logger.info(f"Centrifugo client initialized: {self.wrapper_url}")

    def _get_wrapper_url_from_settings(self) -> str:
        """
        Get Wrapper URL from django-cfg config.

        Returns:
            Wrapper URL string

        Raises:
            CentrifugoConfigurationError: If settings not configured
        """
        from ..config_helper import get_centrifugo_config

        config = get_centrifugo_config()

        if config and config.wrapper_url:
            return config.wrapper_url

        raise CentrifugoConfigurationError(
            "Centrifugo config not found in django-cfg. "
            "Configure DjangoCfgCentrifugoConfig in DjangoConfig.",
            config_key="centrifugo.wrapper_url",
        )

    async def publish(
        self,
        channel: str,
        data: BaseModel | dict,
        user: Optional[Any] = None,
        caller_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PublishResponse:
        """
        Publish message to Centrifugo channel (fire-and-forget).

        Does not wait for client acknowledgment.

        Args:
            channel: Centrifugo channel (e.g., "user#123", "broadcast")
            data: Pydantic model or dict with message data
            user: Django User instance for logging (optional)
            caller_ip: IP address for logging (optional)
            user_agent: User agent for logging (optional)

        Returns:
            PublishResponse with published=True if sent successfully

        Raises:
            CentrifugoPublishError: If publish fails
            CentrifugoValidationError: If data validation fails

        Example:
            >>> result = await client.publish(
            ...     channel="broadcast",
            ...     data={"message": "Hello everyone"}
            ... )
            >>> print(result.published)  # True
        """
        return await self._publish_internal(
            channel=channel,
            data=data,
            wait_for_ack=False,
            ack_timeout=0,
            user=user,
            caller_ip=caller_ip,
            user_agent=user_agent,
        )

    async def publish_with_ack(
        self,
        channel: str,
        data: BaseModel | dict,
        ack_timeout: Optional[int] = None,
        user: Optional[Any] = None,
        caller_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PublishResponse:
        """
        Publish message with ACK tracking (delivery confirmation).

        Waits for client(s) to acknowledge receipt.

        Args:
            channel: Centrifugo channel (e.g., "user#123")
            data: Pydantic model or dict with message data
            ack_timeout: ACK timeout override (seconds)
            user: Django User instance for logging (optional)
            caller_ip: IP address for logging (optional)
            user_agent: User agent for logging (optional)

        Returns:
            PublishResponse with delivered=True and acks_received count

        Raises:
            CentrifugoTimeoutError: If ACK timeout exceeded
            CentrifugoPublishError: If publish fails
            CentrifugoValidationError: If data validation fails

        Example:
            >>> result = await client.publish_with_ack(
            ...     channel="user#123",
            ...     data={"title": "Alert", "message": "Important"},
            ...     ack_timeout=10
            ... )
            >>> if result.delivered:
            ...     print(f"Delivered to {result.acks_received} clients")
        """
        timeout = ack_timeout or self.ack_timeout

        return await self._publish_internal(
            channel=channel,
            data=data,
            wait_for_ack=True,
            ack_timeout=timeout,
            user=user,
            caller_ip=caller_ip,
            user_agent=user_agent,
        )

    async def _publish_internal(
        self,
        channel: str,
        data: BaseModel | dict,
        wait_for_ack: bool,
        ack_timeout: int,
        user: Optional[Any] = None,
        caller_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PublishResponse:
        """
        Internal publish implementation with retry logic.

        Args:
            channel: Centrifugo channel
            data: Message data
            wait_for_ack: Whether to wait for ACK
            ack_timeout: ACK timeout in seconds
            user: Django User for logging
            caller_ip: Caller IP for logging
            user_agent: User agent for logging

        Returns:
            PublishResponse

        Raises:
            CentrifugoPublishError: If all retries fail
            CentrifugoTimeoutError: If ACK timeout
        """
        message_id = str(uuid4())
        start_time = time.time()

        # Serialize data
        if isinstance(data, BaseModel):
            try:
                data_dict = data.model_dump()
            except Exception as e:
                raise CentrifugoValidationError(
                    f"Failed to serialize Pydantic model: {e}",
                    validation_errors=[str(e)],
                )
        elif isinstance(data, dict):
            data_dict = data
        else:
            raise CentrifugoValidationError(
                f"data must be BaseModel or dict, got {type(data).__name__}"
            )

        # Create log entry (async)
        log_entry = None
        try:
            from ..logging import CentrifugoLogger

            log_entry = await CentrifugoLogger.create_log_async(
                message_id=message_id,
                channel=channel,
                data=data_dict,
                wait_for_ack=wait_for_ack,
                ack_timeout=ack_timeout if wait_for_ack else None,
                user=user,
                caller_ip=caller_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.warning(f"Failed to create log entry: {e}", exc_info=True)

        # Prepare request payload
        payload = {
            "channel": channel,
            "data": data_dict,
            "wait_for_ack": wait_for_ack,
            "ack_timeout": ack_timeout if wait_for_ack else 0,
        }

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self._http_client.post("/api/publish", json=payload)

                if response.status_code == 200:
                    result_data = response.json()
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Update log entry (async)
                    if log_entry:
                        try:
                            from ..logging import CentrifugoLogger

                            if result_data.get("delivered", False):
                                await CentrifugoLogger.mark_success_async(
                                    log_entry,
                                    acks_received=result_data.get("acks_received", 0),
                                    duration_ms=duration_ms,
                                )
                            elif wait_for_ack:
                                await CentrifugoLogger.mark_timeout_async(
                                    log_entry,
                                    acks_received=result_data.get("acks_received", 0),
                                    duration_ms=duration_ms,
                                )
                            else:
                                await CentrifugoLogger.mark_success_async(
                                    log_entry, acks_received=0, duration_ms=duration_ms
                                )
                        except Exception as e:
                            logger.warning(f"Failed to update log entry: {e}", exc_info=True)

                    return PublishResponse(
                        message_id=result_data.get("message_id", message_id),
                        published=result_data.get("published", True),
                        delivered=result_data.get("delivered", False),
                        acks_received=result_data.get("acks_received", 0),
                        timeout=not result_data.get("delivered", False) and wait_for_ack,
                    )

                else:
                    last_error = CentrifugoPublishError(
                        f"Wrapper returned HTTP {response.status_code}",
                        channel=channel,
                        status_code=response.status_code,
                        response_data=response.json() if response.text else None,
                    )

            except httpx.TimeoutException as e:
                last_error = CentrifugoTimeoutError(
                    f"HTTP timeout to wrapper: {e}",
                    channel=channel,
                    timeout_seconds=self.http_timeout,
                )

            except httpx.ConnectError as e:
                last_error = CentrifugoConnectionError(
                    f"Failed to connect to wrapper: {e}",
                    wrapper_url=self.wrapper_url,
                )

            except Exception as e:
                last_error = CentrifugoPublishError(
                    f"Unexpected error: {e}",
                    channel=channel,
                )

            # Retry delay
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay)

        # All retries failed
        duration_ms = int((time.time() - start_time) * 1000)

        if log_entry:
            try:
                from ..logging import CentrifugoLogger

                error_code = type(last_error).__name__ if last_error else "unknown"
                error_message = str(last_error) if last_error else "Unknown error"
                await CentrifugoLogger.mark_failed_async(
                    log_entry,
                    error_code=error_code,
                    error_message=error_message,
                    duration_ms=duration_ms,
                )
            except Exception as e:
                logger.warning(f"Failed to update log entry: {e}")

        raise last_error if last_error else CentrifugoPublishError(
            "All retries failed", channel=channel
        )

    async def fire_and_forget(
        self,
        channel: str,
        data: BaseModel | dict,
    ) -> str:
        """
        Send message without waiting for response (alias for publish).

        Args:
            channel: Centrifugo channel
            data: Message data

        Returns:
            Message ID

        Example:
            >>> message_id = await client.fire_and_forget(
            ...     channel="logs",
            ...     data={"event": "user_login", "user_id": "123"}
            ... )
        """
        result = await self.publish(channel=channel, data=data)
        return result.message_id

    async def health_check(self, timeout: int = 5) -> bool:
        """
        Check if wrapper is healthy.

        Args:
            timeout: Health check timeout (seconds)

        Returns:
            True if healthy, False otherwise

        Example:
            >>> if await client.health_check():
            ...     print("Wrapper healthy")
        """
        try:
            response = await self._http_client.get(
                "/health",
                timeout=httpx.Timeout(timeout),
            )

            if response.status_code == 200:
                health_data = response.json()
                return health_data.get("status") == "healthy"

            return False

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_connection_info(self) -> dict:
        """
        Get connection information.

        Returns:
            Dictionary with connection details

        Example:
            >>> info = client.get_connection_info()
            >>> print(info["wrapper_url"])
        """
        return {
            "wrapper_url": self.wrapper_url,
            "has_api_key": self.wrapper_api_key is not None,
            "default_timeout": self.default_timeout,
            "ack_timeout": self.ack_timeout,
            "http_timeout": self.http_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
        }

    async def close(self):
        """
        Close HTTP client connections.

        Call this when shutting down application to clean up resources.

        Example:
            >>> await client.close()
        """
        await self._http_client.aclose()
        logger.info("Centrifugo client closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# ==================== Singleton Pattern ====================

_centrifugo_client: Optional[CentrifugoClient] = None
_centrifugo_client_lock = None


def get_centrifugo_client(force_new: bool = False) -> CentrifugoClient:
    """
    Get global Centrifugo client instance (singleton).

    Creates client from Django settings on first call.
    Subsequent calls return the same instance (thread-safe).

    Args:
        force_new: Force create new instance (for testing)

    Returns:
        CentrifugoClient instance

    Example:
        >>> from django_cfg.apps.integrations.centrifugo import get_centrifugo_client
        >>> client = get_centrifugo_client()
        >>> result = await client.publish_with_ack(...)
    """
    global _centrifugo_client, _centrifugo_client_lock

    if force_new:
        return _create_client_from_settings()

    if _centrifugo_client is None:
        # Thread-safe singleton creation
        import threading

        if _centrifugo_client_lock is None:
            _centrifugo_client_lock = threading.Lock()

        with _centrifugo_client_lock:
            if _centrifugo_client is None:
                _centrifugo_client = _create_client_from_settings()

    return _centrifugo_client


def _create_client_from_settings() -> CentrifugoClient:
    """
    Create Centrifugo client from django-cfg config.

    Returns:
        CentrifugoClient instance

    Raises:
        CentrifugoConfigurationError: If settings not configured
    """
    from ..config_helper import get_centrifugo_config_or_default

    cfg = get_centrifugo_config_or_default()
    logger.debug(f"Creating Centrifugo client from config: {cfg.wrapper_url}")

    return CentrifugoClient(
        wrapper_url=cfg.wrapper_url,
        wrapper_api_key=cfg.wrapper_api_key,
        default_timeout=cfg.default_timeout,
        ack_timeout=cfg.ack_timeout,
        http_timeout=cfg.http_timeout,
        max_retries=cfg.max_retries,
        retry_delay=cfg.retry_delay,
        verify_ssl=cfg.verify_ssl,
    )


__all__ = [
    "CentrifugoClient",
    "get_centrifugo_client",
    "PublishResponse",
]
