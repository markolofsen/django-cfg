"""
WebSocket Connection Manager.

Manages active WebSocket connections with presence tracking and room support.

File size: ~500 lines
"""

import asyncio
import warnings
from typing import Dict, Set, Optional, List, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4
import websockets
from websockets.server import WebSocketServerProtocol
from pydantic import BaseModel, Field, field_validator
from loguru import logger
import redis.asyncio as aioredis

# Import config types (avoiding circular imports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config.models import RPCServerConfig
    from ..config.environment import Environment


class ActiveConnection(BaseModel):
    """
    Information about an active WebSocket connection.

    Tracks in-memory connection state with WebSocket object.
    This is different from models.ActiveConnection which is for RPC serialization.

    Example:
        >>> conn = ActiveConnection(
        ...     connection_id=uuid4(),
        ...     user_id="123",
        ...     websocket=ws,
        ...     authenticated=True,
        ... )
    """

    connection_id: UUID = Field(
        default_factory=uuid4,
        description="Unique connection identifier",
    )

    user_id: Optional[str] = Field(
        default=None,
        description="Authenticated user ID (None if not authenticated)",
    )

    websocket: Any = Field(
        description="WebSocket connection object (WebSocketServerProtocol or mock)",
    )

    @field_validator("websocket")
    @classmethod
    def validate_websocket(cls, v: Any) -> Any:
        """
        Validate websocket has required methods.

        Allows both real WebSocketServerProtocol and mocks for testing.
        Also allows None for RPC bridge fake connections.
        """
        # Allow None for RPC bridge
        if v is None:
            return v

        # Check for required methods (duck typing)
        required_methods = ["send", "recv", "close"]
        for method in required_methods:
            if not hasattr(v, method):
                raise ValueError(f"WebSocket must have '{method}' method")
        return v

    authenticated: bool = Field(
        default=False,
        description="Authentication status",
    )

    connected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Connection timestamp",
    )

    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last activity timestamp",
    )

    rooms: Set[str] = Field(
        default_factory=set,
        description="Rooms this connection is subscribed to",
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom metadata (user agent, IP, etc.)",
    )

    model_config = {
        "arbitrary_types_allowed": True,  # Allow WebSocketServerProtocol
    }

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)

    def join_room(self, room: str) -> None:
        """
        Join a room.

        Args:
            room: Room name to join
        """
        self.rooms.add(room)
        self.update_activity()

    def leave_room(self, room: str) -> None:
        """
        Leave a room.

        Args:
            room: Room name to leave
        """
        self.rooms.discard(room)
        self.update_activity()


class ConnectionStats(BaseModel):
    """Connection statistics."""

    total_connections: int = Field(
        description="Total active connections",
    )

    authenticated_connections: int = Field(
        description="Authenticated connections",
    )

    unique_users: int = Field(
        description="Number of unique users",
    )

    rooms: Dict[str, int] = Field(
        default_factory=dict,
        description="Room membership counts",
    )


