"""
Manager for GrpcAgentConnectionState model.

Provides:
- Custom QuerySet with filtering methods
- Async methods with row-level locking (CRITICAL-02 FIX)
- Dashboard statistics

Created: 2025-12-28
Refactored: 2025-12-29
"""

from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from django.db import models
from django.db.models import Q
from django.utils import timezone


class GrpcAgentConnectionStateQuerySet(models.QuerySet):
    """Custom QuerySet for connection state with filtering methods."""

    def connected(self):
        """Filter connected machines."""
        return self.filter(status="connected")

    def disconnected(self):
        """Filter disconnected machines."""
        return self.filter(status="disconnected")

    def with_errors(self):
        """Filter machines with errors."""
        return self.filter(status="error")

    def healthy(self):
        """Filter healthy connections (connected with good metrics)."""
        return self.filter(
            status="connected",
            consecutive_error_count=0,
        ).filter(
            Q(current_rtt_ms__isnull=True) | Q(current_rtt_ms__lt=1000)
        ).filter(
            Q(current_packet_loss_percent__isnull=True) | Q(current_packet_loss_percent__lt=5)
        )

    def recent(self, hours: int = 24):
        """Filter machines active in last X hours."""
        threshold = timezone.now() - timedelta(hours=hours)
        return self.filter(last_connected_at__gte=threshold)


