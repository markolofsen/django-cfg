"""
Resilient gRPC Client with retry and circuit breaker.

Wraps DynamicGRPCClient with production-grade resilience patterns.

Usage:
    # Sync usage
    client = ResilientGRPCClient(host="localhost", port=50051)
    result = client.call_method("MyService", "MyMethod", {"field": "value"})

    # Async usage
    async with AsyncResilientGRPCClient(host="localhost", port=50051) as client:
        result = await client.call_method("MyService", "MyMethod", {"field": "value"})

Created: 2025-12-31
"""

from __future__ import annotations

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

import grpc
import grpc.aio

from .client import DynamicGRPCClient
from .pool import get_channel_pool, get_sync_channel_pool, GRPCChannelPool, SyncGRPCChannelPool
from ...configs.channels import ClientChannelConfig
from ...configs.tls import TLSConfig
from ...resilience import (
    GRPCCircuitBreaker,
    CircuitOpenError,
    is_retryable_error,
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

logger = get_grpc_logger("resilient_client")

T = TypeVar("T")


# =============================================================================
# Sync Retry Decorator
# =============================================================================


def sync_retry(
    attempts: int = 5,
    wait_initial: float = 0.1,
    wait_max: float = 10.0,
    backoff_multiplier: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Synchronous retry decorator with exponential backoff.

    Args:
        attempts: Maximum retry attempts
        wait_initial: Initial wait time in seconds
        wait_max: Maximum wait time in seconds
        backoff_multiplier: Multiplier for each retry

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: Exception | None = None
            wait = wait_initial

            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except grpc.RpcError as e:
                    last_exc = e
                    if not is_retryable_error(e) or attempt == attempts - 1:
                        raise
                    logger.warning(
                        "grpc_retry",
                        attempt=attempt + 1,
                        max_attempts=attempts,
                        error_code=e.code().name if hasattr(e, "code") else "UNKNOWN",
                        wait_seconds=wait,
                    )
                    time.sleep(wait)
                    wait = min(wait * backoff_multiplier, wait_max)
                except (OSError, ConnectionError) as e:
                    last_exc = e
                    if attempt == attempts - 1:
                        raise
                    logger.warning(
                        "connection_retry",
                        attempt=attempt + 1,
                        max_attempts=attempts,
                        error=str(e),
                        wait_seconds=wait,
                    )
                    time.sleep(wait)
                    wait = min(wait * backoff_multiplier, wait_max)

            if last_exc:
                raise last_exc
            raise RuntimeError("Unexpected retry loop exit")

        return wrapper

    return decorator


# =============================================================================
# Resilient Sync Client
# =============================================================================


class ResilientGRPCClient:
    """
    Synchronous gRPC client with resilience patterns.

    Wraps DynamicGRPCClient with:
    - Automatic retry with exponential backoff
    - Per-target circuit breaker
    - Structured logging

    Usage:
        client = ResilientGRPCClient(host="localhost", port=50051)

        # With retry and circuit breaker
        result = client.call_method(
            service_name="mypackage.MyService",
            method_name="GetData",
            request_data={"id": "123"},
        )

        # Check circuit breaker status
        print(client.circuit_breaker_status)

        # Close when done
        client.close()

        # Or use as context manager
        with ResilientGRPCClient(host="localhost") as client:
            result = client.call_method(...)
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        use_tls: bool = None,
        config: ClientChannelConfig = None,
        tls_config: TLSConfig = None,
        # Resilience options
        enable_retry: bool = True,
        enable_circuit_breaker: bool = True,
        retry_attempts: int = None,
        circuit_breaker_threshold: int = None,
        circuit_breaker_timeout: float = None,
    ):
        """
        Initialize resilient gRPC client.

        Args:
            host: gRPC server host
            port: gRPC server port
            use_tls: Whether to use TLS
            config: Channel configuration
            tls_config: TLS configuration
            enable_retry: Enable automatic retry
            enable_circuit_breaker: Enable circuit breaker
            retry_attempts: Max retry attempts (default from config)
            circuit_breaker_threshold: Failures before opening (default from config)
            circuit_breaker_timeout: Reset timeout in seconds (default from config)
        """
        # Create underlying client
        self._client = DynamicGRPCClient(
            host=host,
            port=port,
            use_tls=use_tls,
            config=config,
            tls_config=tls_config,
        )

        # Resilience settings
        self._enable_retry = enable_retry
        self._enable_circuit_breaker = enable_circuit_breaker
        self._retry_attempts = retry_attempts or get_max_retries()

        # Circuit breaker
        self._circuit_breaker: Optional[GRPCCircuitBreaker] = None
        if enable_circuit_breaker:
            target_id = self._client._config.address
            self._circuit_breaker = GRPCCircuitBreaker.get_or_create_sync(
                target_id=target_id,
                fail_max=circuit_breaker_threshold or get_circuit_breaker_threshold(),
                reset_timeout=circuit_breaker_timeout or get_circuit_breaker_timeout(),
            )

        logger.info(
            "resilient_client_initialized",
            address=self._client._config.address,
            retry_enabled=enable_retry,
            circuit_breaker_enabled=enable_circuit_breaker,
        )

    def call_method(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Call gRPC method with resilience.

        Args:
            service_name: Full service name
            method_name: Method name
            request_data: Request payload as dictionary
            metadata: Optional gRPC metadata
            timeout: Call timeout in seconds
            request_id: Optional request ID for tracing

        Returns:
            Response as dictionary

        Raises:
            CircuitOpenError: If circuit breaker is open
            grpc.RpcError: If call fails after retries
        """
        # Bind request context for logging
        if request_id:
            bind_context(request_id=request_id)

        bind_context(
            grpc_service=service_name,
            grpc_method=method_name,
        )

        start_time = time.monotonic()

        try:
            # Check circuit breaker
            if self._circuit_breaker and not self._circuit_breaker.can_execute():
                raise CircuitOpenError(
                    self._client._config.address,
                    self._circuit_breaker.time_until_retry(),
                )

            # Call with or without retry
            if self._enable_retry:
                result = self._call_with_retry(
                    service_name=service_name,
                    method_name=method_name,
                    request_data=request_data,
                    metadata=metadata,
                    timeout=timeout,
                )
            else:
                result = self._client.call_method(
                    service_name=service_name,
                    method_name=method_name,
                    request_data=request_data,
                    metadata=metadata,
                    timeout=timeout,
                )

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
            # Don't count circuit open as failure
            raise

        except Exception as e:
            # Record failure
            if self._circuit_breaker:
                self._circuit_breaker.record_failure(e)

            # Log error
            duration_ms = (time.monotonic() - start_time) * 1000
            error_msg = str(e)
            status_code = None
            if isinstance(e, grpc.RpcError):
                try:
                    status_code = e.code().name
                    error_msg = f"{status_code}: {e.details()}"
                except Exception:
                    pass

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

    @sync_retry(
        attempts=5,
        wait_initial=GRPC_RETRY_BACKOFF_INITIAL_MS / 1000.0,
        wait_max=GRPC_RETRY_BACKOFF_MAX_MS / 1000.0,
    )
    def _call_with_retry(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Internal method with retry decorator."""
        return self._client.call_method(
            service_name=service_name,
            method_name=method_name,
            request_data=request_data,
            metadata=metadata,
            timeout=timeout,
        )

    @property
    def circuit_breaker_status(self) -> Optional[Dict[str, Any]]:
        """Get circuit breaker status."""
        if self._circuit_breaker:
            return self._circuit_breaker.get_stats()
        return None

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client.is_connected()

    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return self._client.is_healthy()

    def close(self) -> None:
        """Close the client."""
        self._client.close()
        logger.info("resilient_client_closed", address=self._client._config.address)

    def __enter__(self) -> "ResilientGRPCClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"<ResilientGRPCClient address={self._client._config.address}>"


# =============================================================================
# Resilient Async Client
# =============================================================================


class AsyncResilientGRPCClient:
    """
    Asynchronous gRPC client with resilience patterns.

    Uses grpc.aio for native async support with:
    - Automatic retry with exponential backoff (stamina)
    - Per-target circuit breaker (aiobreaker)
    - Structured logging (structlog)
    - Connection pooling (optional)

    Usage:
        async with AsyncResilientGRPCClient(host="localhost") as client:
            result = await client.call_method(
                service_name="mypackage.MyService",
                method_name="GetData",
                request_data={"id": "123"},
            )

        # With connection pooling
        async with AsyncResilientGRPCClient(host="localhost", use_pool=True) as client:
            result = await client.call_method(...)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
        use_tls: bool = False,
        config: ClientChannelConfig = None,
        # Resilience options
        enable_retry: bool = True,
        enable_circuit_breaker: bool = True,
        retry_attempts: int = None,
        circuit_breaker_threshold: int = None,
        circuit_breaker_timeout: float = None,
        # Pool options
        use_pool: bool = False,
        pool: Optional[GRPCChannelPool] = None,
    ):
        """
        Initialize async resilient client.

        Args:
            host: gRPC server host
            port: gRPC server port
            use_tls: Whether to use TLS
            config: Channel configuration
            enable_retry: Enable automatic retry
            enable_circuit_breaker: Enable circuit breaker
            retry_attempts: Max retry attempts
            circuit_breaker_threshold: Failures before opening
            circuit_breaker_timeout: Reset timeout in seconds
            use_pool: Use connection pooling
            pool: Custom pool instance (uses global pool if None)
        """
        self._host = host
        self._port = port
        self._use_tls = use_tls
        self._config = config or ClientChannelConfig(address=f"{host}:{port}", use_tls=use_tls)

        self._enable_retry = enable_retry
        self._enable_circuit_breaker = enable_circuit_breaker
        self._retry_attempts = retry_attempts or get_max_retries()
        self._cb_threshold = circuit_breaker_threshold or get_circuit_breaker_threshold()
        self._cb_timeout = circuit_breaker_timeout or get_circuit_breaker_timeout()

        # Pool settings
        self._use_pool = use_pool
        self._pool = pool
        self._owns_channel = not use_pool  # If using pool, pool owns the channel

        self._channel: Optional[grpc.aio.Channel] = None
        self._circuit_breaker: Optional[GRPCCircuitBreaker] = None

    async def __aenter__(self) -> "AsyncResilientGRPCClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Connect to gRPC server."""
        address = self._config.address
        channel_options = self._config.get_channel_options()

        if self._use_pool:
            # Get channel from pool
            pool = self._pool or get_channel_pool()
            self._channel = await pool.get_channel(
                address=address,
                use_tls=self._use_tls,
                channel_options=channel_options,
            )
            logger.debug("async_client_using_pooled_channel", address=address)
        else:
            # Create dedicated channel
            if self._use_tls:
                credentials = grpc.ssl_channel_credentials()
                self._channel = grpc.aio.secure_channel(address, credentials, options=channel_options)
            else:
                self._channel = grpc.aio.insecure_channel(address, options=channel_options)

            # Wait for channel to be ready
            await self._channel.channel_ready()

        # Initialize circuit breaker
        if self._enable_circuit_breaker:
            self._circuit_breaker = await GRPCCircuitBreaker.get_or_create(
                target_id=address,
                fail_max=self._cb_threshold,
                reset_timeout=self._cb_timeout,
            )

        logger.info(
            "async_client_connected",
            address=address,
            retry_enabled=self._enable_retry,
            circuit_breaker_enabled=self._enable_circuit_breaker,
            pooled=self._use_pool,
        )

    async def close(self) -> None:
        """Close the channel (only if not pooled)."""
        if self._channel and self._owns_channel:
            await self._channel.close()
            logger.info("async_client_closed", address=self._config.address)
        elif self._channel and not self._owns_channel:
            # Channel belongs to pool, just log release
            logger.debug("async_client_released_pooled_channel", address=self._config.address)

    async def call_method(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        request_class: type,
        response_class: type,
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        """
        Call gRPC method asynchronously with resilience.

        Args:
            service_name: Full service name
            method_name: Method name
            request_data: Request payload as dictionary
            request_class: Protobuf request message class
            response_class: Protobuf response message class
            metadata: Optional gRPC metadata
            timeout: Call timeout in seconds
            request_id: Optional request ID for tracing

        Returns:
            Response message

        Raises:
            CircuitOpenError: If circuit breaker is open
            grpc.aio.AioRpcError: If call fails after retries
        """
        if not self._channel:
            raise RuntimeError("Client not connected. Use 'async with' or call connect()")

        # Bind context
        if request_id:
            bind_context(request_id=request_id)
        bind_context(grpc_service=service_name, grpc_method=method_name)

        start_time = time.monotonic()

        try:
            # Check circuit breaker
            if self._circuit_breaker and not self._circuit_breaker.can_execute():
                raise CircuitOpenError(
                    self._config.address,
                    self._circuit_breaker.time_until_retry(),
                )

            # Make call
            result = await self._call_with_resilience(
                service_name=service_name,
                method_name=method_name,
                request_data=request_data,
                request_class=request_class,
                response_class=response_class,
                metadata=metadata,
                timeout=timeout or self._config.call_timeout,
            )

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
            if isinstance(e, grpc.aio.AioRpcError):
                status_code = e.code().name
                error_msg = f"{status_code}: {e.details()}"

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

    async def _call_with_resilience(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        request_class: type,
        response_class: type,
        metadata: Optional[Dict[str, str]] = None,
        timeout: float = 5.0,
    ) -> Any:
        """Internal method with retry logic."""
        from google.protobuf import json_format

        # Build request message
        request = json_format.ParseDict(request_data, request_class())

        # Prepare metadata
        grpc_metadata = [(k, v) for k, v in (metadata or {}).items()]

        # Build method path
        full_method = f"/{service_name}/{method_name}"

        # Retry logic
        last_exc: Exception | None = None
        attempts = self._retry_attempts if self._enable_retry else 1
        wait = GRPC_RETRY_BACKOFF_INITIAL_MS / 1000.0

        for attempt in range(attempts):
            try:
                response = await self._channel.unary_unary(
                    full_method,
                    request_serializer=request.SerializeToString,
                    response_deserializer=response_class.FromString,
                )(request, metadata=grpc_metadata, timeout=timeout)
                return response

            except grpc.aio.AioRpcError as e:
                last_exc = e
                if not is_retryable_error(e) or attempt == attempts - 1:
                    raise
                logger.warning(
                    "async_grpc_retry",
                    attempt=attempt + 1,
                    max_attempts=attempts,
                    error_code=e.code().name,
                    wait_seconds=wait,
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
        """Get pool statistics (if using pooled connection)."""
        if self._use_pool:
            pool = self._pool or get_channel_pool()
            return pool.get_stats()
        return None

    @property
    def is_pooled(self) -> bool:
        """Check if client is using pooled connection."""
        return self._use_pool


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ResilientGRPCClient",
    "AsyncResilientGRPCClient",
    "sync_retry",
]
