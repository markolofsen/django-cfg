"""
Manager for GRPCServerStatus model.

Provides convenient methods for server lifecycle management.
"""

import os
import socket
from typing import Optional

from django.db import models
from django.utils import timezone


class GRPCServerStatusManager(models.Manager):
    """
    Manager for GRPCServerStatus model.

    Provides methods for:
    - Starting/stopping server tracking
    - Getting current server status
    - Cleaning up stale records
    """

    def start_server(
        self,
        host: str,
        port: int,
        pid: int = None,
    ):
        """
        Start tracking a new server instance (SYNC).

        Args:
            host: Server host address
            port: Server port
            pid: Process ID (defaults to current process)

        Returns:
            GRPCServerStatus instance

        Example:
            >>> status = GRPCServerStatus.objects.start_server(
            ...     host="[::]",
            ...     port=50051,
            ...     pid=12345
            ... )
            >>> status.is_running
            True
        """
        if pid is None:
            pid = os.getpid()

        hostname = socket.gethostname()
        address = f"{host}:{port}"
        instance_id = f"{hostname}:{port}:{pid}"

        # Mark any existing server at this address as stopped
        self.stop_servers_at_address(address)

        # Create or update server status (handles restart with same instance_id)
        status, created = self.update_or_create(
            instance_id=instance_id,
            defaults={
                "host": host,
                "port": port,
                "address": address,
                "pid": pid,
                "hostname": hostname,
                "status": self.model.StatusChoices.STARTING,
                "started_at": timezone.now(),
                "last_heartbeat": timezone.now(),
            },
        )

        return status

    async def astart_server(
        self,
        host: str,
        port: int,
        pid: int = None,
    ):
        """
        Start tracking a new server instance (ASYNC - Django 5.2).

        Args:
            host: Server host address
            port: Server port
            pid: Process ID (defaults to current process)

        Returns:
            GRPCServerStatus instance

        Example:
            >>> status = await GRPCServerStatus.objects.astart_server(
            ...     host="[::]",
            ...     port=50051,
            ...     pid=12345
            ... )
            >>> status.is_running
            True
        """
        if pid is None:
            pid = os.getpid()

        hostname = socket.gethostname()
        address = f"{host}:{port}"
        instance_id = f"{hostname}:{port}:{pid}"

        # Mark any existing server at this address as stopped (async)
        await self.astop_servers_at_address(address)

        # Create or update server status (handles restart with same instance_id)
        status, created = await self.aupdate_or_create(
            instance_id=instance_id,
            defaults={
                "host": host,
                "port": port,
                "address": address,
                "pid": pid,
                "hostname": hostname,
                "status": self.model.StatusChoices.STARTING,
                "started_at": timezone.now(),
                "last_heartbeat": timezone.now(),
            },
        )

        return status

    def get_current_server(self, address: str = None) -> Optional["GRPCServerStatus"]:
        """
        Get the currently running server (SYNC).

        Args:
            address: Optional address filter (host:port)

        Returns:
            GRPCServerStatus instance or None

        Example:
            >>> server = GRPCServerStatus.objects.get_current_server()
            >>> if server and server.is_running:
            ...     print(f"Server running for {server.uptime_display}")
        """
        queryset = self.filter(
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ]
        )

        if address:
            queryset = queryset.filter(address=address)

        # Get most recent
        server = queryset.order_by("-started_at").first()

        # Verify it's actually running
        if server and server.is_running:
            return server

        return None

    async def aget_current_server(self, address: str = None) -> Optional["GRPCServerStatus"]:
        """
        Get the currently running server (ASYNC - Django 5.2).

        Args:
            address: Optional address filter (host:port)

        Returns:
            GRPCServerStatus instance or None

        Example:
            >>> server = await GRPCServerStatus.objects.aget_current_server()
            >>> if server and server.is_running:
            ...     print(f"Server running for {server.uptime_display}")
        """
        queryset = self.filter(
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ]
        )

        if address:
            queryset = queryset.filter(address=address)

        # Get most recent (Django 5.2: afirst)
        server = await queryset.order_by("-started_at").afirst()

        # Verify it's actually running
        if server and server.is_running:
            return server

        return None

    def get_running_servers(self):
        """
        Get all currently running servers.

        Returns:
            QuerySet of running servers

        Example:
            >>> servers = GRPCServerStatus.objects.get_running_servers()
            >>> for server in servers:
            ...     print(f"{server.address}: {server.uptime_display}")
        """
        running_servers = []

        # Get servers marked as running
        candidates = self.filter(
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ]
        ).order_by("-started_at")

        # Verify each one is actually running
        for server in candidates:
            if server.is_running:
                running_servers.append(server.id)

        return self.filter(id__in=running_servers)

    def stop_server(self, pid: int = None, address: str = None):
        """
        Stop tracking a server instance.

        Args:
            pid: Process ID to stop
            address: Address to stop (alternative to pid)

        Example:
            >>> GRPCServerStatus.objects.stop_server(pid=12345)
        """
        if pid:
            servers = self.filter(pid=pid)
        elif address:
            servers = self.filter(address=address)
        else:
            # Stop current process
            pid = os.getpid()
            servers = self.filter(pid=pid)

        servers = servers.filter(
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ]
        )

        for server in servers:
            server.mark_stopped()

    def stop_servers_at_address(self, address: str):
        """
        Stop all servers at a specific address (SYNC).

        Args:
            address: Server address (host:port)

        Example:
            >>> GRPCServerStatus.objects.stop_servers_at_address("[::]:50051")
        """
        servers = self.filter(
            address=address,
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ],
        )

        for server in servers:
            server.mark_stopped("Replaced by new server instance")

    async def astop_servers_at_address(self, address: str):
        """
        Stop all servers at a specific address (ASYNC - Django 5.2).

        Args:
            address: Server address (host:port)

        Example:
            >>> await GRPCServerStatus.objects.astop_servers_at_address("[::]:50051")
        """
        servers = []
        async for server in self.filter(
            address=address,
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ],
        ):
            servers.append(server)

        for server in servers:
            await server.amark_stopped("Replaced by new server instance")

    def cleanup_stale_servers(self, hours: int = 24):
        """
        Mark stale servers as stopped.

        A server is considered stale if:
        - Status is STARTING or RUNNING
        - Last heartbeat is older than threshold
        - Process is not alive

        Args:
            hours: Hours without heartbeat to consider stale

        Returns:
            Number of servers cleaned up

        Example:
            >>> count = GRPCServerStatus.objects.cleanup_stale_servers()
            >>> print(f"Cleaned up {count} stale servers")
        """
        from django.utils import timezone
        from datetime import timedelta

        threshold = timezone.now() - timedelta(hours=hours)

        stale_servers = self.filter(
            status__in=[
                self.model.StatusChoices.STARTING,
                self.model.StatusChoices.RUNNING,
            ],
            last_heartbeat__lt=threshold,
        )

        count = 0
        for server in stale_servers:
            if not server.is_running:
                server.mark_stopped("Stale server (no heartbeat)")
                count += 1

        return count

    def get_server_by_pid(self, pid: int) -> Optional["GRPCServerStatus"]:
        """
        Get server by process ID.

        Args:
            pid: Process ID

        Returns:
            GRPCServerStatus instance or None
        """
        return (
            self.filter(pid=pid)
            .order_by("-started_at")
            .first()
        )

    def get_statistics(self):
        """
        Get statistics about server instances.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = GRPCServerStatus.objects.get_statistics()
            >>> print(f"Total servers: {stats['total_servers']}")
            >>> print(f"Currently running: {stats['running_servers']}")
        """
        running_servers = self.get_running_servers()

        return {
            "total_servers": self.count(),
            "running_servers": running_servers.count(),
            "stopped_servers": self.filter(
                status=self.model.StatusChoices.STOPPED
            ).count(),
            "error_servers": self.filter(
                status=self.model.StatusChoices.ERROR
            ).count(),
            "running_list": [
                {
                    "address": server.address,
                    "pid": server.pid,
                    "uptime_seconds": server.uptime_seconds,
                    "started_at": server.started_at.isoformat(),
                }
                for server in running_servers
            ],
        }


__all__ = ["GRPCServerStatusManager"]
