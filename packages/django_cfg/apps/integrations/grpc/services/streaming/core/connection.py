"""
Connection management for bidirectional streaming.

Manages active client connections, queues, and metadata.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components (Refactored)
"""

import asyncio
import time
import logging
from typing import Dict, Optional, List
from ..types import ConnectionInfo

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
logger = logging.getLogger("grpc_streaming.connection")


class ConnectionManager:
    """
    Manages active client connections.

    Responsibilities:
    - Store active connections with queues
    - Track connection metadata
    - Provide connection lookup and status

    Thread-safe for asyncio single event loop.
    """

    def __init__(self):
        """Initialize empty connection registry."""
        self._connections: Dict[str, ConnectionInfo] = {}

    def register(
        self,
        client_id: str,
        output_queue: asyncio.Queue,
        metadata: Optional[dict] = None
    ) -> ConnectionInfo:
        """
        Register new client connection.

        Args:
            client_id: Client UUID
            output_queue: Queue for outgoing commands
            metadata: Optional metadata (version, hostname, etc)

        Returns:
            ConnectionInfo object

        Raises:
            ValueError: If client already registered
        """
        if client_id in self._connections:
            logger.warning(
                f"⚠️  Client {client_id[:8]}... already registered, replacing"
            )

        conn_info = ConnectionInfo(
            client_id=client_id,
            output_queue=output_queue,
            connected_at=time.time(),
            metadata=metadata
        )

        self._connections[client_id] = conn_info

        logger.info(
            f"✅ Registered connection: {client_id[:8]}... "
            f"(total={len(self._connections)})"
        )

        return conn_info

    def unregister(self, client_id: str) -> bool:
        """
        Unregister client connection.

        Args:
            client_id: Client UUID

        Returns:
            True if connection existed and was removed
        """
        if client_id in self._connections:
            del self._connections[client_id]
            logger.info(
                f"❌ Unregistered connection: {client_id[:8]}... "
                f"(remaining={len(self._connections)})"
            )
            return True

        logger.warning(
            f"⚠️  Attempted to unregister unknown client: {client_id[:8]}..."
        )
        return False

    def get(self, client_id: str) -> Optional[ConnectionInfo]:
        """
        Get connection info.

        Args:
            client_id: Client UUID

        Returns:
            ConnectionInfo or None if not found
        """
        return self._connections.get(client_id)

    def is_connected(self, client_id: str) -> bool:
        """
        Check if client is connected.

        Args:
            client_id: Client UUID

        Returns:
            True if connected
        """
        return client_id in self._connections

    def get_all(self) -> Dict[str, ConnectionInfo]:
        """
        Get all active connections.

        Returns:
            Dictionary of client_id -> ConnectionInfo
        """
        return dict(self._connections)

    def get_client_ids(self) -> List[str]:
        """
        Get list of all connected client IDs.

        Returns:
            List of client UUIDs
        """
        return list(self._connections.keys())

    def count(self) -> int:
        """
        Get count of active connections.

        Returns:
            Number of active connections
        """
        return len(self._connections)

    def update_activity(self, client_id: str) -> None:
        """
        Update last activity timestamp for client.

        Args:
            client_id: Client UUID
        """
        conn = self._connections.get(client_id)
        if conn:
            conn.update_activity(time.time())

    def get_stats(self) -> dict:
        """
        Get connection statistics.

        Returns:
            Dictionary with stats
        """
        total = len(self._connections)
        if total == 0:
            return {
                'total_connections': 0,
                'active_connections': 0,
            }

        now = time.time()
        active_5min = sum(
            1 for conn in self._connections.values()
            if conn.last_message_at and (now - conn.last_message_at) < 300
        )

        return {
            'total_connections': total,
            'active_connections': active_5min,
            'clients': [
                conn.to_dict()
                for conn in self._connections.values()
            ]
        }


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'ConnectionManager',
]
