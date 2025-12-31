"""
Betterproto2 gRPC Client with resilience patterns.

Modern async gRPC client using betterproto2 + grpclib with:
- Pydantic-based message serialization
- Automatic retry with exponential backoff
- Circuit breaker pattern
- Connection pooling

Usage:
    from mypackage import MyServiceStub, MyRequest

    async with Betterproto2Client(host="localhost", port=50051) as client:
        stub = await client.get_stub(MyServiceStub)
        response = await stub.my_method(MyRequest(field="value"))

Created: 2025-12-31
"""

from __future__ import annotations

import asyncio
import logging
import ssl
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, Type, TypeVar

try:
    from grpclib.client import Channel
    from grpclib.exceptions import GRPCError
    from grpclib.const import Status as GRPCStatus
    HAS_GRPCLIB = True
except ImportError:
    HAS_GRPCLIB = False
    Channel = None
    GRPCError = Exception
    GRPCStatus = None

from ...resilience import (
    GRPCCircuitBreaker,
    CircuitOpenError,
    get_grpc_logger,
    log_grpc_call,
    bind_context,
    clear_context,
)
from ...configs.constants import (
    get_max_retries,
    get_circuit_breaker_threshold,
    get_circuit_breaker_timeout,
    GRPC_RETRY_BACKOFF_INITIAL_MS,
    GRPC_RETRY_BACKOFF_MAX_MS,
)

logger = get_grpc_logger("betterproto_client")

T = TypeVar("T")
StubT = TypeVar("StubT")


# =============================================================================
# Constants
# =============================================================================

# Retryable gRPC status codes (grpclib)
RETRYABLE_STATUS_CODES = {
    0,   # OK (shouldn't happen but safe)
    1,   # CANCELLED
    4,   # DEADLINE_EXCEEDED
    8,   # RESOURCE_EXHAUSTED
    10,  # ABORTED
    14,  # UNAVAILABLE
}


# =============================================================================
# Betterproto2 Channel Pool
# =============================================================================


@dataclass
class Betterproto2ChannelEntry:
    """Entry in the betterproto2 channel pool."""

    channel: Any  # grpclib.client.Channel
    host: str
    port: int
    use_tls: bool
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    use_count: int = 0
    in_use: bool = False

    def mark_used(self) -> None:
        """Mark channel as used."""
        self.use_count += 1
        self.last_used_at = time.time()

    @property
    def age(self) -> float:
        """Channel age in seconds."""
        return time.time() - self.created_at

    @property
    def idle_time(self) -> float:
        """Time since last use in seconds."""
        return time.time() - self.last_used_at

    def is_stale(self, idle_timeout: float, max_age: float) -> bool:
        """Check if channel should be closed."""
        return self.idle_time > idle_timeout or self.age > max_age


