"""
RPC Bridge for WebSocket Servers.

Handles RPC requests from Django via Redis Streams and sends responses back.

File size: ~500 lines
"""

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Optional, Type, TypeVar
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel, ValidationError

from django_ipc.models import (
    RPCError,
    RPCErrorCode,
    RPCRequest,
    RPCResponse,
)

logger = logging.getLogger(__name__)

TParams = TypeVar("TParams", bound=BaseModel)
TResult = TypeVar("TResult", bound=BaseModel)
RPCHandler = Callable[[TParams], Awaitable[TResult]]


class RPCBridge:
    """
    RPC Bridge for WebSocket servers to handle Django RPC calls.

    Features:
    - Listens to Redis Streams for incoming RPC requests
    - Executes registered async handler functions
    - Sends responses back via Redis Lists
    - Type-safe with Pydantic models
    - Automatic error handling

    Example:
        >>> bridge = RPCBridge(redis_url="redis://localhost:6379/2")
        >>>
        >>> @bridge.rpc_method("send_notification")
        >>> async def send_notification(params: NotificationRequest) -> NotificationResponse:
        ...     # Your WebSocket logic
        ...     return NotificationResponse(delivered=True, user_connected=True)
        >>>
        >>> await bridge.start()
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/2",
        request_stream: str = "stream:requests",
        consumer_group: str = "rpc_group",
        consumer_name: Optional[str] = None,
        response_key_prefix: str = "list:response:",
        response_key_ttl: int = 60,
        max_connections: int = 50,
        log_calls: bool = False,
    ):
        """
        Initialize RPC Bridge.

        Args:
            redis_url: Redis connection URL
            request_stream: Redis Stream name for incoming requests
            consumer_group: Consumer group name
            consumer_name: Consumer name (unique per server instance)
            response_key_prefix: Prefix for response list keys
            response_key_ttl: TTL for response keys (seconds)
            max_connections: Maximum Redis connections
            log_calls: Log all RPC calls (verbose)
        """
        self.redis_url = redis_url
        self.request_stream = request_stream
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name or f"ws_server_{uuid4().hex[:8]}"
        self.response_key_prefix = response_key_prefix
        self.response_key_ttl = response_key_ttl
        self.log_calls = log_calls

        # Redis client (will be initialized in start())
        self._redis: Optional[redis.Redis] = None

        # RPC method registry
        self._handlers: Dict[str, RPCHandler] = {}

        # Running state
        self._running = False
        self._tasks: list[asyncio.Task] = []

        logger.info(
            f"RPC Bridge initialized: consumer={self.consumer_name}, "
            f"stream={self.request_stream}"
        )

    async def _init_redis(self) -> None:
        """Initialize Redis connection and consumer group."""
        try:
            self._redis = await redis.from_url(
                self.redis_url,
                max_connections=50,
                decode_responses=False,  # We handle JSON ourselves
                socket_keepalive=True,
            )

            # Test connection
            await self._redis.ping()

            # Create consumer group if not exists
            try:
                await self._redis.xgroup_create(
                    self.request_stream,
                    self.consumer_group,
                    id="0",
                    mkstream=True,
                )
                logger.info(f"Created consumer group: {self.consumer_group}")
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
                logger.debug(f"Consumer group already exists: {self.consumer_group}")

            logger.info(f"✅ Redis connected: {self.redis_url}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            raise

    def rpc_method(
        self,
        method_name: str,
    ) -> Callable[[RPCHandler], RPCHandler]:
        """
        Decorator to register RPC method handler.

        Args:
            method_name: RPC method name to register

        Returns:
            Decorator function

        Example:
            >>> @bridge.rpc_method("send_notification")
            >>> async def send_notification(params: NotificationRequest) -> NotificationResponse:
            ...     return NotificationResponse(delivered=True, user_connected=True)
        """

        def decorator(handler: RPCHandler) -> RPCHandler:
            self._handlers[method_name] = handler
            logger.info(f"📝 Registered RPC method: {method_name}")
            return handler

        return decorator

    def register_method(self, method_name: str, handler: RPCHandler) -> None:
        """
        Register RPC method handler programmatically.

        Args:
            method_name: RPC method name
            handler: Async handler function

        Example:
            >>> async def my_handler(params: SomeParams) -> SomeResult:
            ...     return SomeResult(...)
            >>> bridge.register_method("my_method", my_handler)
        """
        self._handlers[method_name] = handler
        logger.info(f"📝 Registered RPC method: {method_name}")

    async def _handle_request(self, message_id: str, payload: Dict[str, Any]) -> None:
        """
        Handle single RPC request.

        Args:
            message_id: Redis Stream message ID
            payload: Request payload from stream
        """
        try:
            # Parse request payload
            request_data = json.loads(payload[b"payload"])
            correlation_id = request_data.get("correlation_id")
            method = request_data.get("method")
            reply_to = request_data.get("reply_to")

            if self.log_calls:
                logger.debug(f"📥 RPC request: {method} (cid={correlation_id})")

            # Check if method is registered
            if method not in self._handlers:
                raise ValueError(f"Unknown RPC method: {method}")

            handler = self._handlers[method]

            # Parse parameters (Pydantic validation happens here)
            params_data = request_data.get("params", {})

            # Execute handler
            result = await handler(params_data)

            # Build success response
            response = RPCResponse[type(result)](
                correlation_id=correlation_id,
                success=True,
                result=result,
            )

            # Send response
            await self._send_response(reply_to, response)

            if self.log_calls:
                logger.debug(f"📤 RPC response: {method} (success=True)")

            # Acknowledge message
            await self._redis.xack(self.request_stream, self.consumer_group, message_id)

        except ValidationError as e:
            # Pydantic validation error
            logger.warning(f"❌ Validation error: {e}")
            await self._send_error_response(
                reply_to,
                correlation_id,
                RPCError(
                    code=RPCErrorCode.VALIDATION_ERROR,
                    message=f"Validation error: {str(e)}",
                ),
            )

        except Exception as e:
            # Other errors
            logger.error(f"❌ RPC error: {e}", exc_info=True)
            await self._send_error_response(
                reply_to,
                correlation_id,
                RPCError(
                    code=RPCErrorCode.INTERNAL_ERROR,
                    message=str(e),
                ),
            )

    async def _send_response(self, reply_key: str, response: RPCResponse) -> None:
        """
        Send RPC response to Redis List.

        Args:
            reply_key: Redis List key
            response: RPC response model
        """
        try:
            # Serialize response
            response_json = response.model_dump_json()

            # Push to Redis List (LPUSH)
            await self._redis.lpush(reply_key, response_json)

            # Set TTL on response key
            await self._redis.expire(reply_key, self.response_key_ttl)

        except Exception as e:
            logger.error(f"Failed to send response: {e}")

    async def _send_error_response(
        self,
        reply_key: str,
        correlation_id: str,
        error: RPCError,
    ) -> None:
        """
        Send error response.

        Args:
            reply_key: Redis List key
            correlation_id: Request correlation ID
            error: Error details
        """
        response = RPCResponse[Any](
            correlation_id=correlation_id,
            success=False,
            error=error.message,
            error_code=error.code,
            result=None,
        )
        await self._send_response(reply_key, response)

    async def _listen_stream(self) -> None:
        """
        Listen to Redis Stream for incoming RPC requests.

        Uses XREADGROUP with blocking to efficiently wait for new messages.
        """
        logger.info(f"🎧 Listening to stream: {self.request_stream}")

        while self._running:
            try:
                # Read from stream (blocking, 1 second timeout)
                messages = await self._redis.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.request_stream: ">"},
                    count=10,  # Process up to 10 messages at a time
                    block=1000,  # Block for 1 second
                )

                if not messages:
                    continue

                # Process messages
                for stream, stream_messages in messages:
                    for message_id, payload in stream_messages:
                        # Handle request in background task
                        task = asyncio.create_task(
                            self._handle_request(message_id, payload)
                        )
                        self._tasks.append(task)

            except asyncio.CancelledError:
                logger.info("Stream listener cancelled")
                break
            except Exception as e:
                logger.error(f"Stream listener error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Backoff on error

    async def start(self) -> None:
        """
        Start RPC bridge.

        Initializes Redis connection and starts listening to stream.

        Example:
            >>> await bridge.start()
        """
        if self._running:
            logger.warning("Bridge already running")
            return

        logger.info("🚀 Starting RPC Bridge...")

        # Initialize Redis
        await self._init_redis()

        # Start listening
        self._running = True
        listen_task = asyncio.create_task(self._listen_stream())
        self._tasks.append(listen_task)

        logger.info(f"✅ RPC Bridge started (consumer={self.consumer_name})")

    async def stop(self) -> None:
        """
        Stop RPC bridge gracefully.

        Cancels all running tasks and closes Redis connection.

        Example:
            >>> await bridge.stop()
        """
        if not self._running:
            return

        logger.info("🛑 Stopping RPC Bridge...")

        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        # Wait for tasks to finish
        await asyncio.gather(*self._tasks, return_exceptions=True)

        # Close Redis
        if self._redis:
            await self._redis.close()

        logger.info("✅ RPC Bridge stopped")

    async def health_check(self) -> bool:
        """
        Check if bridge is healthy.

        Returns:
            True if healthy, False otherwise

        Example:
            >>> is_healthy = await bridge.health_check()
        """
        try:
            if not self._redis:
                return False

            # Ping Redis
            await self._redis.ping()

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"RPCBridge(consumer={self.consumer_name}, "
            f"stream={self.request_stream}, "
            f"methods={len(self._handlers)}, "
            f"running={self._running})"
        )


__all__ = ["RPCBridge"]
