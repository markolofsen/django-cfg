"""
Manager for GrpcAgentConnectionEvent model.

Provides:
- Log connection/disconnection/error events
- Query timeline for machine

Created: 2025-12-28
Refactored: 2025-12-29
"""

from datetime import timedelta
from typing import Any, Dict, List

from django.db import models
from django.utils import timezone


class GrpcAgentConnectionEventManager(models.Manager):
    """Manager for GrpcAgentConnectionEvent model."""

    # =========================================================================
    # Event logging
    # =========================================================================

    def log_connection(
        self,
        connection_state,
        ip_address: str = None,
        client_version: str = None,
    ):
        """
        Log a connection event.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            ip_address: Client IP address
            client_version: Client version string

        Returns:
            Created event
        """
        return self.create(
            connection_state=connection_state,
            event_type="connected",
            ip_address=ip_address,
            client_version=client_version or "",
        )

    def log_disconnection(
        self,
        connection_state,
        duration_seconds: int = None,
    ):
        """
        Log a disconnection event.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            duration_seconds: How long the connection was active

        Returns:
            Created event
        """
        return self.create(
            connection_state=connection_state,
            event_type="disconnected",
            duration_seconds=duration_seconds,
        )

    def log_error(
        self,
        connection_state,
        error_message: str,
        error_code: str = "",
        error_details: dict = None,
    ):
        """
        Log an error event.

        Args:
            connection_state: Parent GrpcAgentConnectionState
            error_message: Error message
            error_code: Error code (e.g., gRPC status code name)
            error_details: Additional details as dict

        Returns:
            Created event
        """
        return self.create(
            connection_state=connection_state,
            event_type="error",
            error_message=error_message,
            error_code=error_code,
            error_details=error_details,
        )

    # =========================================================================
    # Async event logging
    # =========================================================================

    async def alog_connection(
        self,
        connection_state,
        ip_address: str = None,
        client_version: str = None,
    ):
        """Log a connection event (ASYNC)."""
        return await self.acreate(
            connection_state=connection_state,
            event_type="connected",
            ip_address=ip_address,
            client_version=client_version or "",
        )

    async def alog_disconnection(
        self,
        connection_state,
        duration_seconds: int = None,
    ):
        """Log a disconnection event (ASYNC)."""
        return await self.acreate(
            connection_state=connection_state,
            event_type="disconnected",
            duration_seconds=duration_seconds,
        )

    async def alog_error(
        self,
        connection_state,
        error_message: str,
        error_code: str = "",
        error_details: dict = None,
    ):
        """Log an error event (ASYNC)."""
        return await self.acreate(
            connection_state=connection_state,
            event_type="error",
            error_message=error_message,
            error_code=error_code,
            error_details=error_details,
        )

    # =========================================================================
    # Queries
    # =========================================================================

    def get_timeline(
        self,
        machine_id: str,
        hours: int = 24,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get event timeline for a machine.

        Args:
            machine_id: Machine identifier
            hours: Hours to look back
            limit: Maximum events to return

        Returns:
            List of event dictionaries
        """
        threshold = timezone.now() - timedelta(hours=hours)

        events = self.filter(
            connection_state__machine_id=machine_id,
            timestamp__gte=threshold,
        ).order_by("-timestamp")[:limit]

        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "error_message": e.error_message or None,
                "duration_seconds": e.duration_seconds,
            }
            for e in events
        ]

    async def aget_timeline(
        self,
        machine_id: str,
        hours: int = 24,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get event timeline for a machine (ASYNC)."""
        threshold = timezone.now() - timedelta(hours=hours)

        events = self.filter(
            connection_state__machine_id=machine_id,
            timestamp__gte=threshold,
        ).order_by("-timestamp")[:limit]

        result = []
        async for e in events:
            result.append({
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "error_message": e.error_message or None,
                "duration_seconds": e.duration_seconds,
            })
        return result

    def for_machine(self, machine_id: str):
        """Filter events for a specific machine."""
        return self.filter(connection_state__machine_id=machine_id)

    def recent(self, hours: int = 24):
        """Filter recent events."""
        threshold = timezone.now() - timedelta(hours=hours)
        return self.filter(timestamp__gte=threshold)

    def errors_only(self):
        """Filter error events only."""
        return self.filter(event_type="error")

    def connections_only(self):
        """Filter connection events only."""
        return self.filter(event_type="connected")

    def disconnections_only(self):
        """Filter disconnection events only."""
        return self.filter(event_type="disconnected")
