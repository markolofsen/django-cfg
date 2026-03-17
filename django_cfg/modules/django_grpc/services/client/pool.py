"""
gRPC Channel Pool for connection reuse.

Provides efficient channel pooling to reduce connection overhead.
Channels are reused across requests and automatically cleaned up when idle.

Usage:
    # Global pool (recommended)
    from django_cfg.modules.django_grpc.services.client.pool import get_channel_pool

    pool = get_channel_pool()
    channel = await pool.get_channel("localhost:50051")

    # Or use context manager
    async with pool.pooled_channel("localhost:50051") as channel:
        # use channel
        pass

    # Cleanup
    await pool.close_all()

Created: 2025-12-31
"""

from __future__ import annotations

import asyncio
import time
import weakref
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, NamedTuple, Optional

from django_cfg.modules.django_grpc.config.pool import GrpcPoolConfig

import grpc
import grpc.aio

from django_cfg.utils import get_logger

logger = get_logger("grpc.pool")

# I-4: grace period for channel close.
# bare close() sends immediate GOAWAY and cancels all in-flight RPCs.
# close(grace=N) allows in-flight RPCs to complete before the connection is torn.
# Used in close_channel() and close_all(); _cleanup_stale() keeps bare close()
# because those channels are confirmed idle (no in-flight RPCs).
_CLOSE_GRACE_SECONDS = 5.0


# =============================================================================
# Pool Configuration
# =============================================================================