class ConnectionManager:
    """
    Manages all active WebSocket connections.

    Features:
        - Connection lifecycle management
        - Multi-connection per user support
        - Room/channel subscriptions
        - Presence tracking with Redis
        - Connection statistics

    Example:
        >>> manager = ConnectionManager(redis_url="redis://localhost:6379/2")
        >>> await manager.initialize()
        >>>
        >>> # Add connection
        >>> conn_info = await manager.add_connection(websocket, user_id="123")
        >>>
        >>> # Join room
        >>> await manager.join_room(conn_info.connection_id, "notifications")
        >>>
        >>> # Send to user
        >>> await manager.send_to_user("123", {"type": "notification", "data": ...})
        >>>
        >>> # Remove connection
        >>> await manager.remove_connection(conn_info.connection_id)
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        config: Optional["RPCServerConfig"] = None,
        environment: Optional["Environment"] = None,
        presence_ttl: int = 300,
    ):
        """
        Initialize connection manager.

        Args:
            redis_url: Redis connection URL (deprecated, use config instead)
            config: RPC server configuration with multi-environment support
            environment: Override environment detection (optional)
            presence_ttl: Presence timeout in seconds (default: 300)

        Raises:
            ValueError: If neither redis_url nor config is provided

        Example (new way):
            >>> from django_ipc.config import RPCServerConfig, RPCEndpointConfig
            >>> config = RPCServerConfig(
            ...     development=RPCEndpointConfig(
            ...         websocket_url="ws://localhost:8001/ws",
            ...         redis_url="redis://localhost:6379/2",
            ...     ),
            ...     production=RPCEndpointConfig(
            ...         websocket_url="wss://api.example.com/ws",
            ...         redis_url="redis://prod-redis:6379/0",
            ...     ),
            ... )
            >>> manager = ConnectionManager(config=config)

        Example (old way, still supported):
            >>> manager = ConnectionManager(redis_url="redis://localhost:6379/2")
        """
        # Validate inputs
        if redis_url and config:
            raise ValueError(
                "Cannot specify both 'redis_url' and 'config'. "
                "Please use 'config' (recommended) or 'redis_url' (deprecated)."
            )

        if not redis_url and not config:
            raise ValueError(
                "Must provide either 'redis_url' or 'config'. "
                "Using 'config' with RPCServerConfig is recommended."
            )

        # Handle old way (backward compatibility)
        if redis_url:
            warnings.warn(
                "Passing 'redis_url' directly is deprecated and will be removed in v2.0. "
                "Please use RPCServerConfig instead. See documentation for examples.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.redis_url = redis_url
            self.config = None
            self.environment = environment or "development"
            logger.warning(
                "Using deprecated redis_url parameter. "
                "Consider migrating to RPCServerConfig for multi-environment support."
            )

        # Handle new way (recommended)
        elif config:
            self.config = config

            # Detect or use provided environment
            if environment:
                self.environment = environment
            else:
                from ..config.environment import detect_environment
                self.environment = detect_environment()

            # Get endpoint for current environment
            try:
                endpoint = config.get_endpoint(self.environment)
                self.redis_url = endpoint.redis_url
                logger.info(
                    f"ConnectionManager initialized for environment: {self.environment} "
                    f"(Redis: {self.redis_url})"
                )
            except ValueError as e:
                logger.error(f"Failed to get endpoint for environment '{self.environment}': {e}")
                raise

        self.presence_ttl = presence_ttl

        # In-memory connection storage
        self._connections: Dict[UUID, ActiveConnection] = {}

        # Index: user_id -> set of connection_ids
        self._user_connections: Dict[str, Set[UUID]] = {}

        # Index: room -> set of connection_ids
        self._room_connections: Dict[str, Set[UUID]] = {}

        # Redis client for distributed presence
        self._redis: Optional[aioredis.Redis] = None

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Initialize connection manager and Redis.

        Raises:
            Exception: If Redis connection fails
        """
        try:
            self._redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info(f"Connection manager initialized with Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown connection manager and close all connections."""
        async with self._lock:
            # Close all WebSocket connections
            for conn_info in list(self._connections.values()):
                try:
                    await conn_info.websocket.close()
                except Exception as e:
                    logger.warning(f"Error closing connection {conn_info.connection_id}: {e}")

            # Clear in-memory state
            self._connections.clear()
            self._user_connections.clear()
            self._room_connections.clear()

            # Close Redis connection
            if self._redis:
                await self._redis.close()

            logger.info("Connection manager shutdown complete")

    async def add_connection(
        self,
        websocket: WebSocketServerProtocol,
        user_id: Optional[str] = None,
        authenticated: bool = False,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ActiveConnection:
        """
        Add new WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: Authenticated user ID (optional)
            authenticated: Authentication status
            metadata: Connection metadata

        Returns:
            ActiveConnection object
        """
        async with self._lock:
            conn_info = ActiveConnection(
                websocket=websocket,
                user_id=user_id,
                authenticated=authenticated,
                metadata=metadata or {},
            )

            # Store connection
            self._connections[conn_info.connection_id] = conn_info

            # Index by user_id
            if user_id:
                if user_id not in self._user_connections:
                    self._user_connections[user_id] = set()
                self._user_connections[user_id].add(conn_info.connection_id)

                # Update Redis presence
                await self._update_presence(user_id, online=True)

            logger.info(
                f"Connection added: {conn_info.connection_id} "
                f"(user: {user_id}, total: {len(self._connections)})"
            )

            return conn_info

    async def remove_connection(self, connection_id: UUID) -> bool:
        """
        Remove WebSocket connection.

        Args:
            connection_id: Connection ID to remove

        Returns:
            True if removed, False if not found
        """
        async with self._lock:
            conn_info = self._connections.get(connection_id)
            if not conn_info:
                return False

            # Remove from user index
            if conn_info.user_id:
                user_conns = self._user_connections.get(conn_info.user_id, set())
                user_conns.discard(connection_id)

                # If no more connections for this user, update presence
                if not user_conns:
                    del self._user_connections[conn_info.user_id]
                    await self._update_presence(conn_info.user_id, online=False)

            # Remove from all rooms
            for room in conn_info.rooms:
                room_conns = self._room_connections.get(room, set())
                room_conns.discard(connection_id)
                if not room_conns:
                    del self._room_connections[room]

            # Remove connection
            del self._connections[connection_id]

            logger.info(
                f"Connection removed: {connection_id} "
                f"(user: {conn_info.user_id}, total: {len(self._connections)})"
            )

            return True

    async def get_connection(self, connection_id: UUID) -> Optional[ActiveConnection]:
        """
        Get connection by ID.

        Args:
            connection_id: Connection ID

        Returns:
            ActiveConnection or None if not found
        """
        return self._connections.get(connection_id)

    async def get_user_connections(self, user_id: str) -> List[ActiveConnection]:
        """
        Get all connections for a user.

        Args:
            user_id: User ID

        Returns:
            List of ActiveConnection objects
        """
        connection_ids = self._user_connections.get(user_id, set())
        return [
            self._connections[conn_id]
            for conn_id in connection_ids
            if conn_id in self._connections
        ]

    async def get_room_connections(self, room: str) -> List[ActiveConnection]:
        """
        Get all connections in a room.

        Args:
            room: Room name

        Returns:
            List of ActiveConnection objects
        """
        connection_ids = self._room_connections.get(room, set())
        return [
            self._connections[conn_id]
            for conn_id in connection_ids
            if conn_id in self._connections
        ]

    async def join_room(self, connection_id: UUID, room: str) -> bool:
        """
        Add connection to room.

        Args:
            connection_id: Connection ID
            room: Room name

        Returns:
            True if joined, False if connection not found
        """
        async with self._lock:
            conn_info = self._connections.get(connection_id)
            if not conn_info:
                return False

            # Add to connection's rooms
            conn_info.join_room(room)

            # Add to room index
            if room not in self._room_connections:
                self._room_connections[room] = set()
            self._room_connections[room].add(connection_id)

            logger.debug(f"Connection {connection_id} joined room: {room}")
            return True

    async def leave_room(self, connection_id: UUID, room: str) -> bool:
        """
        Remove connection from room.

        Args:
            connection_id: Connection ID
            room: Room name

        Returns:
            True if left, False if connection not found
        """
        async with self._lock:
            conn_info = self._connections.get(connection_id)
            if not conn_info:
                return False

            # Remove from connection's rooms
            conn_info.leave_room(room)

            # Remove from room index
            if room in self._room_connections:
                self._room_connections[room].discard(connection_id)
                if not self._room_connections[room]:
                    del self._room_connections[room]

            logger.debug(f"Connection {connection_id} left room: {room}")
            return True

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """
        Send message to all user connections.

        Args:
            user_id: User ID
            message: Message dict to send

        Returns:
            Number of connections message was sent to
        """
        connections = await self.get_user_connections(user_id)
        sent_count = 0

        for conn_info in connections:
            try:
                await conn_info.websocket.send(str(message))
                conn_info.update_activity()
                sent_count += 1
            except Exception as e:
                logger.warning(
                    f"Failed to send to connection {conn_info.connection_id}: {e}"
                )

        return sent_count

    async def send_to_room(self, room: str, message: dict) -> int:
        """
        Send message to all connections in room.

        Args:
            room: Room name
            message: Message dict to send

        Returns:
            Number of connections message was sent to
        """
        connections = await self.get_room_connections(room)
        sent_count = 0

        for conn_info in connections:
            try:
                await conn_info.websocket.send(str(message))
                conn_info.update_activity()
                sent_count += 1
            except Exception as e:
                logger.warning(
                    f"Failed to send to connection {conn_info.connection_id}: {e}"
                )

        return sent_count

    async def broadcast(self, message: dict, exclude: Optional[Set[UUID]] = None) -> int:
        """
        Broadcast message to all connections.

        Args:
            message: Message dict to send
            exclude: Set of connection IDs to exclude

        Returns:
            Number of connections message was sent to
        """
        exclude = exclude or set()
        sent_count = 0

        for conn_id, conn_info in self._connections.items():
            if conn_id in exclude:
                continue

            try:
                await conn_info.websocket.send(str(message))
                conn_info.update_activity()
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to connection {conn_id}: {e}")

        return sent_count

    async def is_user_online(self, user_id: str) -> bool:
        """
        Check if user is online (has active connections).

        Args:
            user_id: User ID

        Returns:
            True if user has connections
        """
        return user_id in self._user_connections

    async def get_stats(self) -> ConnectionStats:
        """
        Get connection statistics.

        Returns:
            ConnectionStats object
        """
        room_counts = {
            room: len(conns)
            for room, conns in self._room_connections.items()
        }

        return ConnectionStats(
            total_connections=len(self._connections),
            authenticated_connections=sum(
                1 for c in self._connections.values() if c.authenticated
            ),
            unique_users=len(self._user_connections),
            rooms=room_counts,
        )

    async def _update_presence(self, user_id: str, online: bool) -> None:
        """
        Update user presence in Redis.

        Args:
            user_id: User ID
            online: Online status
        """
        if not self._redis:
            return

        key = f"presence:{user_id}"

        try:
            if online:
                await self._redis.setex(key, self.presence_ttl, "online")
            else:
                await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Failed to update presence for {user_id}: {e}")


__all__ = [
    "ActiveConnection",
    "ConnectionStats",
    "ConnectionManager",
]
