"""
gRPC Server Display Manager.

Displays startup information specific to gRPC server.
"""

from rich.table import Table
from rich.text import Text

from .base import BaseDisplayManager


class GRPCDisplayManager(BaseDisplayManager):
    """Manager for displaying gRPC server startup information."""

    def display_grpc_startup(
        self,
        host: str,
        port: int,
        max_workers: int,
        enable_reflection: bool,
        enable_health_check: bool,
        registered_services: int,
        service_names: list = None,
    ):
        """
        Display gRPC server startup information.

        Args:
            host: Server host
            port: Server port
            max_workers: Maximum worker threads
            enable_reflection: Whether reflection is enabled
            enable_health_check: Whether health check is enabled
            registered_services: Number of registered services
            service_names: List of registered service names (optional)
        """
        # Display beautiful ASCII art banner for gRPC
        self.print_banner(style="default", color="magenta")
        self.print_spacing()

        # Display header with gRPC indicator
        header_text = self.create_header_text(show_update_check=True)
        # Add gRPC server indicator
        header_text.append(" • ", style="dim")
        header_text.append("⚡ gRPC Server", style="magenta bold")

        # Add startup time if available
        startup_time = self._get_grpc_startup_time()
        if startup_time:
            header_text.append(" • ", style="dim")
            header_text.append(f"⚡ {startup_time}", style="green")

        self.console.print(header_text)
        self.print_spacing()

        # Create server info table
        server_table = self.create_table()
        server_table.add_column("Setting", style="cyan", width=25)
        server_table.add_column("Value", style="white")

        # Server connection info
        address = f"{host}:{port}"
        server_table.add_row("⚡ gRPC Server", f"[bold green]{address}[/bold green]")
        server_table.add_row("👷 Max Workers", str(max_workers))

        # Features
        reflection_status = "✅ Enabled" if enable_reflection else "❌ Disabled"
        health_status = "✅ Enabled" if enable_health_check else "❌ Disabled"
        server_table.add_row("🔍 Reflection", reflection_status)
        server_table.add_row("❤️ Health Check", health_status)

        # Services
        services_text = (
            f"[bold green]{registered_services}[/bold green]"
            if registered_services > 0
            else "[yellow]0 (no services registered)[/yellow]"
        )
        server_table.add_row("📦 Services", services_text)

        # Add startup time
        startup_time = self._get_grpc_startup_time()
        if startup_time:
            server_table.add_row("⚡ Startup Time", f"[green]{startup_time}[/green]")

        # Create server panel
        server_panel = self.create_panel(
            server_table,
            title="⚡ gRPC Server Configuration",
            border_style="magenta",
        )
        self.console.print(server_panel)

        # Display registered services if available
        if service_names and len(service_names) > 0:
            self.print_spacing()
            self._display_services_list(service_names)

        self.print_spacing()

    def _display_services_list(self, service_names: list):
        """
        Display list of registered services.

        Args:
            service_names: List of service names
        """
        services_table = self.create_table()
        services_table.add_column("Service Name", style="cyan")
        services_table.add_column("Status", style="green")

        for service_name in service_names:
            services_table.add_row(
                f"📡 {service_name}",
                "✅ Registered"
            )

        services_panel = self.create_panel(
            services_table,
            title="📡 Registered Services",
            border_style="blue",
        )
        self.console.print(services_panel)

    def display_grpc_minimal(
        self,
        host: str,
        port: int,
        registered_services: int,
    ):
        """
        Display minimal gRPC server startup info.

        Args:
            host: Server host
            port: Server port
            registered_services: Number of registered services
        """
        # Display header with gRPC indicator
        header_text = self.create_header_text(show_update_check=True)
        # Add gRPC server indicator
        header_text.append(" • ", style="dim")
        header_text.append("⚡ gRPC Server", style="magenta bold")

        # Add server address and services count
        address = f"{host}:{port}"
        header_text.append(" • ", style="dim")
        header_text.append(f"⚡ {address}", style="magenta bold")
        header_text.append(" • ", style="dim")

        if registered_services > 0:
            header_text.append(f"📦 {registered_services} service(s)", style="green")
        else:
            header_text.append("📦 no services", style="yellow")

        self.console.print(header_text)

    def _get_grpc_startup_time(self) -> str:
        """
        Get formatted gRPC startup time from timer.

        Returns:
            Formatted startup time string or None
        """
        try:
            from ..timing import get_grpc_startup_time
            return get_grpc_startup_time()
        except ImportError:
            return None


__all__ = ["GRPCDisplayManager"]
