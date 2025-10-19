"""
Django-CFG RPC Client.

Synchronous RPC client enabling Django applications to communicate
with django-cfg-rpc WebSocket servers via Redis.

Works with or without django-cfg-rpc installed:
- With django-cfg-rpc: Full type safety with Pydantic models
- Without django-cfg-rpc: Basic dict-based communication
"""

import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from uuid import uuid4

import redis

from .exceptions import (
    HAS_DJANGO_CFG_RPC,
    RPCConfigurationError,
    RPCConnectionError,
    RPCRemoteError,
    RPCTimeoutError,
)

logger = logging.getLogger(__name__)

# Try to import Pydantic from django-cfg-rpc
if HAS_DJANGO_CFG_RPC:
    try:
        from pydantic import BaseModel
        TParams = TypeVar("TParams", bound=BaseModel)
        TResult = TypeVar("TResult", bound=BaseModel)
    except ImportError:
        # Fallback if pydantic not available
        BaseModel = dict  # type: ignore
        TParams = TypeVar("TParams")
        TResult = TypeVar("TResult")
else:
    BaseModel = dict  # type: ignore
    TParams = TypeVar("TParams")
    TResult = TypeVar("TResult")


class DjangoCfgRPCClient:
    """
    Synchronous RPC client for Django to communicate with django-cfg-rpc servers.

    Features:
    - Uses Redis Streams for reliable request delivery
    - Uses Redis Lists for fast response retrieval
    - Blocks synchronously using BLPOP (no async/await)
    - Handles correlation IDs automatically
    - Type-safe API with Pydantic models (if django-cfg-rpc installed)
    - Connection pooling for performance
    - Automatic cleanup of ephemeral keys

    Example:
        >>> from django_cfg.modules.django_ipc_client import get_rpc_client
        >>>
        >>> # With django-cfg-rpc models
        >>> from django_ipc.models import NotificationRequest, NotificationResponse
        >>> rpc = get_rpc_client()
        >>> result: NotificationResponse = rpc.call(
        ...     method="send_notification",
        ...     params=NotificationRequest(user_id="123", type="info",
        ...                                 title="Hello", message="World"),
        ...     result_model=NotificationResponse
        ... )
        >>>
        >>> # Without django-cfg-rpc (dict-based)
        >>> result = rpc.call_dict(
        ...     method="send_notification",
        ...     params={"user_id": "123", "type": "info",
        ...             "title": "Hello", "message": "World"}
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

            logger.info(f"Django-CFG RPC Client initialized: {self.redis_url}")

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

            if not hasattr(settings, "DJANGO_CFG_RPC"):
                raise RPCConfigurationError(
                    "DJANGO_CFG_RPC not found in Django settings. "
                    "Configure DjangoCfgRPCConfig in django-cfg.",
                    config_key="DJANGO_CFG_RPC",
                )

            redis_url = settings.DJANGO_CFG_RPC.get("REDIS_URL")
            if not redis_url:
                raise RPCConfigurationError(
                    "REDIS_URL not found in DJANGO_CFG_RPC settings",
                    config_key="DJANGO_CFG_RPC.REDIS_URL",
                )

            return redis_url

        except ImportError:
            raise RPCConfigurationError(
                "Django not installed. Provide redis_url explicitly or configure Django."
            )

    def call(
        self,
        method: str,
        params: Any,
        result_model: Optional[Type[TResult]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """
        Make synchronous RPC call to django-cfg-rpc server.

        Args:
            method: RPC method name
            params: Pydantic model or dict with parameters
            result_model: Expected result model class (optional)
            timeout: Optional timeout override (seconds)

        Returns:
            Pydantic result model instance (if result_model provided) or dict

        Raises:
            RPCTimeoutError: If timeout exceeded
            RPCRemoteError: If remote execution failed
            ValidationError: If response doesn't match result_model

        Example:
            >>> from django_ipc.models import NotificationRequest, NotificationResponse
            >>> result = rpc.call(
            ...     method="send_notification",
            ...     params=NotificationRequest(user_id="123", type="info",
            ...                                 title="Hello", message="World"),
            ...     result_model=NotificationResponse,
            ...     timeout=10
            ... )
            >>> print(result.delivered)  # True/False
        """
        timeout = timeout or self.default_timeout

        # Generate correlation ID
        cid = str(uuid4())
        reply_key = f"{self.response_key_prefix}{cid}"

        # Serialize params
        if HAS_DJANGO_CFG_RPC and hasattr(params, "model_dump_json"):
            params_json = params.model_dump_json()
        elif HAS_DJANGO_CFG_RPC and hasattr(params, "model_dump"):
            params_json = json.dumps(params.model_dump())
        elif isinstance(params, dict):
            params_json = json.dumps(params)
        else:
            params_json = json.dumps({"data": params})

        # Build RPC request payload
        request_payload = {
            "type": "rpc",
            "method": method,
            "params": json.loads(params_json),  # Embedded as dict
            "correlation_id": cid,
            "reply_to": reply_key,  # Redis List key for response
            "timeout": timeout,
        }

        if self.log_calls:
            logger.debug(f"RPC call: {method} (cid={cid})")

        try:
            # Send request to Redis Stream
            message_id = self._redis.xadd(
                self.request_stream,
                {"payload": json.dumps(request_payload)},
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

            if self.log_calls:
                logger.debug(f"RPC response received: {method}")

            # Check response type
            if response_dict.get("type") == "error":
                # Error response
                error_data = response_dict.get("error", {})
                raise RPCRemoteError(error_data)

            # Extract result
            result_data = response_dict.get("result")

            if result_data is None:
                raise RPCRemoteError({
                    "code": "internal_error",
                    "message": "Response has no result field",
                })

            # Deserialize result if model provided
            if result_model and HAS_DJANGO_CFG_RPC:
                try:
                    return result_model(**result_data)
                except Exception as e:
                    logger.error(f"Failed to deserialize result: {e}")
                    # Return raw dict as fallback
                    return result_data
            else:
                return result_data

        finally:
            # Always cleanup response key
            try:
                self._redis.delete(reply_key)
            except Exception as e:
                logger.error(f"Failed to cleanup response key {reply_key}: {e}")

    def call_dict(
        self,
        method: str,
        params: Dict[str, Any],
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make RPC call with dict params (no Pydantic).

        Args:
            method: RPC method name
            params: Dictionary with parameters
            timeout: Optional timeout override (seconds)

        Returns:
            Dictionary with result

        Example:
            >>> result = rpc.call_dict(
            ...     method="send_notification",
            ...     params={"user_id": "123", "type": "info",
            ...             "title": "Hello", "message": "World"}
            ... )
            >>> print(result["delivered"])
        """
        return self.call(method=method, params=params, result_model=None, timeout=timeout)

    def fire_and_forget(self, method: str, params: Any) -> str:
        """
        Send RPC request without waiting for response.

        Useful for notifications where result doesn't matter.
        Returns immediately after sending to Redis Stream.

        Args:
            method: RPC method name
            params: Pydantic model or dict with parameters

        Returns:
            Message ID from Redis Stream

        Example:
            >>> rpc.fire_and_forget(
            ...     method="log_event",
            ...     params={"event": "user_login", "user_id": "123"}
            ... )
        """
        cid = str(uuid4())

        # Serialize params
        if HAS_DJANGO_CFG_RPC and hasattr(params, "model_dump_json"):
            params_json = params.model_dump_json()
        elif HAS_DJANGO_CFG_RPC and hasattr(params, "model_dump"):
            params_json = json.dumps(params.model_dump())
        elif isinstance(params, dict):
            params_json = json.dumps(params)
        else:
            params_json = json.dumps({"data": params})

        request_payload = {
            "type": "rpc",
            "method": method,
            "params": json.loads(params_json),
            "correlation_id": cid,
            "timeout": 0,  # Indicates fire-and-forget
        }

        message_id = self._redis.xadd(
            self.request_stream,
            {"payload": json.dumps(request_payload)},
            maxlen=self.stream_maxlen,
            approximate=True,
        )

        if self.log_calls:
            logger.debug(f"Fire-and-forget: {method} (mid={message_id})")

        return message_id.decode() if isinstance(message_id, bytes) else str(message_id)

    def health_check(self, timeout: int = 5) -> bool:
        """
        Check if RPC system is healthy.

        Attempts to ping Redis.

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
            >>> print(info["request_stream"])
        """
        return {
            "redis_url": self.redis_url,
            "pool_size": self._pool.max_connections if self._pool else 0,
            "request_stream": self.request_stream,
            "consumer_group": self.consumer_group,
            "default_timeout": self.default_timeout,
            "has_django_ipc": HAS_DJANGO_CFG_RPC,
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

_rpc_client: Optional[DjangoCfgRPCClient] = None
_rpc_client_lock = None


def get_rpc_client(force_new: bool = False) -> DjangoCfgRPCClient:
    """
    Get global RPC client instance (singleton).

    Creates client from Django settings on first call.
    Subsequent calls return the same instance (thread-safe).

    Args:
        force_new: Force create new instance (for testing)

    Returns:
        DjangoCfgRPCClient instance

    Example:
        >>> from django_cfg.modules.django_ipc_client import get_rpc_client
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


def _create_client_from_settings() -> DjangoCfgRPCClient:
    """
    Create RPC client from Django settings.

    Returns:
        DjangoCfgRPCClient instance

    Raises:
        RPCConfigurationError: If settings not configured
    """
    try:
        from django.conf import settings

        if not hasattr(settings, "DJANGO_CFG_RPC"):
            raise RPCConfigurationError(
                "DJANGO_CFG_RPC not found in Django settings"
            )

        rpc_settings = settings.DJANGO_CFG_RPC

        return DjangoCfgRPCClient(
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
    "DjangoCfgRPCClient",
    "get_rpc_client",
]
