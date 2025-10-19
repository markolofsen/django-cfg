"""
Ngrok display manager for Django CFG.
"""

from .base import MAIN_PANEL_WIDTH, BaseDisplayManager


class NgrokDisplayManager(BaseDisplayManager):
    """Manager for displaying ngrok tunnel information."""

    def display_tunnel_info(self, tunnel_url: str):
        """Display active ngrok tunnel information."""
        try:
            if not self._is_ngrok_configured():
                return

            ngrok_service = self._get_ngrok_service()
            if not ngrok_service:
                return

            # Create ngrok info table
            ngrok_table = self.create_table()
            ngrok_table.add_column("Key", style="cyan", no_wrap=True)
            ngrok_table.add_column("Value", style="bright_white")

            # Add tunnel information
            ngrok_table.add_row("🌐 Tunnel URL:", tunnel_url)

            # Add webhook URL example
            webhook_url = ngrok_service.get_webhook_url()
            ngrok_table.add_row("🔗 Webhook URL:", webhook_url)

            # Add API URL
            api_url = ngrok_service.get_api_url()
            ngrok_table.add_row("🚀 API URL:", api_url)

            # Add environment variables info
            ngrok_table.add_row("📝 Env Variables:", "NGROK_URL, DJANGO_NGROK_URL set")

            # Add domain info if configured
            if self.config.ngrok.tunnel.domain:
                ngrok_table.add_row("🏷️  Custom Domain:", self.config.ngrok.tunnel.domain)

            # Add auth info
            if self.config.ngrok.auth.get_authtoken():
                ngrok_table.add_row("🔐 Auth Token:", "✅ Configured")
            else:
                ngrok_table.add_row("🔐 Auth Token:", "❌ Not configured (limited features)")

            # Create panel with ngrok info
            ngrok_panel = self.create_panel(
                ngrok_table,
                title="🚇 [bold green]Ngrok Tunnel Active[/bold green]",
                border_style="green",
                width=MAIN_PANEL_WIDTH
            )

            # Print the panel (not centered to respect width)
            self.print_spacing()
            self.console.print(ngrok_panel)
            self.print_spacing()

        except Exception:
            # Silently fail - ngrok info is not critical
            pass

    def display_config_status(self):
        """Display ngrok configuration status when tunnel is not active."""
        try:
            if not self._is_ngrok_configured():
                return

            ngrok_service = self._get_ngrok_service()
            if not ngrok_service:
                return

            # Create ngrok config status table
            status_table = self.create_table()
            status_table.add_column("Key", style="cyan", no_wrap=True)
            status_table.add_column("Value", style="bright_white")

            # Add configuration status
            status_table.add_row("🔧 Configuration:", "✅ Enabled")

            # Add auth status
            if self.config.ngrok.auth.get_authtoken():
                status_table.add_row("🔐 Auth Token:", "✅ Configured")
            else:
                status_table.add_row("🔐 Auth Token:", "❌ Not configured")

            # Add domain info if configured
            if self.config.ngrok.tunnel.domain:
                status_table.add_row("🏷️  Custom Domain:", self.config.ngrok.tunnel.domain)

            # Add auto-start status
            if self.config.ngrok.auto_start:
                status_table.add_row("🚀 Auto Start:", "✅ Enabled")
            else:
                status_table.add_row("🚀 Auto Start:", "❌ Disabled")

            # Add usage hint
            status_table.add_row("💡 Usage:", "Run 'pnpm manage.py runserver_ngrok' to start tunnel")

            # Create panel with ngrok config status - full width
            ngrok_panel = self.create_full_width_panel(
                status_table,
                title="🚇 [bold yellow]Ngrok Ready (Not Active)[/bold yellow]",
                border_style="yellow"
            )

            # Print the panel (not centered to respect width)
            self.print_spacing()
            self.console.print(ngrok_panel)
            self.print_spacing()

        except Exception:
            # Silently fail - ngrok config status is not critical
            pass

    def display_if_active(self):
        """Display ngrok information if configured and check if active."""
        if not self._is_ngrok_configured():
            return

        ngrok_service = self._get_ngrok_service()
        if not ngrok_service:
            return

        # Check if tunnel is active or available from environment
        tunnel_url = ngrok_service.get_tunnel_url()
        env_url = ngrok_service.get_tunnel_url_from_env()

        # IMPORTANT: During Django startup, ngrok tunnel may not be active yet
        # Only show active tunnel info if we actually have a tunnel URL
        # Otherwise, show config status (ready but not active)
        active_url = None

        if tunnel_url:
            # Active tunnel found from manager
            active_url = tunnel_url
        elif env_url:
            # Environment URL found (tunnel was started in this process)
            active_url = env_url

        if active_url:
            self.display_tunnel_info(active_url)
        else:
            self.display_config_status()

    def _is_ngrok_configured(self) -> bool:
        """Check if ngrok is configured."""
        return (self.config and
                hasattr(self.config, 'ngrok') and
                self.config.ngrok and
                self.config.ngrok.enabled)

    def _get_ngrok_service(self):
        """Get ngrok service instance."""
        try:
            from django_cfg.modules.django_ngrok import get_ngrok_service
            return get_ngrok_service()
        except Exception:
            return None