class GrpcAgentConnectionStateManager(models.Manager):
    """Manager for GrpcAgentConnectionState model."""

    def get_queryset(self):
        return GrpcAgentConnectionStateQuerySet(self.model, using=self._db)

    # =========================================================================
    # QuerySet proxy methods
    # =========================================================================

    def connected(self):
        return self.get_queryset().connected()

    def disconnected(self):
        return self.get_queryset().disconnected()

    def with_errors(self):
        return self.get_queryset().with_errors()

    def healthy(self):
        return self.get_queryset().healthy()

    def recent(self, hours: int = 24):
        return self.get_queryset().recent(hours=hours)

    # =========================================================================
    # CRUD methods
    # =========================================================================

    def get_or_create_for_machine(
        self,
        machine_id: str,
        machine_name: str,
    ) -> Tuple[Any, bool]:
        """
        Get or create connection state for a machine.

        Args:
            machine_id: Unique machine identifier
            machine_name: Human-readable machine name

        Returns:
            Tuple of (connection_state, created)
        """
        return self.get_or_create(
            machine_id=machine_id,
            defaults={
                "machine_name": machine_name,
            }
        )

    # =========================================================================
    # ASYNC METHODS WITH ROW-LEVEL LOCKING (CRITICAL-02 FIX)
    # =========================================================================
    # These methods use select_for_update() to prevent race conditions when
    # multiple concurrent operations try to update the connection state.
    #
    # Two API styles:
    # 1. By PK (for instance methods): amark_connected_safe(pk=...), etc.
    # 2. By machine_id (for direct calls): amark_connected_by_machine_id(...), etc.
    # =========================================================================

    async def aget_or_create_for_machine(
        self,
        machine_id: str,
        machine_name: str,
    ) -> Tuple[Any, bool]:
        """Get or create connection state for a machine (ASYNC)."""
        return await self.aget_or_create(
            machine_id=machine_id,
            defaults={
                "machine_name": machine_name,
            }
        )

    async def amark_connected_safe(
        self,
        pk,
        ip_address: str = None,
        client_version: str = None,
    ) -> Optional[Any]:
        """
        Mark machine as connected with row-level locking by PK (ASYNC).

        Args:
            pk: Primary key of the record
            ip_address: Client IP address
            client_version: Client version string

        Returns:
            Updated connection_state or None if not found
        """
        from django.db import transaction

        async with transaction.atomic():
            locked = await (
                self.select_for_update()
                .filter(pk=pk)
                .afirst()
            )

            if locked is None:
                return None

            locked.status = self.model.ConnectionStatus.CONNECTED
            locked.last_connected_at = timezone.now()
            locked.consecutive_error_count = 0
            if ip_address:
                locked.last_known_ip = ip_address
            if client_version:
                locked.client_version = client_version

            await locked.asave(update_fields=[
                "status", "last_connected_at", "consecutive_error_count",
                "last_known_ip", "client_version", "updated_at",
            ])

            return locked

    async def amark_disconnected_safe(self, pk) -> Optional[Any]:
        """Mark machine as disconnected with row-level locking by PK (ASYNC)."""
        from django.db import transaction

        async with transaction.atomic():
            locked = await (
                self.select_for_update()
                .filter(pk=pk)
                .afirst()
            )

            if locked is None:
                return None

            locked.status = self.model.ConnectionStatus.DISCONNECTED
            locked.last_disconnected_at = timezone.now()

            await locked.asave(update_fields=[
                "status", "last_disconnected_at", "updated_at",
            ])

            return locked

    async def amark_error_safe(self, pk, error_message: str) -> Optional[Any]:
        """Mark machine as having an error with row-level locking by PK (ASYNC)."""
        from django.db import transaction

        async with transaction.atomic():
            locked = await (
                self.select_for_update()
                .filter(pk=pk)
                .afirst()
            )

            if locked is None:
                return None

            locked.status = self.model.ConnectionStatus.ERROR
            locked.last_error_message = error_message
            locked.last_error_at = timezone.now()
            locked.consecutive_error_count += 1

            await locked.asave(update_fields=[
                "status", "last_error_message", "last_error_at",
                "consecutive_error_count", "updated_at",
            ])

            return locked

    async def aupdate_status_safe(
        self,
        machine_id: str,
        new_status: str,
        ip_address: str = None,
        client_version: str = None,
        error_message: str = None,
    ) -> Tuple[Any, bool]:
        """
        Atomically update connection status with row-level locking.

        Args:
            machine_id: Unique machine identifier
            new_status: New status to set ("connected", "disconnected", "error")
            ip_address: Client IP address (for connected status)
            client_version: Client version string (for connected status)
            error_message: Error message (for error status)

        Returns:
            Tuple of (connection_state, updated)
        """
        from django.db import transaction

        async with transaction.atomic():
            locked = await (
                self.select_for_update()
                .filter(machine_id=machine_id)
                .afirst()
            )

            if locked is None:
                return None, False

            old_status = locked.status
            now = timezone.now()

            if new_status == "connected":
                locked.status = self.model.ConnectionStatus.CONNECTED
                locked.last_connected_at = now
                locked.consecutive_error_count = 0
                if ip_address:
                    locked.last_known_ip = ip_address
                if client_version:
                    locked.client_version = client_version

                await locked.asave(update_fields=[
                    "status", "last_connected_at", "consecutive_error_count",
                    "last_known_ip", "client_version", "updated_at",
                ])

            elif new_status == "disconnected":
                locked.status = self.model.ConnectionStatus.DISCONNECTED
                locked.last_disconnected_at = now

                await locked.asave(update_fields=[
                    "status", "last_disconnected_at", "updated_at",
                ])

            elif new_status == "error":
                locked.status = self.model.ConnectionStatus.ERROR
                locked.last_error_message = error_message or ""
                locked.last_error_at = now
                locked.consecutive_error_count += 1

                await locked.asave(update_fields=[
                    "status", "last_error_message", "last_error_at",
                    "consecutive_error_count", "updated_at",
                ])

            else:
                return locked, False

            updated = old_status != locked.status
            return locked, updated

    async def amark_connected_by_machine_id(
        self,
        machine_id: str,
        machine_name: str,
        ip_address: str = None,
        client_version: str = None,
    ) -> Tuple[Any, bool]:
        """
        Mark machine as connected, creating record if needed (ASYNC).

        Uses row-level locking to prevent race conditions.

        Returns:
            Tuple of (connection_state, created)
        """
        from django.db import transaction

        async with transaction.atomic():
            locked = await (
                self.select_for_update()
                .filter(machine_id=machine_id)
                .afirst()
            )

            if locked is not None:
                locked.machine_name = machine_name
                locked.status = self.model.ConnectionStatus.CONNECTED
                locked.last_connected_at = timezone.now()
                locked.consecutive_error_count = 0
                if ip_address:
                    locked.last_known_ip = ip_address
                if client_version:
                    locked.client_version = client_version

                await locked.asave(update_fields=[
                    "machine_name", "status", "last_connected_at",
                    "consecutive_error_count", "last_known_ip",
                    "client_version", "updated_at",
                ])
                return locked, False

        # Record doesn't exist, create new one
        try:
            state = await self.acreate(
                machine_id=machine_id,
                machine_name=machine_name,
                status=self.model.ConnectionStatus.CONNECTED,
                last_connected_at=timezone.now(),
                last_known_ip=ip_address,
                client_version=client_version or "",
            )
            return state, True
        except Exception:
            # Race condition - another process created it, try update again
            return await self.amark_connected_by_machine_id(
                machine_id=machine_id,
                machine_name=machine_name,
                ip_address=ip_address,
                client_version=client_version,
            )

    async def amark_disconnected_by_machine_id(self, machine_id: str) -> Optional[Any]:
        """Mark machine as disconnected by machine_id (ASYNC)."""
        state, _ = await self.aupdate_status_safe(
            machine_id=machine_id,
            new_status="disconnected",
        )
        return state

    async def amark_error_by_machine_id(
        self,
        machine_id: str,
        error_message: str,
    ) -> Optional[Any]:
        """Mark machine as having an error by machine_id (ASYNC)."""
        state, _ = await self.aupdate_status_safe(
            machine_id=machine_id,
            new_status="error",
            error_message=error_message,
        )
        return state

    # =========================================================================
    # Dashboard statistics
    # =========================================================================

    def get_summary_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for dashboard."""
        qs = self.get_queryset()
        recent_qs = qs.recent(hours=hours)

        total = qs.count()
        connected = qs.connected().count()
        disconnected = qs.disconnected().count()
        errors = qs.with_errors().count()

        connectivity_pct = (connected / total * 100) if total > 0 else 0.0

        recent_errors = recent_qs.filter(
            consecutive_error_count__gt=0
        ).count()

        return {
            "total_machines": total,
            "connected": connected,
            "disconnected": disconnected,
            "errors": errors,
            "connectivity_percentage": round(connectivity_pct, 2),
            "recent_errors": recent_errors,
            "period_hours": hours,
        }

    def get_uptime_stats(self, machine_id: str, days: int = 7) -> Dict[str, Any]:
        """Calculate uptime statistics for a machine."""
        from ..connection_state.event import GrpcAgentConnectionEventManager

        threshold = timezone.now() - timedelta(days=days)
        total_seconds = days * 24 * 60 * 60

        try:
            state = self.get(machine_id=machine_id)
        except self.model.DoesNotExist:
            return {
                "total_seconds": total_seconds,
                "uptime_seconds": 0,
                "downtime_seconds": total_seconds,
                "uptime_percentage": 0.0,
                "period_days": days,
            }

        # Import here to avoid circular import
        from ...models.connection_state import GrpcAgentConnectionEvent

        events = GrpcAgentConnectionEvent.objects.filter(
            connection_state=state,
            timestamp__gte=threshold,
        ).order_by("timestamp")

        uptime_seconds = 0
        last_connect_time = None

        for event in events:
            if event.event_type == "connected":
                last_connect_time = event.timestamp
            elif event.event_type == "disconnected" and last_connect_time:
                uptime_seconds += (event.timestamp - last_connect_time).total_seconds()
                last_connect_time = None

        if last_connect_time and state.status == "connected":
            uptime_seconds += (timezone.now() - last_connect_time).total_seconds()

        downtime_seconds = total_seconds - uptime_seconds
        uptime_pct = (uptime_seconds / total_seconds * 100) if total_seconds > 0 else 0.0

        return {
            "total_seconds": total_seconds,
            "uptime_seconds": int(uptime_seconds),
            "downtime_seconds": int(downtime_seconds),
            "uptime_percentage": round(uptime_pct, 2),
            "period_days": days,
        }