def _get_pool_config() -> GrpcPoolConfig:
    """Read pool config from the grpc_module singleton. Falls back to defaults."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import settings
        return settings.pool
    except Exception:
        return GrpcPoolConfig()


# PoolConfig alias kept for backwards compatibility with any external code.
# Use GrpcPoolConfig directly for new code.
PoolConfig = GrpcPoolConfig


# =============================================================================
# Channel Entry
# =============================================================================


@dataclass
class ChannelEntry:
    """Entry in the channel pool."""

    channel: grpc.aio.Channel
    address: str
    use_tls: bool
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    use_count: int = 0
    in_use: bool = False

    def mark_used(self) -> None:
        """Mark channel as recently used."""
        self.last_used_at = time.time()
        self.use_count += 1

    @property
    def age(self) -> float:
        """Get channel age in seconds."""
        return time.time() - self.created_at

    @property
    def idle_time(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self.last_used_at

    def is_stale(self, idle_timeout: float, max_age: float) -> bool:
        """Check if channel is stale and should be closed."""
        return self.idle_time > idle_timeout or self.age > max_age


# =============================================================================
# Async Channel Pool
# =============================================================================


class GRPCChannelPool:
    """
    Async gRPC channel pool for connection reuse.

    Features:
    - Reuses channels across requests
    - Automatic cleanup of idle channels
    - Per-address channel management
    - Thread-safe with asyncio locks
    - Configurable pool size and timeouts

    Usage:
        pool = GRPCChannelPool()

        # Get a channel (creates or reuses)
        channel = await pool.get_channel("localhost:50051")

        # Use context manager for automatic release
        async with pool.pooled_channel("localhost:50051") as channel:
            # use channel...
            pass

        # Cleanup
        await pool.close_all()
    """

    def __init__(self, config: Optional[GrpcPoolConfig] = None):
        """
        Initialize channel pool.

        Args:
            config: Pool configuration (uses grpc_module config if None)
        """
        self._config = config or _get_pool_config()
        self._channels: dict[str, list[ChannelEntry]] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._closed = False

        logger.info(
            f"Channel pool initialized: max_size={self._config.max_size}, "
            f"idle_timeout={self._config.idle_timeout}"
        )

    async def get_channel(
        self,
        address: str,
        use_tls: bool = False,
        channel_options: Optional[list] = None,
        tls_config=None,  # I-3: Optional[TLSConfig] — avoids import cycle at module level
    ) -> grpc.aio.Channel:
        """
        Get a channel from the pool or create a new one.

        Args:
            address: Server address (host:port)
            use_tls: Whether to use TLS
            channel_options: Optional gRPC channel options

        Returns:
            gRPC async channel

        Raises:
            RuntimeError: If pool is closed
        """
        if self._closed:
            raise RuntimeError("Channel pool is closed")

        pool_key = self._make_key(address, use_tls)

        # B-3 fix: do NOT hold _lock during channel creation.
        # _create_channel() calls channel.channel_ready() which can block up
        # to channel_ready_timeout (default 5 s). Holding _lock during that
        # wait serialises ALL callers — the whole pool stalls.
        #
        # Pattern: check under lock → create outside lock → insert under lock.
        # A small window exists where two tasks both miss the pool check and
        # each create a channel independently; both get inserted and are valid
        # — a minor over-allocation rather than a deadlock.

        async with self._lock:
            self._ensure_cleanup_task()
            channel = self._get_available_channel(pool_key)

        if channel:
            logger.debug(f"Channel reused: address={address}, pool_key={pool_key}")
            return channel

        # Create channel outside the lock (may take up to channel_ready_timeout)
        channel = await self._create_channel(address, use_tls, channel_options, tls_config=tls_config)

        async with self._lock:
            # Re-check: another task may have created a channel for this key
            # while we were waiting. Prefer the existing one to avoid leaking
            # the channel we just created.
            existing = self._get_available_channel(pool_key)
            if existing:
                # Close the redundant channel we created
                try:
                    await channel.close()
                except Exception as e:
                    logger.debug("Failed to close redundant channel: %s", e)
                logger.debug(f"Channel discarded (race): address={address}, pool_key={pool_key}")
                return existing

            entry = ChannelEntry(
                channel=channel,
                address=address,
                use_tls=use_tls,
            )
            entry.mark_used()

            if pool_key not in self._channels:
                self._channels[pool_key] = []
            self._channels[pool_key].append(entry)

            logger.debug(
                f"Channel created: address={address}, pool_key={pool_key}, "
                f"pool_size={len(self._channels[pool_key])}"
            )

            return channel

    def _make_key(self, address: str, use_tls: bool) -> str:
        """Create pool key from address and TLS setting."""
        return f"{address}:{'tls' if use_tls else 'plain'}"

    def _get_available_channel(self, pool_key: str) -> Optional[grpc.aio.Channel]:
        """Get available channel from pool."""
        if pool_key not in self._channels:
            return None

        entries = self._channels[pool_key]

        for entry in entries:
            if not entry.in_use:
                # Check if channel is still valid
                if not entry.is_stale(
                    self._config.idle_timeout,
                    self._config.max_age,
                ):
                    # I-5: skip channels in terminal/transient-failure states.
                    # SHUTDOWN channels can never recover; TRANSIENT_FAILURE channels
                    # indicate the remote is unreachable and should not be reused.
                    # check_connectivity_state(False) reads the cached state without
                    # triggering a connection attempt (try_to_connect=False).
                    try:
                        state = entry.channel.get_state(try_to_connect=False)
                        if state in (
                            grpc.ChannelConnectivity.SHUTDOWN,
                            grpc.ChannelConnectivity.TRANSIENT_FAILURE,
                        ):
                            logger.debug(
                                "I-5: skipping channel in bad state: "
                                "pool_key=%s state=%s", pool_key, state
                            )
                            continue
                    except Exception:
                        # get_state() is best-effort; don't break pool on failure
                        pass
                    entry.mark_used()
                    return entry.channel

        return None

    async def _create_channel(
        self,
        address: str,
        use_tls: bool,
        channel_options: Optional[list] = None,
        tls_config=None,  # I-3: Optional[TLSConfig]
    ) -> grpc.aio.Channel:
        """Create a new gRPC channel."""
        options = channel_options or self._get_default_options()

        # I-3: use TLSConfig credentials when provided; fallback to system roots.
        if use_tls:
            if tls_config is not None and tls_config.enabled:
                credentials = tls_config.get_channel_credentials()
                # Merge any TLS channel options (e.g. ssl_target_name_override)
                extra_opts = tls_config.get_channel_options()
                if extra_opts:
                    options = list(options) + extra_opts
            else:
                credentials = grpc.ssl_channel_credentials()
            channel = grpc.aio.secure_channel(address, credentials, options=options)
        else:
            channel = grpc.aio.insecure_channel(address, options=options)

        # Wait for channel to be ready
        try:
            await asyncio.wait_for(channel.channel_ready(), timeout=self._config.channel_ready_timeout)
        except asyncio.TimeoutError:
            await channel.close()
            raise ConnectionError(f"Channel to {address} failed to become ready")

        return channel

    def _get_default_options(self) -> list[tuple[str, Any]]:
        """Get default channel options."""
        from ...config.constants import (
            get_keepalive_time_ms,
            get_keepalive_timeout_ms,
            get_max_send_message_length,
            get_max_receive_message_length,
        )

        return [
            ("grpc.keepalive_time_ms", get_keepalive_time_ms()),
            ("grpc.keepalive_timeout_ms", get_keepalive_timeout_ms()),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.max_send_message_length", get_max_send_message_length()),
            ("grpc.max_receive_message_length", get_max_receive_message_length()),
            ("grpc.enable_retries", 0),  # Handled by our retry layer
        ]

    @asynccontextmanager
    async def pooled_channel(
        self,
        address: str,
        use_tls: bool = False,
        channel_options: Optional[list] = None,
        tls_config=None,  # I-3: Optional[TLSConfig]
    ):
        """
        Context manager for pooled channel access.

        Automatically releases channel back to pool on exit.

        Args:
            address: Server address
            use_tls: Whether to use TLS
            channel_options: Optional channel options

        Yields:
            gRPC async channel
        """
        channel = await self.get_channel(address, use_tls, channel_options, tls_config=tls_config)
        try:
            yield channel
        finally:
            # Channel stays in pool, just mark as available
            await self._release_channel(address, use_tls, channel)

    async def _release_channel(
        self,
        address: str,
        use_tls: bool,
        channel: grpc.aio.Channel,
    ) -> None:
        """Release channel back to pool."""
        pool_key = self._make_key(address, use_tls)

        async with self._lock:
            if pool_key in self._channels:
                for entry in self._channels[pool_key]:
                    if entry.channel is channel:
                        entry.in_use = False
                        entry.last_used_at = time.time()
                        logger.debug(
                            f"Channel released: address={address}, use_count={entry.use_count}"
                        )
                        return

    def _ensure_cleanup_task(self) -> None:
        """Ensure cleanup and health-check tasks are running."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(
                self._cleanup_loop(), name="grpc-pool-cleanup"
            )
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(
                self._health_check_loop(), name="grpc-pool-health"
            )

    async def _cleanup_loop(self) -> None:
        """Background task to cleanup stale channels."""
        while not self._closed:
            await asyncio.sleep(self._config.cleanup_interval)
            await self._cleanup_stale()

    async def _health_check_loop(self) -> None:
        """Background task to evict channels in TRANSIENT_FAILURE or SHUTDOWN state.

        C-02: runs on health_check_interval (default 30 s), separate from the
        cleanup cycle (default 60 s) so unhealthy channels are evicted faster.
        """
        while not self._closed:
            await asyncio.sleep(self._config.health_check_interval)
            await self._evict_unhealthy()

    async def _evict_unhealthy(self) -> None:
        """Remove channels that are in TRANSIENT_FAILURE or SHUTDOWN state."""
        bad_states = {
            grpc.ChannelConnectivity.TRANSIENT_FAILURE,
            grpc.ChannelConnectivity.SHUTDOWN,
        }
        async with self._lock:
            total_evicted = 0
            for pool_key, entries in list(self._channels.items()):
                to_remove = [
                    e for e in entries
                    if not e.in_use and self._get_channel_state(e) in bad_states
                ]
                for entry in to_remove:
                    try:
                        await entry.channel.close()
                    except Exception as e:
                        logger.debug("Failed to close unhealthy channel: %s", e)
                    entries.remove(entry)
                    total_evicted += 1
                if not entries:
                    del self._channels[pool_key]
            if total_evicted > 0:
                logger.info("Health-check evicted %d unhealthy channel(s)", total_evicted)

    @staticmethod
    def _get_channel_state(entry: "ChannelEntry") -> "grpc.ChannelConnectivity":
        """Return channel connectivity state, SHUTDOWN on any error."""
        try:
            return entry.channel.get_state(try_to_connect=False)
        except Exception:
            return grpc.ChannelConnectivity.SHUTDOWN

    async def _cleanup_stale(self) -> None:
        """Remove stale channels from pool."""
        async with self._lock:
            total_removed = 0

            for pool_key, entries in list(self._channels.items()):
                to_remove = []

                for entry in entries:
                    # Don't remove channels in use
                    if entry.in_use:
                        continue

                    # I-5: always evict SHUTDOWN channels regardless of idle/age.
                    try:
                        state = entry.channel.get_state(try_to_connect=False)
                        if state == grpc.ChannelConnectivity.SHUTDOWN:
                            to_remove.append(entry)
                            continue
                    except Exception:
                        pass

                    # Check if stale
                    if entry.is_stale(
                        self._config.idle_timeout,
                        self._config.max_age,
                    ):
                        # Keep minimum idle channels
                        idle_count = sum(1 for e in entries if not e.in_use)
                        if idle_count > self._config.min_idle:
                            to_remove.append(entry)

                # Remove stale entries
                for entry in to_remove:
                    try:
                        await entry.channel.close()
                    except Exception as e:
                        logger.warning(f"Channel close error: {e}")
                    entries.remove(entry)
                    total_removed += 1

                # Remove empty pool keys
                if not entries:
                    del self._channels[pool_key]

            if total_removed > 0:
                logger.info(
                    f"Stale channels removed: count={total_removed}, "
                    f"remaining_pools={len(self._channels)}"
                )

    async def close_channel(self, address: str, use_tls: bool = False) -> None:
        """
        Close all channels for a specific address.

        Args:
            address: Server address
            use_tls: Whether TLS was used
        """
        pool_key = self._make_key(address, use_tls)

        async with self._lock:
            if pool_key in self._channels:
                entries = self._channels.pop(pool_key)
                for entry in entries:
                    try:
                        # I-4: grace period so in-flight RPCs can complete
                        await entry.channel.close(grace=_CLOSE_GRACE_SECONDS)
                    except Exception as e:
                        logger.warning(f"Channel close error: {e}")

                logger.info(f"Channels closed: address={address}, count={len(entries)}")

    async def close_all(self) -> None:
        """Close all channels and shutdown pool."""
        self._closed = True

        # Cancel cleanup and health-check tasks
        for task in (self._cleanup_task, self._health_check_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._cleanup_task = None
        self._health_check_task = None

        # Close all channels
        async with self._lock:
            total_closed = 0
            for _pool_key, entries in list(self._channels.items()):
                for entry in entries:
                    try:
                        # I-4: grace period so in-flight RPCs can complete
                        await entry.channel.close(grace=_CLOSE_GRACE_SECONDS)
                        total_closed += 1
                    except Exception as e:
                        logger.warning(f"Channel close error: {e}")
            self._channels.clear()

        logger.info(f"Channel pool closed: channels_closed={total_closed}")

    def get_stats(self) -> dict:
        """
        Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        stats = {
            "total_channels": 0,
            "channels_in_use": 0,
            "channels_idle": 0,
            "pools": {},
        }

        for pool_key, entries in self._channels.items():
            in_use = sum(1 for e in entries if e.in_use)
            idle = len(entries) - in_use

            stats["total_channels"] += len(entries)
            stats["channels_in_use"] += in_use
            stats["channels_idle"] += idle
            stats["pools"][pool_key] = {
                "total": len(entries),
                "in_use": in_use,
                "idle": idle,
            }

        return stats

    @property
    def size(self) -> int:
        """Get total number of channels in pool."""
        return sum(len(entries) for entries in self._channels.values())

    @property
    def is_closed(self) -> bool:
        """Check if pool is closed."""
        return self._closed


# =============================================================================
# Sync Channel Pool (for sync clients)
# =============================================================================


class SyncChannelEntry(NamedTuple):
    """Entry in the sync channel pool."""

    channel: grpc.Channel
    last_used: float
    use_count: int


class SyncGRPCChannelPool:
    """
    Synchronous gRPC channel pool.

    Similar to GRPCChannelPool but for sync grpc.Channel.
    """

    def __init__(self, config: Optional[GrpcPoolConfig] = None):
        """Initialize sync channel pool."""
        self._config = config or _get_pool_config()
        self._channels: dict[str, list[SyncChannelEntry]] = {}
        # A-06 fix: removed asyncio.Lock() — it is not usable from sync code
        # and raised a DeprecationWarning in Python 3.10+ when created outside
        # a running event loop. SyncGRPCChannelPool is fully sync; only
        # _thread_lock is needed.
        import threading
        self._thread_lock = threading.Lock()

        logger.info("Sync channel pool initialized")

    def get_channel(
        self,
        address: str,
        use_tls: bool = False,
        channel_options: Optional[list] = None,
    ) -> grpc.Channel:
        """Get or create a sync channel."""
        pool_key = f"{address}:{'tls' if use_tls else 'plain'}"

        with self._thread_lock:
            # Try to get existing channel
            if pool_key in self._channels:
                for i, (channel, last_used, count) in enumerate(self._channels[pool_key]):
                    # Check if not stale
                    if time.time() - last_used < self._config.idle_timeout:
                        self._channels[pool_key][i] = SyncChannelEntry(channel, time.time(), count + 1)
                        logger.debug(f"Sync channel reused: address={address}")
                        return channel

            # Create new channel
            options = channel_options or self._get_default_options()

            if use_tls:
                credentials = grpc.ssl_channel_credentials()
                channel = grpc.secure_channel(address, credentials, options=options)
            else:
                channel = grpc.insecure_channel(address, options=options)

            # Wait for ready
            grpc.channel_ready_future(channel).result(timeout=self._config.channel_ready_timeout)

            # Add to pool
            if pool_key not in self._channels:
                self._channels[pool_key] = []
            self._channels[pool_key].append(SyncChannelEntry(channel, time.time(), 1))

            logger.debug(f"Sync channel created: address={address}")
            return channel

    def _get_default_options(self) -> list[tuple[str, Any]]:
        """Get default channel options."""
        from ...config.constants import (
            get_keepalive_time_ms,
            get_keepalive_timeout_ms,
        )

        return [
            ("grpc.keepalive_time_ms", get_keepalive_time_ms()),
            ("grpc.keepalive_timeout_ms", get_keepalive_timeout_ms()),
            ("grpc.keepalive_permit_without_calls", 1),
        ]

    def close_all(self) -> None:
        """Close all channels."""
        with self._thread_lock:
            for pool_key, entries in self._channels.items():
                for channel, _, _ in entries:
                    try:
                        channel.close()
                    except Exception as e:
                        logger.debug("Failed to close sync channel: %s", e)
            self._channels.clear()
            logger.info("Sync channel pool closed")


# =============================================================================
# Global Pool Singleton
# =============================================================================

_global_pool: Optional[GRPCChannelPool] = None
_global_sync_pool: Optional[SyncGRPCChannelPool] = None


def get_channel_pool(config: Optional[GrpcPoolConfig] = None) -> GRPCChannelPool:
    """
    Get global async channel pool.

    Args:
        config: Pool configuration (only used on first call)

    Returns:
        Global GRPCChannelPool instance
    """
    global _global_pool

    if _global_pool is None or _global_pool.is_closed:
        _global_pool = GRPCChannelPool(config)

    return _global_pool


def get_sync_channel_pool(config: Optional[GrpcPoolConfig] = None) -> SyncGRPCChannelPool:
    """
    Get global sync channel pool.

    Args:
        config: Pool configuration (only used on first call)

    Returns:
        Global SyncGRPCChannelPool instance
    """
    global _global_sync_pool

    if _global_sync_pool is None:
        _global_sync_pool = SyncGRPCChannelPool(config)

    return _global_sync_pool


async def close_global_pool() -> None:
    """Close global async pool."""
    global _global_pool

    if _global_pool is not None:
        await _global_pool.close_all()
        _global_pool = None


def close_global_sync_pool() -> None:
    """Close global sync pool."""
    global _global_sync_pool

    if _global_sync_pool is not None:
        _global_sync_pool.close_all()
        _global_sync_pool = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PoolConfig",
    "ChannelEntry",
    "GRPCChannelPool",
    "SyncGRPCChannelPool",
    "get_channel_pool",
    "get_sync_channel_pool",
    "close_global_pool",
    "close_global_sync_pool",
]