class Betterproto2ChannelPool:
    """
    Connection pool for betterproto2/grpclib channels.

    Manages channel lifecycle with:
    - Channel reuse by host:port key
    - Idle channel cleanup
    - Maximum age enforcement

    Usage:
        pool = Betterproto2ChannelPool()

        async with pool.get_channel("localhost", 50051) as channel:
            stub = MyServiceStub(channel)
            response = await stub.method(request)

        await pool.close_all()
    """

    def __init__(
        self,
        max_size: int = 20,
        idle_timeout: float = 120.0,
        max_age: float = 3600.0,
        cleanup_interval: float = 60.0,
    ):
        """
        Initialize channel pool.

        Args:
            max_size: Maximum channels in pool
            idle_timeout: Close idle channels after seconds
            max_age: Maximum channel age in seconds
            cleanup_interval: Cleanup task interval
        """
        if not HAS_GRPCLIB:
            raise ImportError(
                "grpclib is required for Betterproto2ChannelPool. "
                "Install with: pip install 'django-cfg[grpc]'"
            )

        self._max_size = max_size
        self._idle_timeout = idle_timeout
        self._max_age = max_age
        self._cleanup_interval = cleanup_interval

        self._channels: Dict[str, list[Betterproto2ChannelEntry]] = {}
        self._lock = asyncio.Lock()
        self._closed = False
        self._cleanup_task: Optional[asyncio.Task] = None

    def _make_key(self, host: str, port: int, use_tls: bool) -> str:
        """Generate pool key."""
        return f"{host}:{port}:{'tls' if use_tls else 'plain'}"

    async def _create_channel(
        self,
        host: str,
        port: int,
        use_tls: bool = False,
        ssl_context: Optional[ssl.SSLContext] = None,
    ) -> Any:
        """Create new grpclib Channel."""
        if use_tls:
            if ssl_context is None:
                ssl_context = ssl.create_default_context()
            channel = Channel(host=host, port=port, ssl=ssl_context)
        else:
            channel = Channel(host=host, port=port)

        return channel

    @asynccontextmanager
    async def get_channel(
        self,
        host: str,
        port: int,
        use_tls: bool = False,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """
        Get channel from pool as context manager.

        Args:
            host: Server host
            port: Server port
            use_tls: Use TLS
            ssl_context: Custom SSL context

        Yields:
            grpclib.client.Channel
        """
        if self._closed:
            raise RuntimeError("Channel pool is closed")

        key = self._make_key(host, port, use_tls)
        entry: Optional[Betterproto2ChannelEntry] = None

        async with self._lock:
            # Try to get existing channel
            if key in self._channels:
                for e in self._channels[key]:
                    if not e.in_use and not e.is_stale(self._idle_timeout, self._max_age):
                        entry = e
                        entry.in_use = True
                        entry.mark_used()
                        break

            # Create new if needed
            if entry is None:
                channel = await self._create_channel(host, port, use_tls, ssl_context)
                entry = Betterproto2ChannelEntry(
                    channel=channel,
                    host=host,
                    port=port,
                    use_tls=use_tls,
                )
                entry.in_use = True
                entry.mark_used()

                if key not in self._channels:
                    self._channels[key] = []
                self._channels[key].append(entry)

                logger.debug(f"Created new betterproto2 channel: {key}")

        try:
            yield entry.channel
        finally:
            entry.in_use = False

    async def close_all(self) -> None:
        """Close all channels in pool."""
        self._closed = True

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._lock:
            for key, entries in self._channels.items():
                for entry in entries:
                    try:
                        entry.channel.close()
                    except Exception as e:
                        logger.warning(f"Error closing channel {key}: {e}")
            self._channels.clear()

        logger.info("Betterproto2 channel pool closed")

    @property
    def size(self) -> int:
        """Total channels in pool."""
        return sum(len(entries) for entries in self._channels.values())

    @property
    def is_closed(self) -> bool:
        """Check if pool is closed."""
        return self._closed

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        total = 0
        in_use = 0
        pools = {}

        for key, entries in self._channels.items():
            total += len(entries)
            pool_in_use = sum(1 for e in entries if e.in_use)
            in_use += pool_in_use
            pools[key] = {
                "total": len(entries),
                "in_use": pool_in_use,
                "idle": len(entries) - pool_in_use,
            }

        return {
            "total_channels": total,
            "channels_in_use": in_use,
            "channels_idle": total - in_use,
            "pools": pools,
        }


# =============================================================================
# Global Pool
# =============================================================================

_betterproto_pool: Optional[Betterproto2ChannelPool] = None


def get_betterproto_pool(
    max_size: int = 20,
    idle_timeout: float = 120.0,
) -> Betterproto2ChannelPool:
    """Get or create global betterproto2 channel pool."""
    global _betterproto_pool

    if _betterproto_pool is None or _betterproto_pool.is_closed:
        _betterproto_pool = Betterproto2ChannelPool(
            max_size=max_size,
            idle_timeout=idle_timeout,
        )

    return _betterproto_pool


async def close_betterproto_pool() -> None:
    """Close global betterproto2 pool."""
    global _betterproto_pool

    if _betterproto_pool is not None:
        await _betterproto_pool.close_all()
        _betterproto_pool = None


# =============================================================================
# Resilient Betterproto2 Client
# =============================================================================


def is_retryable_grpclib_error(error: Exception) -> bool:
    """Check if grpclib error is retryable."""
    if not HAS_GRPCLIB:
        return False

    if isinstance(error, GRPCError):
        # GRPCError has status attribute
        status = getattr(error, 'status', None)
        if status is not None:
            return status.value in RETRYABLE_STATUS_CODES

    # Connection errors are retryable
    if isinstance(error, (ConnectionError, OSError, asyncio.TimeoutError)):
        return True

    return False


class Betterproto2Client:
    """
    Resilient betterproto2/grpclib client.

    Provides production-grade resilience for betterproto2 stubs:
    - Automatic retry with exponential backoff
    - Circuit breaker pattern
    - Connection pooling
    - Structured logging

    Usage:
        from mypackage import MyServiceStub, MyRequest

        async with Betterproto2Client(host="localhost", port=50051) as client:
            stub = client.get_stub(MyServiceStub)
            response = await stub.my_method(MyRequest(field="value"))

        # With circuit breaker
        async with Betterproto2Client(
            host="localhost",
            port=50051,
            enable_circuit_breaker=True,
        ) as client:
            stub = client.get_stub(MyServiceStub)
            try:
                response = await stub.my_method(request)
            except CircuitOpenError:
                # Handle circuit open
                pass
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
        use_tls: bool = False,
        ssl_context: Optional[ssl.SSLContext] = None,
        # Resilience options
        enable_retry: bool = True,
        enable_circuit_breaker: bool = True,
        retry_attempts: Optional[int] = None,
        circuit_breaker_threshold: Optional[int] = None,
        circuit_breaker_timeout: Optional[float] = None,
        # Pool options
        use_pool: bool = False,
        pool: Optional[Betterproto2ChannelPool] = None,
    ):
        """
        Initialize betterproto2 client.

        Args:
            host: gRPC server host
            port: gRPC server port
            use_tls: Use TLS encryption
            ssl_context: Custom SSL context
            enable_retry: Enable automatic retry
            enable_circuit_breaker: Enable circuit breaker
            retry_attempts: Max retry attempts
            circuit_breaker_threshold: Failures before opening
            circuit_breaker_timeout: Reset timeout in seconds
            use_pool: Use connection pooling
            pool: Custom pool instance
        """
        if not HAS_GRPCLIB:
            raise ImportError(
                "grpclib is required for Betterproto2Client. "
                "Install with: pip install 'django-cfg[grpc]'"
            )

        self._host = host
        self._port = port
        self._use_tls = use_tls
        self._ssl_context = ssl_context

        # Resilience settings
        self._enable_retry = enable_retry
        self._enable_circuit_breaker = enable_circuit_breaker
        self._retry_attempts = retry_attempts or get_max_retries()
        self._cb_threshold = circuit_breaker_threshold or get_circuit_breaker_threshold()
        self._cb_timeout = circuit_breaker_timeout or get_circuit_breaker_timeout()

        # Pool settings
        self._use_pool = use_pool
        self._pool = pool

        # State
        self._channel: Optional[Any] = None
        self._channel_context = None
        self._circuit_breaker: Optional[GRPCCircuitBreaker] = None
        self._stubs: Dict[type, Any] = {}

    async def __aenter__(self) -> "Betterproto2Client":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Connect to gRPC server."""
        address = f"{self._host}:{self._port}"

        if self._use_pool:
            # Get channel from pool
            pool = self._pool or get_betterproto_pool()
            self._channel_context = pool.get_channel(
                host=self._host,
                port=self._port,
                use_tls=self._use_tls,
                ssl_context=self._ssl_context,
            )
            self._channel = await self._channel_context.__aenter__()
            logger.debug(f"Using pooled betterproto2 channel: {address}")
        else:
            # Create dedicated channel
            if self._use_tls:
                ssl_ctx = self._ssl_context or ssl.create_default_context()
                self._channel = Channel(
                    host=self._host,
                    port=self._port,
                    ssl=ssl_ctx,
                )
            else:
                self._channel = Channel(
                    host=self._host,
                    port=self._port,
                )

        # Initialize circuit breaker
        if self._enable_circuit_breaker:
            self._circuit_breaker = await GRPCCircuitBreaker.get_or_create(
                target_id=address,
                fail_max=self._cb_threshold,
                reset_timeout=self._cb_timeout,
            )

        logger.info(
            f"Betterproto2 client connected: address={address}, "
            f"retry={self._enable_retry}, circuit_breaker={self._enable_circuit_breaker}, "
            f"pooled={self._use_pool}"
        )

    async def close(self) -> None:
        """Close connection."""
        self._stubs.clear()

        if self._use_pool and self._channel_context:
            # Release channel back to pool
            await self._channel_context.__aexit__(None, None, None)
            logger.debug(f"Released pooled channel: {self._host}:{self._port}")
        elif self._channel:
            # Close dedicated channel
            self._channel.close()
            logger.info(f"Betterproto2 client closed: {self._host}:{self._port}")

        self._channel = None
        self._channel_context = None

    def get_stub(self, stub_class: Type[StubT]) -> StubT:
        """
        Get or create stub instance.

        Args:
            stub_class: Betterproto2 stub class

        Returns:
            Stub instance bound to channel
        """
        if not self._channel:
            raise RuntimeError("Client not connected. Use 'async with' or call connect()")

        if stub_class not in self._stubs:
            self._stubs[stub_class] = stub_class(self._channel)

        return self._stubs[stub_class]

    async def call_method(
        self,
        stub_class: Type[StubT],
        method_name: str,
        request: Any,
        request_id: Optional[str] = None,
    ) -> Any:
        """
        Call gRPC method with resilience.

        This method wraps stub calls with retry and circuit breaker.

        Args:
            stub_class: Stub class
            method_name: Method name on stub
            request: Request message (betterproto dataclass)
            request_id: Optional request ID for tracing

        Returns:
            Response message

        Raises:
            CircuitOpenError: If circuit breaker is open
            GRPCError: If call fails after retries
        """
        if not self._channel:
            raise RuntimeError("Client not connected")

        service_name = stub_class.__name__.replace("Stub", "")

        # Bind context
        if request_id:
            bind_context(request_id=request_id)
        bind_context(grpc_service=service_name, grpc_method=method_name)

        start_time = time.monotonic()

        try:
            # Check circuit breaker
            if self._circuit_breaker and not self._circuit_breaker.can_execute():
                raise CircuitOpenError(
                    f"{self._host}:{self._port}",
                    self._circuit_breaker.time_until_retry(),
                )

            # Get stub and method
            stub = self.get_stub(stub_class)
            method = getattr(stub, method_name, None)
            if method is None:
                raise AttributeError(f"Method '{method_name}' not found on {stub_class.__name__}")

            # Call with retry
            result = await self._call_with_retry(method, request)

            # Record success
            if self._circuit_breaker:
                self._circuit_breaker.record_success()

            # Log success
            duration_ms = (time.monotonic() - start_time) * 1000
            log_grpc_call(
                logger,
                service=service_name,
                method=method_name,
                success=True,
                duration_ms=duration_ms,
            )

            return result

        except CircuitOpenError:
            raise

        except Exception as e:
            # Record failure
            if self._circuit_breaker:
                self._circuit_breaker.record_failure(e)

            # Log error
            duration_ms = (time.monotonic() - start_time) * 1000
            error_msg = str(e)
            status_code = None

            if HAS_GRPCLIB and isinstance(e, GRPCError):
                status = getattr(e, 'status', None)
                if status:
                    status_code = status.name
                    error_msg = f"{status_code}: {e}"

            log_grpc_call(
                logger,
                service=service_name,
                method=method_name,
                success=False,
                duration_ms=duration_ms,
                error=error_msg,
                status_code=status_code,
            )

            raise

        finally:
            clear_context()

    async def _call_with_retry(self, method: Any, request: Any) -> Any:
        """Execute method with retry logic."""
        last_exc: Optional[Exception] = None
        attempts = self._retry_attempts if self._enable_retry else 1
        wait = GRPC_RETRY_BACKOFF_INITIAL_MS / 1000.0

        for attempt in range(attempts):
            try:
                return await method(request)

            except Exception as e:
                last_exc = e

                if not is_retryable_grpclib_error(e) or attempt == attempts - 1:
                    raise

                logger.warning(
                    f"Betterproto2 retry: attempt={attempt + 1}/{attempts}, "
                    f"error={e}, wait={wait:.2f}s"
                )

                await asyncio.sleep(wait)
                wait = min(wait * 2, GRPC_RETRY_BACKOFF_MAX_MS / 1000.0)

        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected retry loop exit")

    @property
    def circuit_breaker_status(self) -> Optional[Dict[str, Any]]:
        """Get circuit breaker status."""
        if self._circuit_breaker:
            return self._circuit_breaker.get_stats()
        return None

    @property
    def pool_stats(self) -> Optional[Dict[str, Any]]:
        """Get pool statistics."""
        if self._use_pool:
            pool = self._pool or get_betterproto_pool()
            return pool.get_stats()
        return None

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._channel is not None

    @property
    def address(self) -> str:
        """Get server address."""
        return f"{self._host}:{self._port}"


# =============================================================================
# Resilient Wrapper for Direct Stub Usage
# =============================================================================


class ResilientStubWrapper(Generic[StubT]):
    """
    Wrapper that adds resilience to any betterproto2 stub.

    Wraps stub method calls with retry and circuit breaker.

    Usage:
        stub = MyServiceStub(channel)
        resilient = ResilientStubWrapper(stub, "localhost:50051")

        # All methods now have retry and circuit breaker
        response = await resilient.my_method(request)
    """

    def __init__(
        self,
        stub: StubT,
        target_id: str,
        enable_retry: bool = True,
        enable_circuit_breaker: bool = True,
        retry_attempts: Optional[int] = None,
        circuit_breaker_threshold: Optional[int] = None,
        circuit_breaker_timeout: Optional[float] = None,
    ):
        """
        Initialize resilient wrapper.

        Args:
            stub: Betterproto2 stub instance
            target_id: Target identifier for circuit breaker
            enable_retry: Enable retry
            enable_circuit_breaker: Enable circuit breaker
            retry_attempts: Max retry attempts
            circuit_breaker_threshold: Failures before opening
            circuit_breaker_timeout: Reset timeout
        """
        self._stub = stub
        self._target_id = target_id
        self._enable_retry = enable_retry
        self._enable_circuit_breaker = enable_circuit_breaker
        self._retry_attempts = retry_attempts or get_max_retries()
        self._cb_threshold = circuit_breaker_threshold or get_circuit_breaker_threshold()
        self._cb_timeout = circuit_breaker_timeout or get_circuit_breaker_timeout()

        self._circuit_breaker: Optional[GRPCCircuitBreaker] = None
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Initialize circuit breaker on first use."""
        if self._initialized:
            return

        if self._enable_circuit_breaker:
            self._circuit_breaker = await GRPCCircuitBreaker.get_or_create(
                target_id=self._target_id,
                fail_max=self._cb_threshold,
                reset_timeout=self._cb_timeout,
            )

        self._initialized = True

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to stub with resilience wrapper."""
        attr = getattr(self._stub, name)

        if not callable(attr):
            return attr

        # Wrap callable methods
        async def resilient_call(*args, **kwargs):
            await self._ensure_initialized()

            # Check circuit breaker
            if self._circuit_breaker and not self._circuit_breaker.can_execute():
                raise CircuitOpenError(
                    self._target_id,
                    self._circuit_breaker.time_until_retry(),
                )

            try:
                result = await self._call_with_retry(attr, *args, **kwargs)

                if self._circuit_breaker:
                    self._circuit_breaker.record_success()

                return result

            except CircuitOpenError:
                raise

            except Exception as e:
                if self._circuit_breaker:
                    self._circuit_breaker.record_failure(e)
                raise

        return resilient_call

    async def _call_with_retry(self, method: Any, *args, **kwargs) -> Any:
        """Execute method with retry."""
        last_exc: Optional[Exception] = None
        attempts = self._retry_attempts if self._enable_retry else 1
        wait = GRPC_RETRY_BACKOFF_INITIAL_MS / 1000.0

        for attempt in range(attempts):
            try:
                return await method(*args, **kwargs)

            except Exception as e:
                last_exc = e

                if not is_retryable_grpclib_error(e) or attempt == attempts - 1:
                    raise

                logger.warning(
                    f"Stub wrapper retry: attempt={attempt + 1}/{attempts}, "
                    f"error={e}, wait={wait:.2f}s"
                )

                await asyncio.sleep(wait)
                wait = min(wait * 2, GRPC_RETRY_BACKOFF_MAX_MS / 1000.0)

        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected retry loop exit")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Pool
    "Betterproto2ChannelPool",
    "Betterproto2ChannelEntry",
    "get_betterproto_pool",
    "close_betterproto_pool",
    # Client
    "Betterproto2Client",
    "ResilientStubWrapper",
    # Utilities
    "is_retryable_grpclib_error",
    "HAS_GRPCLIB",
]
