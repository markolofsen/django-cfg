"""
Connection Models for WebSocket RPC.

Pydantic 2 models for tracking WebSocket connections and their state.
Used for connection management and user presence tracking.

File size: ~200 lines
"""

from pydantic import BaseModel, Field, ConfigDict, IPvAnyAddress, field_validator
from datetime import datetime, timezone, timedelta
from typing import Optional, Any
from uuid import UUID, uuid4


class ConnectionInfo(BaseModel):
    """
    WebSocket connection information.

    Complete connection state including user, server, and metadata.

    Example:
        >>> from ipaddress import IPv4Address
        >>> connection = ConnectionInfo(
        ...     connection_id=uuid4(),
        ...     user_id="user_123",
        ...     server_id="ws_server_1",
        ...     ip_address=IPv4Address("192.168.1.100"),
        ...     user_agent="Mozilla/5.0...",
        ...     metadata={"device": "mobile", "app_version": "2.1.0"}
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    connection_id: UUID = Field(
        default_factory=uuid4,
        description="Unique connection identifier",
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Authenticated user ID",
    )

    server_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="WebSocket server instance ID",
        examples=["ws_server_1", "ws_server_2"],
    )

    ip_address: IPvAnyAddress = Field(
        ...,
        description="Client IP address (IPv4 or IPv6)",
    )

    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Client user agent string",
    )

    connected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Connection established timestamp (UTC)",
    )

    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last activity timestamp (UTC)",
    )

    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional connection metadata",
    )

    def is_active(self, timeout_seconds: int = 300) -> bool:
        """
        Check if connection is still active based on last activity.

        Args:
            timeout_seconds: Activity timeout threshold (default: 5 minutes)

        Returns:
            True if connection is active, False otherwise

        Example:
            >>> connection = ConnectionInfo(...)
            >>> if connection.is_active(timeout_seconds=300):
            ...     print("Connection is active")
        """
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed < timeout_seconds

    def update_activity(self) -> None:
        """
        Update last activity timestamp to current time.

        Example:
            >>> connection.update_activity()
            >>> print(connection.last_activity)  # Now
        """
        self.last_activity = datetime.now(timezone.utc)

    def get_connection_duration(self) -> timedelta:
        """
        Get total connection duration.

        Returns:
            Duration since connection established

        Example:
            >>> duration = connection.get_connection_duration()
            >>> print(f"Connected for {duration.total_seconds()} seconds")
        """
        return datetime.now(timezone.utc) - self.connected_at


class ConnectionStateUpdate(BaseModel):
    """
    Update for connection state.

    Used to update specific fields of connection without replacing entire object.

    Example:
        >>> update = ConnectionStateUpdate(
        ...     connection_id=connection.connection_id,
        ...     last_activity=datetime.now(timezone.utc),
        ...     metadata={"status": "typing", "in_room": "room_123"}
        ... )
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    connection_id: UUID = Field(
        ...,
        description="Connection to update",
    )

    last_activity: Optional[datetime] = Field(
        default=None,
        description="Updated last activity timestamp",
    )

    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Updated metadata (merged with existing)",
    )

    @field_validator("last_activity")
    @classmethod
    def validate_last_activity(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure last_activity is not in the future."""
        if v is not None and v > datetime.now(timezone.utc):
            raise ValueError("last_activity cannot be in the future")
        return v


class ConnectionListResponse(BaseModel):
    """
    Response with list of connections.

    Used for admin/monitoring endpoints.

    Example:
        >>> response = ConnectionListResponse(
        ...     total=150,
        ...     active=145,
        ...     connections=[connection1, connection2, ...]
        ... )
    """

    model_config = ConfigDict(validate_assignment=True)

    total: int = Field(
        ...,
        ge=0,
        description="Total connections",
    )

    active: int = Field(
        ...,
        ge=0,
        description="Active connections (recent activity)",
    )

    connections: list[ConnectionInfo] = Field(
        ...,
        description="List of connection details",
    )

    def get_connections_by_user(self, user_id: str) -> list[ConnectionInfo]:
        """
        Filter connections by user ID.

        Args:
            user_id: User ID to filter by

        Returns:
            List of connections for the user

        Example:
            >>> user_connections = response.get_connections_by_user("user_123")
        """
        return [conn for conn in self.connections if conn.user_id == user_id]

    def get_connections_by_server(self, server_id: str) -> list[ConnectionInfo]:
        """
        Filter connections by server ID.

        Args:
            server_id: Server ID to filter by

        Returns:
            List of connections on the server

        Example:
            >>> server_connections = response.get_connections_by_server("ws_server_1")
        """
        return [conn for conn in self.connections if conn.server_id == server_id]


__all__ = [
    "ConnectionInfo",
    "ConnectionStateUpdate",
    "ConnectionListResponse",
]
