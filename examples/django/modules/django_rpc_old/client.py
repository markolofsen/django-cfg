"""
WebSocket RPC Client for Django.

Synchronous RPC client enabling Django applications to communicate
with external WebSocket servers via Redis.

File size: ~650 lines
"""

import redis
import json
import logging
from uuid import uuid4
from typing import Optional, TypeVar, Type
from pydantic import BaseModel

from django_cfg.models.websocket import (
    RPCRequest,
    RPCResponse,
    RPCError,
    RPCErrorCode,
)
from .exceptions import (
    RPCTimeoutError,
    RPCRemoteError,
    RPCConnectionError,
    RPCConfigurationError,
)

logger = logging.getLogger(__name__)

TParams = TypeVar("TParams", bound=BaseModel)
TResult = TypeVar("TResult", bound=BaseModel)


class WebSocketRPCClient:
    """
    Synchronous RPC client for Django to communicate with WebSocket servers.

    Features:
    - Uses Redis Streams for reliable request delivery
    - Uses Redis Lists for fast response retrieval
    - Blocks synchronously using BLPOP (no async/await)
    - Handles correlation IDs automatically
    - Type-safe API with Pydantic models
    - Connection pooling for performance
    - Automatic cleanup of ephemeral keys

    Example:
        >>> from django_cfg.modules.django_rpc import get_rpc_client
        >>> from django_cfg.models.websocket import NotificationRequest, NotificationResponse
        >>>
        >>> rpc = get_rpc_client()
        >>> result: NotificationResponse = rpc.call(
        ...     method="send_notification",
        ...     params=NotificationRequest(user_id="123", message="Hello"),
        ...     result_model=NotificationResponse
        ... )
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        timeout: int = 30,
        request_stream: str = "stream:requests",
        consumer_group: str = "rpc_group",
        stream_maxlen: int = 10000,
        response_key_prefix: str = "list:response:",
        response_key_ttl: int = 60,
        max_connections: int = 50,
        log_calls: bool = False,
    ):
        """
        Initialize RPC client.

        Args:
            redis_url: Redis connection URL
            timeout: Default timeout for RPC calls (seconds)
            request_stream: Redis Stream name for requests
            consumer_group: Consumer group name
            stream_maxlen: Maximum stream length
            response_key_prefix: Prefix for response list keys
            response_key_ttl: Response key TTL (seconds)
            max_connections: Maximum Redis connections in pool
            log_calls: Log all RPC calls (verbose)
        """
        self.redis_url = redis_url or self._get_redis_url_from_settings()
        self.default_timeout = timeout
        self.request_stream = request_stream
        self.consumer_group = consumer_group
        self.stream_maxlen = stream_maxlen
        self.response_key_prefix = response_key_prefix
        self.response_key_ttl = response_key_ttl
        self.log_calls = log_calls

        # Create Redis connection pool
        try:
            self._pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=max_connections,
                decode_responses=False,  # We handle JSON ourselves
                socket_keepalive=True,
            )
            self._redis = redis.Redis(connection_pool=self._pool)

            # Test connection
            self._redis.ping()

            logger.info(f"WebSocket RPC Client initialized: {self.redis_url}")

        except redis.ConnectionError as e:
            raise RPCConnectionError(
                f"Failed to connect to Redis: {e}",
                redis_url=self.redis_url,
            )
        except Exception as e:
            raise RPCConnectionError(
                f"Failed to initialize RPC client: {e}",
                redis_url=self.redis_url,
            )

    def _get_redis_url_from_settings(self) -> str:
        """
        Get Redis URL from Django settings.

        Returns:
            Redis URL string

        Raises:
            RPCConfigurationError: If settings not configured
        """
        try:
            from django.conf import settings

            if not hasattr(settings, "WEBSOCKET_RPC"):
                raise RPCConfigurationError(
                    "WEBSOCKET_RPC not found in Django settings. "
                    "Configure WebSocketRPCConfig in django-cfg.",
                    config_key="WEBSOCKET_RPC",
                )

            redis_url = settings.WEBSOCKET_RPC.get("REDIS_URL")
            if not redis_url:
                raise RPCConfigurationError(
                    "REDIS_URL not found in WEBSOCKET_RPC settings",
                    config_key="WEBSOCKET_RPC.REDIS_URL",
                )

            return redis_url

        except ImportError:
            raise RPCConfigurationError(
                "Django not installed. Provide redis_url explicitly or configure Django."
            )

    def call(
        self,
        method: str,
        params: TParams,
        result_model: Type[TResult],
        timeout: Optional[int] = None,
    ) -> TResult:
        """
        Make synchronous RPC call to WebSocket server.

        Args:
            method: RPC method name
            params: Pydantic model with parameters
            result_model: Expected result model class
            timeout: Optional timeout override (seconds)

        Returns:
            Pydantic result model instance

        Raises:
            RPCTimeoutError: If timeout exceeded
            RPCRemoteError: If remote execution failed
            ValidationError: If response doesn't match result_model

        Example:
            >>> from django_cfg.models.websocket import EchoParams, EchoResult
            >>> result = rpc.call(
            ...     method="echo",
            ...     params=EchoParams(message="Hello"),
            ...     result_model=EchoResult,
            ...     timeout=10
            ... )
            >>> print(result.echoed)  # "Hello"
        """
        timeout = timeout or self.default_timeout

        # Generate correlation ID
        cid = uuid4()
        reply_key = f"{self.response_key_prefix}{cid}"

        # Build RPC request
        request = RPCRequest[type(params)](
            correlation_id=cid,
            method=method,
            params=params,
            reply_to=reply_key,
            timeout=timeout,
        )

        if self.log_calls:
            logger.debug(f"RPC call: {method} (cid={cid})")

        try:
            # Send request to Redis Stream
            message_id = self._redis.xadd(
                self.request_stream,
                {"payload": request.model_dump_json()},
                maxlen=self.stream_maxlen,
                approximate=True,
            )

            if self.log_calls:
                logger.debug(f"Request sent to stream: {message_id}")

            # Block waiting for response (BLPOP)
            response_data = self._redis.blpop(reply_key, timeout)

            if response_data is None:
                # Timeout occurred
                logger.warning(f"RPC timeout: {method} (cid={cid}, timeout={timeout}s)")
                raise RPCTimeoutError(
                    f"RPC call '{method}' timed out after {timeout}s",
                    method=method,
                    timeout_seconds=timeout,
                )

            # Unpack BLPOP result: (key, value)
            _, response_json = response_data

            # Parse response
            response_dict = json.loads(response_json)
            response = RPCResponse[result_model](**response_dict)

            if self.log_calls:
                logger.debug(f"RPC response: {method} (success={response.success})")

            # Check for errors
            if not response.success:
                error = RPCError(
                    code=response.error_code or RPCErrorCode.INTERNAL_ERROR,
                    message=response.error or "Unknown error",
                    retryable=response.error_code in {
                        RPCErrorCode.TIMEOUT,
                        RPCErrorCode.SERVICE_UNAVAILABLE,
                        RPCErrorCode.RATE_LIMIT_EXCEEDED,
                    },
                )
                raise RPCRemoteError(error)

            if response.result is None:
                raise RPCRemoteError(
                    RPCError(
                        code=RPCErrorCode.INTERNAL_ERROR,
                        message="Response success=True but result is None",
                    )
                )

            return response.result

        finally:
            # Always cleanup response key
            try:
                self._redis.delete(reply_key)
            except Exception as e:
                logger.error(f"Failed to cleanup response key {reply_key}: {e}")

    def fire_and_forget(self, method: str, params: TParams) -> str:
        """
        Send RPC request without waiting for response.

        Useful for notifications where result doesn't matter.
        Returns immediately after sending to Redis Stream.

        Args:
            method: RPC method name
            params: Pydantic model with parameters

        Returns:
            Message ID from Redis Stream

        Example:
            >>> from pydantic import BaseModel
            >>> class EventLog(BaseModel):
            ...     event: str
            ...     user_id: str
            >>> rpc.fire_and_forget(
            ...     method="log_event",
            ...     params=EventLog(event="user_login", user_id="123")
            ... )
        """
        cid = uuid4()

        request = RPCRequest[type(params)](
            correlation_id=cid,
            method=method,
            params=params,
            reply_to=f"{self.response_key_prefix}{cid}",  # Won't be used
            timeout=0,  # Indicates fire-and-forget
        )

        message_id = self._redis.xadd(
            self.request_stream,
            {"payload": request.model_dump_json()},
            maxlen=self.stream_maxlen,
            approximate=True,
        )

        if self.log_calls:
            logger.debug(f"Fire-and-forget: {method} (mid={message_id})")

        return message_id.decode()

    def broadcast(self, channel: str, message: BaseModel) -> int:
        """
        Broadcast message via Redis Pub/Sub.

        Sends message to all WebSocket servers subscribed to channel.

        Args:
            channel: Redis channel name
            message: Pydantic model to broadcast

        Returns:
            Number of subscribers that received message

        Example:
            >>> from django_cfg.models.websocket import BroadcastRequest
            >>> rpc.broadcast(
            ...     channel="notifications:broadcast",
            ...     message=BroadcastRequest(
            ...         target="all",
            ...         event_type="system_update",
            ...         payload={"version": "2.0"}
            ...     )
            ... )
        """
        subscribers = self._redis.publish(channel, message.model_dump_json())

        if self.log_calls:
            logger.info(f"Broadcast to {channel}: {subscribers} subscribers")

        return subscribers

    def health_check(self, timeout: int = 5) -> bool:
        """
        Check if RPC system is healthy.

        Attempts to:
        1. Ping Redis
        2. Send echo RPC call (if echo method exists)

        Args:
            timeout: Health check timeout (seconds)

        Returns:
            True if healthy, False otherwise

        Example:
            >>> if rpc.health_check():
            ...     print("RPC system healthy")
            ... else:
            ...     print("RPC system unhealthy")
        """
        try:
            # Try to ping Redis
            ping_result = self._redis.ping()
            if not ping_result:
                logger.error("Health check failed: Redis ping returned False")
                return False

            # Try simple echo RPC (optional, depends on server implementation)
            try:
                from django_cfg.models.websocket import EchoParams, EchoResult

                result = self.call(
                    method="echo",
                    params=EchoParams(message="health_check"),
                    result_model=EchoResult,
                    timeout=timeout,
                )

                if result.echoed != "health_check":
                    logger.error(
                        f"Health check failed: Echo mismatch "
                        f"(expected 'health_check', got '{result.echoed}')"
                    )
                    return False

            except (ImportError, RPCTimeoutError, RPCRemoteError):
                # Echo method may not be implemented, that's okay
                # Redis ping success is minimum health check
                pass

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_connection_info(self) -> dict:
        """
        Get connection information.

        Returns:
            Dictionary with connection details

        Example:
            >>> info = rpc.get_connection_info()
            >>> print(info["redis_url"])
            >>> print(info["pool_size"])
        """
        return {
            "redis_url": self.redis_url,
            "pool_size": self._pool.max_connections if self._pool else 0,
            "request_stream": self.request_stream,
            "consumer_group": self.consumer_group,
            "default_timeout": self.default_timeout,
        }

    def close(self):
        """
        Close Redis connection pool.

        Call this when shutting down application to clean up resources.

        Example:
            >>> rpc.close()
        """
        if self._pool:
            self._pool.disconnect()
            logger.info("RPC client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ==================== Singleton Pattern ====================

_rpc_client: Optional[WebSocketRPCClient] = None
_rpc_client_lock = None


def get_rpc_client(force_new: bool = False) -> WebSocketRPCClient:
    """
    Get global RPC client instance (singleton).

    Creates client from Django settings on first call.
    Subsequent calls return the same instance (thread-safe).

    Args:
        force_new: Force create new instance (for testing)

    Returns:
        WebSocketRPCClient instance

    Example:
        >>> from django_cfg.modules.django_rpc import get_rpc_client
        >>> rpc = get_rpc_client()
        >>> result = rpc.call(...)
    """
    global _rpc_client, _rpc_client_lock

    if force_new:
        return _create_client_from_settings()

    if _rpc_client is None:
        # Thread-safe singleton creation
        import threading

        if _rpc_client_lock is None:
            _rpc_client_lock = threading.Lock()

        with _rpc_client_lock:
            if _rpc_client is None:
                _rpc_client = _create_client_from_settings()

    return _rpc_client


def _create_client_from_settings() -> WebSocketRPCClient:
    """
    Create RPC client from Django settings.

    Returns:
        WebSocketRPCClient instance

    Raises:
        RPCConfigurationError: If settings not configured
    """
    try:
        from django.conf import settings

        if not hasattr(settings, "WEBSOCKET_RPC"):
            raise RPCConfigurationError(
                "WEBSOCKET_RPC not found in Django settings"
            )

        rpc_settings = settings.WEBSOCKET_RPC

        return WebSocketRPCClient(
            redis_url=rpc_settings.get("REDIS_URL"),
            timeout=rpc_settings.get("RPC_TIMEOUT", 30),
            request_stream=rpc_settings.get("REQUEST_STREAM", "stream:requests"),
            consumer_group=rpc_settings.get("CONSUMER_GROUP", "rpc_group"),
            stream_maxlen=rpc_settings.get("STREAM_MAXLEN", 10000),
            response_key_prefix=rpc_settings.get("RESPONSE_KEY_PREFIX", "list:response:"),
            response_key_ttl=rpc_settings.get("RESPONSE_KEY_TTL", 60),
            max_connections=rpc_settings.get("REDIS_MAX_CONNECTIONS", 50),
            log_calls=rpc_settings.get("LOG_RPC_CALLS", False),
        )

    except ImportError:
        raise RPCConfigurationError(
            "Django not installed. Cannot create client from settings."
        )


__all__ = [
    "WebSocketRPCClient",
    "get_rpc_client",
]
